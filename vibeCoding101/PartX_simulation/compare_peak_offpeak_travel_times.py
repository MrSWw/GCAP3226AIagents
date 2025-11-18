#!/usr/bin/env python3
"""
Compare travel time between two stops using consolidated CSVs for two runs.
Approach:
- For each CSV: group by snapshot_ts and route. For each (snapshot,route) where both stops present,
  take the earliest non-null ETA per stop (min(eta) per stop), compute delta = eta_stopB - eta_stopA if positive.
- Report summary stats (count, mean, median, 90th percentile) and output CSVs with deltas.

Usage: python3 compare_peak_offpeak_travel_times.py
"""
import pandas as pd
from pathlib import Path
import numpy as np

BASE = Path(__file__).resolve().parent

files = {
    'offpeak': BASE / 'monitor_outputs_60min' / 'monitor_summary_20251031_062043.csv',
    'peak': BASE / 'monitor_outputs_until_0830' / 'monitor_summary_20251104_003106.csv',
}

# If paths above are not correct relative, try absolute location
for k,v in files.items():
    if not v.exists():
        # try absolute from workspace root
        alt = Path('/workspaces/GCAP3226AIagents') / v
        if alt.exists():
            files[k] = alt

print('Using files:')
for k,v in files.items():
    print(k, v, 'exists=', v.exists())


def load_and_compute_deltas(path):
    df = pd.read_csv(path, parse_dates=['snapshot_ts','eta','data_timestamp'])
    # keep only records with non-null eta
    df = df.dropna(subset=['eta'])
    # Ensure timezone-aware: many ETAs are in +08:00 and snapshot_ts in +00:00; pandas parsed them.
    # Keep stop ids distinct
    stops = df['queried_stop_id'].unique()
    # We expect two stops; find them
    stops = list(stops)
    if len(stops) < 2:
        print('Warning: less than two stops found in', path)
    # We will treat the first as A and second as B but prefer known IDs if present
    # Known stop ids in this project: 3F24CFF9046300D9 (St. Martin?) and B34F59A0270AEDA4 (Chong San?)
    preferred = ['3F24CFF9046300D9','B34F59A0270AEDA4']
    stopA, stopB = (stops[0], stops[1]) if len(stops) >= 2 else (stops[0], stops[0])
    for p in preferred:
        if p in stops:
            if p == preferred[0]:
                stopA = p
            elif p == preferred[1]:
                stopB = p
    # Make sure stopA != stopB
    if stopA == stopB and len(stops) >= 2:
        stopB = [s for s in stops if s!=stopA][0]
    print('Using stopA=',stopA,'stopB=',stopB)

    # For each snapshot_ts and route, compute min ETA at each stop
    grouped = df.groupby(['snapshot_ts','route','queried_stop_id'])['eta'].min().reset_index()
    # pivot so stops are columns
    pivot = grouped.pivot_table(index=['snapshot_ts','route'], columns='queried_stop_id', values='eta')
    # only keep rows where both stops present
    pivot = pivot.dropna(axis=0, how='any')
    if pivot.empty:
        print('No matching snapshot+route pairs with both stops present in', path)
        return pd.DataFrame()
    # compute delta in seconds: stopB - stopA
    # convert to datetime
    pivot = pivot.reset_index()
    pivot['eta_A'] = pd.to_datetime(pivot[stopA])
    pivot['eta_B'] = pd.to_datetime(pivot[stopB])
    pivot['delta_s'] = (pivot['eta_B'] - pivot['eta_A']).dt.total_seconds()
    # keep only positive deltas
    pivot = pivot[pivot['delta_s'] > 0].copy()
    return pivot[['snapshot_ts','route',stopA,stopB,'eta_A','eta_B','delta_s']]

results = {}
for k,path in files.items():
    results[k] = load_and_compute_deltas(path)
    print(f'{k}: computed {len(results[k])} travel-time deltas')

# summarize
summary = {}
for k,df in results.items():
    if df.empty:
        summary[k] = None
        continue
    arr = df['delta_s'].values
    summary[k] = {
        'count': int(len(arr)),
        'mean_s': float(np.mean(arr)),
        'median_s': float(np.median(arr)),
        'p90_s': float(np.percentile(arr,90)),
        'std_s': float(np.std(arr, ddof=1)),
    }

print('\nSummary:')
for k,v in summary.items():
    print(k, v)

# compare peak vs offpeak
if summary.get('peak') and summary.get('offpeak'):
    diff_mean = summary['peak']['mean_s'] - summary['offpeak']['mean_s']
    diff_median = summary['peak']['median_s'] - summary['offpeak']['median_s']
    diff_p90 = summary['peak']['p90_s'] - summary['offpeak']['p90_s']
    print('\nDifferences (peak - offpeak) in seconds:')
    print('mean_s diff:', diff_mean)
    print('median_s diff:', diff_median)
    print('p90_s diff:', diff_p90)

# save detailed CSVs
OUT = BASE / 'presentation' / 'travel_time_comparison'
OUT.mkdir(parents=True, exist_ok=True)
for k,df in results.items():
    outp = OUT / f'travel_deltas_{k}.csv'
    df.to_csv(outp, index=False)
    print('wrote', outp)

# write summary JSON
import json
with open(OUT / 'travel_time_summary.json','w') as f:
    json.dump({'summary':summary}, f, indent=2)
print('wrote summary JSON at', OUT / 'travel_time_summary.json')

print('Done')
