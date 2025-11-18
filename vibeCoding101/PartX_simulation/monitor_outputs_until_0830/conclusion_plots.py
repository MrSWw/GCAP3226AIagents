#!/usr/bin/env python3
"""Generate conclusion plots from monitor_summary CSV
Produces:
 - wait_distribution.png  (hist + percentiles)
 - mean_wait_cleaned.png  (per-minute mean with outliers removed)
 - route_counts.png       (counts per route)
Saved under: analysis/
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE = Path(__file__).parent
CSV = BASE / 'monitor_summary_20251104_003106.csv'
OUT = BASE / 'analysis'
OUT.mkdir(exist_ok=True)

if not CSV.exists():
    raise SystemExit('CSV not found: ' + str(CSV))

print('Loading', CSV)
df = pd.read_csv(CSV, parse_dates=['snapshot_ts','eta','data_timestamp'])

# ensure tz-aware
if df['snapshot_ts'].dt.tz is None:
    df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts']).dt.tz_localize('UTC')
if df['eta'].dt.tz is None:
    df['eta'] = pd.to_datetime(df['eta']).dt.tz_localize('Asia/Hong_Kong')

# local times
df['snapshot_local'] = df['snapshot_ts'].dt.tz_convert('Asia/Hong_Kong')
df['eta_local'] = df['eta'].dt.tz_convert('Asia/Hong_Kong')
# wait seconds
df['wait_s'] = (df['eta_local'] - df['snapshot_local']).dt.total_seconds()
# minute bucket
df['snapshot_min'] = df['snapshot_local'].dt.floor('min')

# 1) wait distribution with percentiles
wait = df['wait_s'].dropna()
# compute percentiles
p10 = wait.quantile(0.1)
p50 = wait.quantile(0.5)
p90 = wait.quantile(0.9)

plt.figure(figsize=(8,4))
plt.hist(wait/60.0, bins=80, color='C0', alpha=0.8)
plt.axvline(p10/60.0, color='C1', linestyle='--', label=f'10%={p10/60:.1f}m')
plt.axvline(p50/60.0, color='C2', linestyle='-', label=f'median={p50/60:.1f}m')
plt.axvline(p90/60.0, color='C3', linestyle='--', label=f'90%={p90/60:.1f}m')
plt.xlabel('wait (minutes)')
plt.ylabel('count')
plt.title('Wait time distribution (minutes)')
plt.legend()
plt.tight_layout()
out1 = OUT / 'wait_distribution.png'
plt.savefig(out1, dpi=150)
plt.close()
print('Wrote', out1)

# 2) mean wait per minute: raw vs cleaned (filter out very large waits > 3600s)
per_min_raw = df.groupby('snapshot_min')['wait_s'].mean()
clean_df = df[df['wait_s'].between(0,3600)]
per_min_clean = clean_df.groupby('snapshot_min')['wait_s'].mean()

plt.figure(figsize=(10,4))
per_min_raw.plot(label='raw mean wait (s)', alpha=0.6)
per_min_clean.plot(label='cleaned mean wait (s, <=3600s)', linewidth=2)
plt.ylabel('mean wait (s)')
plt.xlabel('minute')
plt.title('Mean wait per minute: raw vs cleaned')
plt.legend()
plt.tight_layout()
out2 = OUT / 'mean_wait_cleaned.png'
plt.savefig(out2, dpi=150)
plt.close()
print('Wrote', out2)

# 3) route counts (how many ETA rows per route) - top routes
route_counts = df['route'].value_counts().nlargest(20)
plt.figure(figsize=(8,4))
route_counts.plot(kind='bar')
plt.ylabel('rows (ETA entries)')
plt.title('Top routes by ETA entry count')
plt.tight_layout()
out3 = OUT / 'route_counts_top20.png'
plt.savefig(out3, dpi=150)
plt.close()
print('Wrote', out3)

print('Done')
