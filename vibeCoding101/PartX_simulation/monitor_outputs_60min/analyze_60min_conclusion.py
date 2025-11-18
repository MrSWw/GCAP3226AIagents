#!/usr/bin/env python3
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Paths
WORKDIR = Path(__file__).resolve().parent
CSV = WORKDIR / "monitor_summary_20251031_062043.csv"
ANALYSIS_DIR = WORKDIR / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)

print("Loading", CSV)
df = pd.read_csv(CSV)

# Normalize snapshot and eta column names and compute wait_s
# Many CSVs use 'snapshot_ts' and 'eta' (ISO strings). We'll parse them.
if 'snapshot_local' in df.columns:
    df['snapshot_local'] = pd.to_datetime(df['snapshot_local'], errors='coerce')
elif 'snapshot_ts' in df.columns:
    df['snapshot_local'] = pd.to_datetime(df['snapshot_ts'], errors='coerce')
else:
    # try common alternative column names
    for c in ['local_snapshot', 'polled_at', 'polled_local']:
        if c in df.columns:
            df['snapshot_local'] = pd.to_datetime(df[c], errors='coerce')
            break

# eta time column
if 'eta_time' in df.columns:
    df['eta_time'] = pd.to_datetime(df['eta_time'], errors='coerce')
elif 'eta' in df.columns:
    df['eta_time'] = pd.to_datetime(df['eta'], errors='coerce')

# compute wait_s if missing
if 'wait_s' not in df.columns:
    if 'eta_time' in df.columns and 'snapshot_local' in df.columns:
        df['wait_s'] = (df['eta_time'] - df['snapshot_local']).dt.total_seconds()
    else:
        raise SystemExit('CSV has no wait_s and cannot compute it (missing eta or snapshot columns)')

# Basic overall stats
total_rows = len(df)
start = None
end = None
if 'snapshot_local' in df.columns and df['snapshot_local'].notna().any():
    start = df['snapshot_local'].min()
    end = df['snapshot_local'].max()

# Per-stop aggregation
per_stop = {}
for stop_id, g in df.groupby('queried_stop_id'):
    routes = g['route'].dropna().unique().tolist() if 'route' in g.columns else []
    wait = g['wait_s'].dropna()
    per_stop[stop_id] = {
        'rows': int(len(g)),
        'distinct_routes': int(len(routes)),
        'mean_wait_s': float(wait.mean()) if len(wait) else None,
        'median_wait_s': float(wait.median()) if len(wait) else None,
        'min_wait_s': float(wait.min()) if len(wait) else None,
        'max_wait_s': float(wait.max()) if len(wait) else None,
        'mean_wait_per_min_plot': f'mean_wait_per_min_{stop_id}.png',
        'counts_per_min_plot': f'counts_per_min_{stop_id}.png'
    }

# top outliers (largest wait_s)
outliers = []
if 'wait_s' in df.columns:
    top = df.sort_values('wait_s', ascending=False).head(20)
    for _, r in top.iterrows():
        outliers.append({
            'snapshot_local': r['snapshot_local'].isoformat() if pd.notna(r.get('snapshot_local')) else None,
            'queried_stop_id': r.get('queried_stop_id'),
            'route': r.get('route'),
            'eta_seq': int(r['eta_seq']) if 'eta_seq' in r and not pd.isna(r['eta_seq']) else None,
            'wait_s': float(r['wait_s']) if not pd.isna(r['wait_s']) else None
        })

summary = {
    'csv': CSV.name,
    'total_rows': int(total_rows),
    'time_span': {
        'start': start.isoformat() if start is not None else None,
        'end': end.isoformat() if end is not None else None,
    },
    'per_stop': per_stop,
    'top_outliers': outliers
}

# Save summary
with open(ANALYSIS_DIR / 'analysis_summary.json', 'w', encoding='utf8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print('Wrote', ANALYSIS_DIR / 'analysis_summary.json')

# ========== Plots ==========
# 1) Wait distribution histogram
plt.figure(figsize=(8,4))
wait_all = df['wait_s'].dropna()
plt.hist(wait_all/60.0, bins=60, color='#3182bd', edgecolor='black')
plt.xlabel('Wait (minutes)')
plt.ylabel('Count')
plt.title('Wait time distribution (minutes)')
plt.tight_layout()
plt.savefig(ANALYSIS_DIR / 'wait_distribution.png')
plt.close()
print('Wrote', ANALYSIS_DIR / 'wait_distribution.png')

# 2) Mean wait cleaned (clip top 1%)
clean = wait_all.copy()
clip_val = clean.quantile(0.99)
clean_clipped = np.minimum(clean, clip_val)
# group by minute
if 'snapshot_local' in df.columns:
    tmp = df[['snapshot_local','wait_s']].dropna()
    tmp = tmp.set_index('snapshot_local').resample('1T').mean()
    tmp['wait_s_clipped'] = np.minimum(tmp['wait_s'], clip_val)
    plt.figure(figsize=(10,3))
    plt.plot(tmp.index, tmp['wait_s_clipped']/60.0, '-o', markersize=3)
    plt.xlabel('Time')
    plt.ylabel('Mean wait (min, clipped at 99th pct)')
    plt.title('Mean wait per minute (clipped)')
    plt.tight_layout()
    plt.savefig(ANALYSIS_DIR / 'mean_wait_cleaned.png')
    plt.close()
    print('Wrote', ANALYSIS_DIR / 'mean_wait_cleaned.png')

# 3) Route counts (top 20)
if 'route' in df.columns:
    route_counts = df['route'].value_counts().nlargest(20)
    plt.figure(figsize=(8,4))
    route_counts.plot(kind='bar', color='#2b8cbe')
    plt.xlabel('Route')
    plt.ylabel('ETA record count')
    plt.title('Top routes by ETA record count')
    plt.tight_layout()
    plt.savefig(ANALYSIS_DIR / 'route_counts_top20.png')
    plt.close()
    print('Wrote', ANALYSIS_DIR / 'route_counts_top20.png')

print('Done')
