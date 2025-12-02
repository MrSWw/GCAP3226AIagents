#!/usr/bin/env python3
"""
Analyze all CSV files to extract monitoring dates and create a summary report.
"""

import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re

def parse_timestamp(ts_str):
    """Parse various timestamp formats."""
    if not ts_str:
        return None
    
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    
    return None

def extract_date_from_filename(filename):
    """Extract date from filename patterns like *_20251124_*.csv"""
    match = re.search(r'(\d{8})_\d{6}', filename)
    if match:
        date_str = match.group(1)
        try:
            return datetime.strptime(date_str, "%Y%m%d").date()
        except ValueError:
            pass
    return None

def analyze_csv_file(csv_path):
    """Analyze a single CSV file for monitoring dates."""
    info = {
        'path': str(csv_path),
        'filename': csv_path.name,
        'dates': set(),
        'min_date': None,
        'max_date': None,
        'row_count': 0,
        'has_eta_data': False,
        'columns': []
    }
    
    # Try to extract date from filename first
    filename_date = extract_date_from_filename(csv_path.name)
    if filename_date:
        info['dates'].add(filename_date)
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            info['columns'] = reader.fieldnames or []
            
            # Look for timestamp columns
            timestamp_cols = [col for col in info['columns'] 
                            if any(keyword in col.lower() 
                                 for keyword in ['timestamp', 'time', 'date', 'eta', 'snapshot'])]
            
            # Check if this looks like ETA monitoring data
            info['has_eta_data'] = any(col.lower() in ['eta', 'route', 'stop_id', 'queried_stop_id'] 
                                      for col in info['columns'])
            
            for row in reader:
                info['row_count'] += 1
                
                # Try to extract dates from timestamp columns
                for col in timestamp_cols:
                    if col in row and row[col]:
                        dt = parse_timestamp(row[col])
                        if dt:
                            date = dt.date()
                            info['dates'].add(date)
                            
                            if not info['min_date'] or dt < info['min_date']:
                                info['min_date'] = dt
                            if not info['max_date'] or dt > info['max_date']:
                                info['max_date'] = dt
    
    except Exception as e:
        info['error'] = str(e)
    
    return info

def main():
    base_dir = Path('/workspaces/GCAP3226AIagents')
    csv_collection_dir = base_dir / 'csv_collection'
    
    print("Analyzing all CSV files in the workspace...")
    print("=" * 80)
    
    # Find all CSV files
    all_csvs = list(base_dir.glob('**/*.csv'))
    # Exclude the csv_collection folder itself
    all_csvs = [f for f in all_csvs if not str(f).startswith(str(csv_collection_dir))]
    
    print(f"\nFound {len(all_csvs)} CSV files\n")
    
    # Analyze each CSV
    results = []
    eta_monitoring_files = []
    
    for csv_path in sorted(all_csvs):
        print(f"Analyzing: {csv_path.relative_to(base_dir)}")
        info = analyze_csv_file(csv_path)
        results.append(info)
        
        if info['has_eta_data'] and info['dates']:
            eta_monitoring_files.append(info)
    
    # Create summary report
    summary_path = csv_collection_dir / 'MONITORING_DATES_SUMMARY.md'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# CSV Monitoring Dates Summary\n\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total CSV Files**: {len(all_csvs)}\n")
        f.write(f"**ETA Monitoring Files**: {len(eta_monitoring_files)}\n\n")
        
        f.write("---\n\n")
        f.write("## ETA Monitoring Files by Date\n\n")
        
        # Group by date
        files_by_date = defaultdict(list)
        for info in eta_monitoring_files:
            for date in info['dates']:
                files_by_date[date].append(info)
        
        for date in sorted(files_by_date.keys()):
            f.write(f"\n### {date.strftime('%Y-%m-%d')} ({date.strftime('%A')})\n\n")
            f.write(f"**Files**: {len(files_by_date[date])}\n\n")
            
            for info in sorted(files_by_date[date], key=lambda x: x['path']):
                rel_path = Path(info['path']).relative_to(base_dir)
                f.write(f"- `{rel_path}`\n")
                f.write(f"  - Rows: {info['row_count']:,}\n")
                if info['min_date'] and info['max_date']:
                    f.write(f"  - Time Range: {info['min_date'].strftime('%H:%M:%S')} - {info['max_date'].strftime('%H:%M:%S')}\n")
                f.write("\n")
        
        f.write("\n---\n\n")
        f.write("## All Files Summary\n\n")
        f.write("| File | Rows | Dates | Time Range | Has ETA Data |\n")
        f.write("|------|------|-------|------------|-------------|\n")
        
        for info in sorted(results, key=lambda x: x['path']):
            rel_path = Path(info['path']).relative_to(base_dir)
            dates_str = ", ".join(sorted(d.strftime('%Y-%m-%d') for d in info['dates'])) if info['dates'] else "N/A"
            if len(dates_str) > 30:
                dates_str = dates_str[:27] + "..."
            
            time_range = "N/A"
            if info['min_date'] and info['max_date']:
                time_range = f"{info['min_date'].strftime('%m-%d %H:%M')} - {info['max_date'].strftime('%m-%d %H:%M')}"
            
            eta_marker = "✓" if info['has_eta_data'] else ""
            
            f.write(f"| `{rel_path}` | {info['row_count']:,} | {dates_str} | {time_range} | {eta_marker} |\n")
        
        f.write("\n---\n\n")
        f.write("## Date Coverage Summary\n\n")
        
        all_dates = set()
        for info in eta_monitoring_files:
            all_dates.update(info['dates'])
        
        if all_dates:
            sorted_dates = sorted(all_dates)
            f.write(f"**Earliest Date**: {sorted_dates[0].strftime('%Y-%m-%d (%A)')}\n\n")
            f.write(f"**Latest Date**: {sorted_dates[-1].strftime('%Y-%m-%d (%A)')}\n\n")
            f.write(f"**Total Unique Dates**: {len(sorted_dates)}\n\n")
            f.write(f"**Date Range**: {sorted_dates[0]} to {sorted_dates[-1]} ({(sorted_dates[-1] - sorted_dates[0]).days + 1} days)\n\n")
            
            f.write("\n### All Monitoring Dates:\n\n")
            for date in sorted_dates:
                file_count = len(files_by_date[date])
                total_rows = sum(info['row_count'] for info in files_by_date[date])
                f.write(f"- **{date.strftime('%Y-%m-%d (%A)')}**: {file_count} files, {total_rows:,} total rows\n")
    
    # Create CSV index
    index_path = csv_collection_dir / 'csv_files_index.csv'
    with open(index_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Path', 'Filename', 'Rows', 'Dates', 'Min_DateTime', 'Max_DateTime', 'Has_ETA_Data', 'Columns'])
        
        for info in sorted(results, key=lambda x: x['path']):
            rel_path = Path(info['path']).relative_to(base_dir)
            dates_str = "; ".join(sorted(d.strftime('%Y-%m-%d') for d in info['dates'])) if info['dates'] else ""
            min_dt = info['min_date'].isoformat() if info['min_date'] else ""
            max_dt = info['max_date'].isoformat() if info['max_date'] else ""
            cols_str = "; ".join(info['columns'][:10])  # First 10 columns
            if len(info['columns']) > 10:
                cols_str += f" ... ({len(info['columns'])} total)"
            
            writer.writerow([
                str(rel_path),
                info['filename'],
                info['row_count'],
                dates_str,
                min_dt,
                max_dt,
                'Yes' if info['has_eta_data'] else 'No',
                cols_str
            ])
    
    print(f"\n{'=' * 80}")
    print(f"✓ Analysis complete!")
    print(f"\nSummary report: {summary_path.relative_to(base_dir)}")
    print(f"CSV index: {index_path.relative_to(base_dir)}")
    print(f"\nETA monitoring files found: {len(eta_monitoring_files)}")
    if all_dates:
        print(f"Date range: {min(all_dates)} to {max(all_dates)}")
        print(f"Total unique monitoring dates: {len(all_dates)}")

if __name__ == '__main__':
    main()
