#!/usr/bin/env python3
import pandas as pd
from pathlib import Path

csv_dir = Path(__file__).parent / 'monitor_outputs_60min'
csv_files = sorted(csv_dir.glob('monitor_summary_*.csv'))
if not csv_files:
    print('No monitor_summary CSV found')
    raise SystemExit(1)
path = csv_files[-1]

df = pd.read_csv(path, parse_dates=['snapshot_ts','eta','data_timestamp'])
# normalize timezone awareness if needed
if df['snapshot_ts'].dt.tz is None:
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts']).dt.tz_localize('UTC')
if df['eta'].dt.tz is None:
    df['eta'] = pd.to_datetime(df['eta']).dt.tz_localize('Asia/Hong_Kong')

summary = {}
summary['csv_file'] = str(path.name)
summary['total_rows'] = len(df)
summary['unique_snapshots'] = df['snapshot_ts'].nunique()
summary['first_snapshot'] = df['snapshot_ts'].min()
summary['last_snapshot'] = df['snapshot_ts'].max()
summary['rows_per_stop'] = df['queried_stop_id'].value_counts().to_dict()
summary['distinct_routes_per_stop'] = df.groupby('queried_stop_id')['route'].nunique().to_dict()

# compute wait seconds = (eta - snapshot_ts).total_seconds()
df['wait_s'] = (df['eta'].dt.tz_convert('Asia/Hong_Kong') - df['snapshot_ts'].dt.tz_convert('Asia/Hong_Kong')).dt.total_seconds()
agg_df = df.groupby('queried_stop_id')['wait_s'].agg(['count','mean','median','min','max'])
summary['wait_stats_per_stop'] = {}
for stop_id, row in agg_df.iterrows():
    summary['wait_stats_per_stop'][stop_id] = {
        'count': int(row['count']),
        'mean_s': float(row['mean']) if not pd.isna(row['mean']) else None,
        'median_s': float(row['median']) if not pd.isna(row['median']) else None,
        'min_s': float(row['min']) if not pd.isna(row['min']) else None,
        'max_s': float(row['max']) if not pd.isna(row['max']) else None,
    }

# print a readable report
print('Monitor summary file:', summary['csv_file'])
print('Total rows:', summary['total_rows'])
print('Snapshots:', summary['unique_snapshots'], 'from', summary['first_snapshot'], 'to', summary['last_snapshot'])
print('\nRows per stop:')
for s,c in summary['rows_per_stop'].items():
    print('  ', s, c)
print('\nDistinct routes per stop:')
for s,r in summary['distinct_routes_per_stop'].items():
    print('  ', s, r)
print('\nWait time (seconds) stats per stop:')
for s,stats in summary['wait_stats_per_stop'].items():
    print(f"  {s}: count={stats['count']}, mean={stats['mean_s']:.1f}s, median={stats['median_s']:.1f}s, min={stats['min_s']:.1f}s, max={stats['max_s']:.1f}s")

# exit with success
