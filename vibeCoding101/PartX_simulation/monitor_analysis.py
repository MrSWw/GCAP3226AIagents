#!/usr/bin/env python3
"""產生監控資料的分析圖表

輸入：monitor_outputs_60min/monitor_summary_*.csv
輸出：monitor_outputs_60min/analysis/

會產生：
 - mean_wait_per_minute_{stop_id}.png
 - counts_per_minute_{stop_id}.png
 - wait_hist_by_eta_seq.png
 - combined_wait_trend.png
 - analysis_summary.json
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import json

BASE = Path(__file__).parent / 'monitor_outputs_60min'
ANALYSIS_DIR = BASE / 'analysis'
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# 找最新的 monitor_summary CSV
csvs = sorted(BASE.glob('monitor_summary_*.csv'))
if not csvs:
    raise SystemExit('No monitor_summary CSV found in ' + str(BASE))
csv_path = csvs[-1]
print('Using', csv_path.name)

df = pd.read_csv(csv_path, parse_dates=['snapshot_ts','eta','data_timestamp'])
# ensure tz-aware
if df['snapshot_ts'].dt.tz is None:
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts']).dt.tz_localize('UTC')
if df['eta'].dt.tz is None:
    df['eta'] = pd.to_datetime(df['eta']).dt.tz_localize('Asia/Hong_Kong')

# normalize both to Asia/Hong_Kong for wait calculations
df['snapshot_local'] = df['snapshot_ts'].dt.tz_convert('Asia/Hong_Kong')
df['eta_local'] = df['eta'].dt.tz_convert('Asia/Hong_Kong')

df['wait_s'] = (df['eta_local'] - df['snapshot_local']).dt.total_seconds()
# floor snapshot to minute for per-minute aggregation
df['snapshot_min'] = df['snapshot_local'].dt.floor('T')

summary = {}
# per-stop analyses
for stop_id, g in df.groupby('queried_stop_id'):
    out_prefix = ANALYSIS_DIR / f'{stop_id}'
    # mean wait per minute
    per_min = g.groupby('snapshot_min')['wait_s'].mean()
    counts_min = g.groupby('snapshot_min').size()

    plt.figure(figsize=(10,4))
    per_min.plot(title=f'Mean wait (s) per minute - {stop_id}')
    plt.ylabel('mean wait (s)')
    plt.xlabel('snapshot_min')
    plt.tight_layout()
    fig1 = ANALYSIS_DIR / f'mean_wait_per_minute_{stop_id}.png'
    plt.savefig(fig1)
    plt.close()

    plt.figure(figsize=(10,4))
    counts_min.plot(kind='bar', width=0.8)
    plt.title(f'ETA rows per minute - {stop_id}')
    plt.ylabel('rows')
    plt.xlabel('snapshot_min')
    plt.tight_layout()
    fig2 = ANALYSIS_DIR / f'counts_per_minute_{stop_id}.png'
    plt.savefig(fig2)
    plt.close()

    summary[stop_id] = {
        'rows': int(len(g)),
        'snapshots': int(g['snapshot_min'].nunique()),
        'mean_wait_s': float(g['wait_s'].mean()),
        'median_wait_s': float(g['wait_s'].median()),
        'min_wait_s': float(g['wait_s'].min()),
        'max_wait_s': float(g['wait_s'].max()),
        'mean_wait_per_min_csv': str(fig1.name),
        'counts_per_min_csv': str(fig2.name),
    }

# combined trend: mean wait per minute for each stop in one plot
plt.figure(figsize=(10,5))
for stop_id, g in df.groupby('queried_stop_id'):
    per_min = g.groupby('snapshot_min')['wait_s'].mean()
    per_min.plot(label=stop_id)
plt.legend()
plt.title('Mean wait per minute (by stop)')
plt.ylabel('mean wait (s)')
plt.xlabel('snapshot_min')
plt.tight_layout()
combined_fig = ANALYSIS_DIR / 'combined_wait_trend.png'
plt.savefig(combined_fig)
plt.close()
summary['combined_wait_trend'] = str(combined_fig.name)

# ETA-seq distribution (hist by seq)
plt.figure(figsize=(8,5))
for seq in sorted(df['eta_seq'].unique()):
    subset = df[df['eta_seq']==seq]
    plt.hist(subset['wait_s'].dropna(), bins=30, alpha=0.5, label=f'eta_seq={int(seq)}')
plt.legend()
plt.title('Wait time distribution by eta_seq')
plt.xlabel('wait seconds')
plt.ylabel('count')
plt.tight_layout()
seq_fig = ANALYSIS_DIR / 'wait_hist_by_eta_seq.png'
plt.savefig(seq_fig)
plt.close()
summary['wait_hist_by_eta_seq'] = str(seq_fig.name)

# save summary JSON
with open(ANALYSIS_DIR / 'analysis_summary.json','w') as f:
    json.dump(summary, f, indent=2, default=str)

print('Analysis outputs written to', ANALYSIS_DIR)
print('Files:', [p.name for p in sorted(ANALYSIS_DIR.iterdir())])
