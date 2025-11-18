#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).parent
CSV = BASE / 'monitor_summary_20251104_003106.csv'
OUTDIR = BASE / 'analysis'
OUTDIR.mkdir(exist_ok=True)

if not CSV.exists():
    raise SystemExit('CSV not found: ' + str(CSV))

print('Loading', CSV)
df = pd.read_csv(CSV, parse_dates=['snapshot_ts','eta','data_timestamp'])
# ensure tz-aware
if df['snapshot_ts'].dt.tz is None:
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts']).dt.tz_localize('UTC')
# convert to local timezone
df['snapshot_local'] = df['snapshot_ts'].dt.tz_convert('Asia/Hong_Kong')
# minute bucket
df['snapshot_min'] = df['snapshot_local'].dt.floor('min')

# We'll create 5-minute aggregated counts and plot as line with markers to reduce clutter
resample = '5T'  # 5 minutes

for stop, g in df.groupby('queried_stop_id'):
    counts = g.set_index('snapshot_local').resample(resample).size()
    # fill missing intervals with 0
    counts = counts.asfreq(resample, fill_value=0)

    plt.figure(figsize=(12,4))
    counts.plot(marker='o', linewidth=1)
    plt.title(f'ETA rows per {resample} - {stop}')
    plt.ylabel('rows')
    plt.xlabel('time')
    # improve x ticks: show every Nth tick depending on number of points
    n = len(counts)
    if n > 12:
        step = max(1, n // 12)
        plt.xticks(counts.index[::step], rotation=45)
    else:
        plt.xticks(rotation=45)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    out = OUTDIR / f'counts_per_5min_{stop}_improved.png'
    plt.savefig(out, dpi=150)
    plt.close()
    print('Wrote', out)

# Also produce 10-minute aggregated version for comparison
resample2 = '10T'
for stop, g in df.groupby('queried_stop_id'):
    counts = g.set_index('snapshot_local').resample(resample2).size()
    counts = counts.asfreq(resample2, fill_value=0)
    plt.figure(figsize=(12,3.5))
    counts.plot(kind='bar', width=0.8)
    plt.title(f'ETA rows per {resample2} - {stop} (bar)')
    plt.ylabel('rows')
    plt.xlabel('time')
    n = len(counts)
    if n > 12:
        step = max(1, n // 12)
        plt.xticks(range(0,n,step), [ts.strftime('%H:%M') for ts in counts.index[::step]], rotation=45)
    else:
        plt.xticks(rotation=45)
    plt.tight_layout()
    out2 = OUTDIR / f'counts_per_10min_{stop}_improved.png'
    plt.savefig(out2, dpi=150)
    plt.close()
    print('Wrote', out2)

print('Done')
