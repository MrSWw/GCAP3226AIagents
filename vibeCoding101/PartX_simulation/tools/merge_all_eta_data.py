#!/usr/bin/env python3
"""
Merge all historical ETA data from multiple sources into a unified CSV for analysis.
"""
from pathlib import Path
import csv
import sys

def normalize_row(row, source_file):
    """Normalize different CSV formats to common schema"""
    # Target schema: snapshot_ts, queried_stop_id, route, direction, eta, eta_seq, data_timestamp
    normalized = {}
    
    # Handle different column name variations
    normalized['snapshot_ts'] = row.get('snapshot_ts', '')
    normalized['queried_stop_id'] = row.get('queried_stop_id') or row.get('stop_id', '')
    normalized['route'] = row.get('route', '')
    normalized['direction'] = row.get('direction') or row.get('dir', '')
    normalized['eta'] = row.get('eta', '')
    normalized['eta_seq'] = row.get('eta_seq', '')
    normalized['data_timestamp'] = row.get('data_timestamp', '')
    normalized['source_file'] = source_file
    
    # Only include if has minimum required fields
    if normalized['queried_stop_id'] and normalized['route'] and normalized['eta']:
        return normalized
    return None

def merge_csv_files(input_files, output_file):
    """Merge multiple CSV files with normalization"""
    all_rows = []
    seen = set()  # deduplicate by (snapshot_ts, stop_id, route, eta_seq, eta)
    
    for input_file in input_files:
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    normalized = normalize_row(row, str(input_file))
                    if normalized:
                        # Create dedup key
                        key = (
                            normalized['snapshot_ts'],
                            normalized['queried_stop_id'],
                            normalized['route'],
                            normalized['eta_seq'],
                            normalized['eta']
                        )
                        if key not in seen:
                            seen.add(key)
                            all_rows.append(normalized)
            print(f"✓ Processed: {input_file} ({len(all_rows)} total rows so far)")
        except Exception as e:
            print(f"✗ Error reading {input_file}: {e}", file=sys.stderr)
    
    # Sort by snapshot_ts
    all_rows.sort(key=lambda x: x['snapshot_ts'])
    
    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['snapshot_ts', 'queried_stop_id', 'route', 'direction', 'eta', 'eta_seq', 'data_timestamp', 'source_file']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n✓ Merged {len(all_rows)} unique rows into: {output_file}")
    print(f"  Deduplicated: {len(seen)} unique records")

def main():
    base = Path('/workspaces/GCAP3226AIagents')
    
    # Collect all relevant CSV files
    input_files = []
    
    # 1. Main Newdata monitoring
    newdata = base / 'Newdata'
    if (newdata / 'realtime_monitoring.csv').exists():
        input_files.append(newdata / 'realtime_monitoring.csv')
    
    # 2. presentation/simulation
    pres_sim = base / 'presentation' / 'simulation'
    for csv_file in pres_sim.glob('*.csv'):
        if 'stop' in csv_file.name or 'eta' in csv_file.name.lower():
            input_files.append(csv_file)
    
    # 3. vibeCoding101/PartX_simulation monitor outputs
    part_sim = base / 'vibeCoding101' / 'PartX_simulation'
    for monitor_dir in part_sim.glob('monitor_outputs_*'):
        for csv_file in monitor_dir.rglob('*.csv'):
            if 'monitor' in csv_file.name or 'summary' in csv_file.name:
                input_files.append(csv_file)
    
    # 4. vibeCoding101 root level monitoring CSVs
    for csv_file in part_sim.glob('*.csv'):
        if 'monitor' in csv_file.name or 'route_pair' in csv_file.name:
            input_files.append(csv_file)
    
    print(f"Found {len(input_files)} CSV files to merge:")
    for f in input_files:
        print(f"  - {f.relative_to(base)}")
    
    output_file = base / 'Newdata' / 'all_historical_eta_merged.csv'
    merge_csv_files(input_files, output_file)

if __name__ == '__main__':
    main()
