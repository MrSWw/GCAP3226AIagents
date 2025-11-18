#!/usr/bin/env python3
"""分析 monitor_summary_20251104_003106.csv 並輸出圖表與 JSON 摘要
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import json

BASE = Path(__file__).parent
CSV = BASE / 'monitor_summary_20251104_003106.csv'
ANALYSIS = BASE / 'analysis'
ANALYSIS.mkdir(exist_ok=True)

if not CSV.exists():
    raise SystemExit(f'CSV not found: {CSV}')

print('Loading', CSV)
df = pd.read_csv(CSV, parse_dates=['snapshot_ts','eta','data_timestamp'])
# ensure tz-awareness
if df['snapshot_ts'].dt.tz is None:
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts']).dt.tz_localize('UTC')
if df['eta'].dt.tz is None:
    df['eta'] = pd.to_datetime(df['eta']).dt.tz_localize('Asia/Hong_Kong')

# convert to local timezone for computations
df['snapshot_local'] = df['snapshot_ts'].dt.tz_convert('Asia/Hong_Kong')
df['eta_local'] = df['eta'].dt.tz_convert('Asia/Hong_Kong')

# wait seconds
df['wait_s'] = (df['eta_local'] - df['snapshot_local']).dt.total_seconds()
# minute bucket
df['snapshot_min'] = df['snapshot_local'].dt.floor('min')

summary = {}
summary['csv'] = str(CSV.name)
summary['total_rows'] = int(len(df))
summary['time_span'] = {'start': str(df['snapshot_local'].min()), 'end': str(df['snapshot_local'].max())}

# per stop stats
per_stop = {}
for stop, g in df.groupby('queried_stop_id'):
    per_stop[stop] = {
        'rows': int(len(g)),
        'distinct_routes': int(g['route'].nunique()),
        'mean_wait_s': float(g['wait_s'].mean()),
        'median_wait_s': float(g['wait_s'].median()),
        'min_wait_s': float(g['wait_s'].min()),
        'max_wait_s': float(g['wait_s'].max()),
    }
    # per-minute mean
    per_min = g.groupby('snapshot_min')['wait_s'].mean()
    fig = ANALYSIS / f'mean_wait_per_min_{stop}.png'
    plt.figure(figsize=(10,3))
    per_min.plot(title=f'Mean wait (s) per minute - {stop}')
    plt.ylabel('mean wait (s)')
    plt.xlabel('minute')
    plt.tight_layout()
    plt.savefig(fig)
    plt.close()
    per_stop[stop]['mean_wait_per_min_plot'] = str(fig.name)
    # counts per minute
    counts = g.groupby('snapshot_min').size()
    fig2 = ANALYSIS / f'counts_per_min_{stop}.png'
    plt.figure(figsize=(10,3))
    counts.plot(kind='bar', width=0.8)
    plt.title(f'ETA rows per minute - {stop}')
    plt.ylabel('rows')
    plt.xlabel('minute')
    plt.tight_layout()
    plt.savefig(fig2)
    plt.close()
    per_stop[stop]['counts_per_min_plot'] = str(fig2.name)

summary['per_stop'] = per_stop

# combined trend
plt.figure(figsize=(10,4))
for stop, g in df.groupby('queried_stop_id'):
    per_min = g.groupby('snapshot_min')['wait_s'].mean()
    per_min.plot(label=stop)
plt.legend()
plt.title('Mean wait per minute (by stop)')
plt.ylabel('mean wait (s)')
plt.xlabel('minute')
plt.tight_layout()
combined_fig = ANALYSIS / 'combined_mean_wait.png'
plt.savefig(combined_fig)
plt.close()
summary['combined_plot'] = str(combined_fig.name)

# eta_seq distribution
seqs = sorted(df['eta_seq'].dropna().unique())
plt.figure(figsize=(8,5))
for seq in seqs:
    subset = df[df['eta_seq']==seq]
    plt.hist(subset['wait_s'].dropna(), bins=40, alpha=0.5, label=f'eta_seq={int(seq)}')
plt.legend()
plt.title('Wait time distribution by eta_seq')
plt.xlabel('wait seconds')
plt.ylabel('count')
plt.tight_layout()
seq_fig = ANALYSIS / 'wait_hist_by_eta_seq.png'
plt.savefig(seq_fig)
plt.close()
summary['eta_seq_hist'] = str(seq_fig.name)

# top outliers
outliers = df.sort_values('wait_s', ascending=False).head(10)[['snapshot_local','queried_stop_id','route','eta_seq','wait_s']]
summary['top_outliers'] = outliers.to_dict(orient='records')

# save summary
with open(ANALYSIS / 'analysis_summary.json','w') as f:
    json.dump(summary, f, indent=2, default=str)

print('Wrote analysis to', ANALYSIS)
print('Summary:', json.dumps(summary, indent=2))
