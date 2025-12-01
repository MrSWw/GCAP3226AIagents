#!/usr/bin/env python3
"""Aggregate collected CSV data into peak/off-peak summary and route allocation summary.

Usage:
  python aggregate_peak_offpeak.py --input-dir ./vibeCoding101/PartX_simulation --out-agg ./aggregated_by_date_peak_offpeak.csv --out-alloc ./route_allocation_summary.csv

Options:
  --peak-ranges  Comma-separated time ranges (HH:MM-HH:MM) to treat as peak. Default: 07:00-09:00,17:00-19:00
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, time


def parse_peak_ranges(s: str):
    ranges = []
    for piece in s.split(','):
        a,b = piece.split('-')
        t0 = datetime.strptime(a.strip(), '%H:%M').time()
        t1 = datetime.strptime(b.strip(), '%H:%M').time()
        ranges.append((t0, t1))
    return ranges


def is_peak(dt: datetime, ranges):
    t = dt.time()
    for a,b in ranges:
        if a <= b:
            if a <= t < b:
                return True
        else:
            # overnight range
            if t >= a or t < b:
                return True
    return False


def collect_csv_files(root: Path):
    return list(root.rglob('*.csv'))


def try_parse_datetime(col):
    try:
        return pd.to_datetime(col, utc=False, errors='coerce')
    except Exception:
        return pd.to_datetime(col, errors='coerce')


def aggregate(input_dir: Path, out_agg: Path, peak_ranges):
    files = collect_csv_files(input_dir)
    rows = []
    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        source = str(f.relative_to(input_dir))

        # find any datetime-like column (prefer 'eta' or 'datetime' or 'time')
        dt_cols = [c for c in df.columns if c.lower() in ('eta','datetime','time','timestamp')]
        if not dt_cols:
            # attempt to find any column with datetime-like values
            for c in df.columns:
                parsed = try_parse_datetime(df[c])
                if parsed.notna().any():
                    dt_cols = [c]
                    break
        if dt_cols:
            dtcol = dt_cols[0]
            dts = try_parse_datetime(df[dtcol])
            for i,dt in enumerate(dts):
                if pd.isna(dt):
                    continue
                tag = 'peak' if is_peak(dt.to_pydatetime(), peak_ranges) else 'off-peak'
                date = dt.date()
                time_s = dt.time()
                # collect row: keep original columns as JSON-friendly strings where necessary
                rec = {
                    'source_file': source,
                    'row_index': i,
                    'datetime': dt.isoformat(),
                    'date': date.isoformat(),
                    'time': time_s.strftime('%H:%M:%S'),
                    'peak_or_offpeak': tag,
                }
                # attach some commonly useful columns if present
                for col in ('queried_stop_id','stop_id','route','routes','avg_waiting_time','avg_queue_time'):
                    if col in df.columns:
                        val = df.at[i, col] if i < len(df) else np.nan
                        rec[col] = val
                rows.append(rec)
        else:
            # no datetime found; write a summary row with file-level stats
            rec = {
                'source_file': source,
                'row_index': -1,
                'datetime': None,
                'date': None,
                'time': None,
                'peak_or_offpeak': 'unknown',
                'note': 'no datetime-like column'
            }
            rows.append(rec)

    if rows:
        outdf = pd.DataFrame(rows)
        outdf.to_csv(out_agg, index=False)
        print('Wrote aggregated file:', out_agg)
    else:
        print('No rows found to aggregate')


def route_allocation_summary(input_dir: Path, out_alloc: Path):
    files = collect_csv_files(input_dir)
    rows = []
    for f in files:
        name = f.name
        if 'allocated' in name or 'alloc' in name or 'allocation' in name:
            try:
                df = pd.read_csv(f)
            except Exception:
                continue
            # expect columns: simulation, routes, avg_waiting_time, avg_queue_time
            for i, r in df.iterrows():
                rec = {
                    'source_file': str(f.relative_to(input_dir)),
                    'row_index': i,
                }
                for col in ('simulation','routes','avg_waiting_time','avg_queue_time','stop_id'):
                    if col in df.columns:
                        rec[col] = r.get(col)
                rows.append(rec)

    if rows:
        alloc_df = pd.DataFrame(rows)
        # try to normalize routes column (split by ; or | or ,)
        if 'routes' in alloc_df.columns:
            alloc_df['routes_list'] = alloc_df['routes'].astype(str).str.replace('[\[\]\"\']','', regex=True).str.split('[;,|]')
        alloc_df.to_csv(out_alloc, index=False)
        print('Wrote route allocation file:', out_alloc)
    else:
        print('No allocation files found')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-dir', type=str, default='vibeCoding101/PartX_simulation')
    p.add_argument('--out-agg', type=str, default='aggregated_by_date_peak_offpeak.csv')
    p.add_argument('--out-alloc', type=str, default='route_allocation_summary.csv')
    p.add_argument('--peak-ranges', type=str, default='07:00-09:00,17:00-19:00')
    args = p.parse_args()

    input_dir = Path(args.input_dir)
    out_agg = Path(args.out_agg)
    out_alloc = Path(args.out_alloc)
    peak_ranges = parse_peak_ranges(args.peak_ranges)

    if not input_dir.exists():
        print('Input dir not found:', input_dir)
        sys.exit(2)

    aggregate(input_dir, out_agg, peak_ranges)
    route_allocation_summary(input_dir, out_alloc)


if __name__ == '__main__':
    main()
