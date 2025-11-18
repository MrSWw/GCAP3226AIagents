#!/usr/bin/env python3
import pandas as pd
import glob
import os
import json
from pathlib import Path

out_dir = Path('presentation/simulation')
out_dir.mkdir(parents=True, exist_ok=True)
stops_csv = out_dir / 'stops_for_merge.csv'
result_csv = out_dir / 'all_etas_two_stops.csv'
summary_json = out_dir / 'all_etas_two_stops_summary.json'

if not stops_csv.exists():
    raise SystemExit(f"Stops CSV not found: {stops_csv}")

stops = pd.read_csv(stops_csv, dtype=str)
stop_ids = set(stops['stop_id'].astype(str).tolist())

# find monitor summary CSVs anywhere in repo
search_pattern = '/workspaces/GCAP3226AIagents/**/monitor_summary*.csv'
files = glob.glob(search_pattern, recursive=True)
files = [f for f in files if os.path.isfile(f)]

rows = []
file_summaries = []
for f in files:
    try:
        df = pd.read_csv(f, low_memory=False)
    except Exception as e:
        file_summaries.append({'file': f, 'error': str(e)})
        continue
    cols = set(df.columns.str.lower())
    # detect stop id column
    stop_col = None
    for cand in ['queried_stop_id', 'stop_id', 'stopid', 'queried_stopid']:
        if cand in cols:
            # find original column name
            stop_col = [c for c in df.columns if c.lower() == cand][0]
            break
    if stop_col is None:
        file_summaries.append({'file': f, 'error': 'no stop id column'})
        continue
    # detect eta column
    eta_col = None
    for cand in ['eta', 'eta_local', 'eta_ts', 'eta_time']:
        if cand in cols:
            eta_col = [c for c in df.columns if c.lower() == cand][0]
            break
    # snapshot ts
    snap_col = None
    for cand in ['snapshot_ts', 'snapshot', 'snapshot_local', 'data_timestamp']:
        if cand in cols:
            snap_col = [c for c in df.columns if c.lower() == cand][0]
            break
    route_col = None
    for cand in ['route', 'route_name', 'route_no']:
        if cand in cols:
            route_col = [c for c in df.columns if c.lower() == cand][0]
            break

    # filter rows
    sel = df[df[stop_col].astype(str).isin(stop_ids)].copy()
    if sel.empty:
        file_summaries.append({'file': f, 'matched': 0})
        continue
    # keep useful columns
    keep = [stop_col]
    if route_col:
        keep.append(route_col)
    if eta_col:
        keep.append(eta_col)
    if snap_col:
        keep.append(snap_col)
    # ensure uniqueness of keep
    keep = list(dict.fromkeys(keep))
    sel = sel[keep]
    # rename to canonical
    rename_map = {stop_col: 'stop_id'}
    if route_col:
        rename_map[route_col] = 'route'
    if eta_col:
        rename_map[eta_col] = 'eta'
    if snap_col:
        rename_map[snap_col] = 'snapshot_ts'
    sel = sel.rename(columns=rename_map)
    # append source file info
    sel['source_file'] = os.path.relpath(f, start=os.getcwd())
    rows.append(sel)
    file_summaries.append({'file': f, 'matched': int(len(sel))})

if rows:
    all_df = pd.concat(rows, ignore_index=True, sort=False)
    # deduplicate exact duplicates
    all_df = all_df.drop_duplicates()
    # try to parse eta and snapshot_ts as datetime
    for col in ['eta', 'snapshot_ts']:
        if col in all_df.columns:
            try:
                all_df[col] = pd.to_datetime(all_df[col], utc=False, errors='coerce')
            except Exception:
                pass
    # sort
    sort_cols = [c for c in ['stop_id', 'eta', 'snapshot_ts', 'route'] if c in all_df.columns]
    if sort_cols:
        all_df = all_df.sort_values(by=sort_cols)
    all_df.to_csv(result_csv, index=False)
    summary = {
        'files_searched': len(files),
        'files_with_matches': sum(1 for s in file_summaries if s.get('matched', 0) > 0),
        'total_rows': int(len(all_df)),
        'per_file': file_summaries,
        'output_csv': str(result_csv)
    }
else:
    summary = {
        'files_searched': len(files),
        'files_with_matches': 0,
        'total_rows': 0,
        'per_file': file_summaries,
        'output_csv': str(result_csv)
    }

with open(summary_json, 'w') as f:
    json.dump(summary, f, indent=2)

print('Done. Summary written to', summary_json)
print('If rows found, CSV written to', result_csv)
