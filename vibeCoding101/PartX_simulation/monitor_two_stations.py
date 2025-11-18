#!/usr/bin/env python3
"""
monitor_two_stations.py

Continuously poll KMB (or Citybus) stop-eta endpoints for two stops and
capture snapshots of the realtime ETA situation for the next hour (or user-provided horizon).

The script saves:
 - per-snapshot JSON files in ./monitor_outputs/
 - a consolidated CSV `monitor_summary_{timestamp}.csv` with all captured ETA rows

Usage (example):
  python3 monitor_two_stations.py \
    --stop-ids 3F24CFF9046300D9 B34F59A0270AEDA4 \
    --provider kmb \
    --horizon-min 60 \
    --interval-sec 30

For quick tests use smaller horizon/interval (e.g. --horizon-min 1 --interval-sec 5).
"""
from __future__ import annotations
import argparse
import os
import time
import json
from datetime import datetime, timedelta
import requests
from dateutil import parser as dateparser
import pandas as pd

BASES = {
    'kmb': 'https://data.etabus.gov.hk',
    'citybus': 'https://rt.data.gov.hk'
}


def fetch_stop_eta(stop_id: str, provider: str = 'kmb'):
    """Return list of ETA rows (may be empty)."""
    if provider == 'kmb':
        url = f"{BASES['kmb']}/v1/transport/kmb/stop-eta/{stop_id}"
    else:
        url = f"{BASES['citybus']}/v1/transport/citybus-nwfb/stop-eta/{stop_id}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        j = r.json()
        return j.get('data', [])
    except Exception as e:
        print(f"Error fetching ETA for {stop_id}: {e}")
        return []


def snapshot_two_stops(stop_ids, provider, horizon_min, out_dir):
    """Take one snapshot: fetch ETAs for each stop, filter to horizon, and save JSON."""
    # use timezone-aware now
    now = datetime.now().astimezone()
    horizon_dt = now + timedelta(minutes=horizon_min)
    snapshot = {'timestamp': now.isoformat(), 'horizon_min': horizon_min, 'stops': []}

    for sid in stop_ids:
        rows = fetch_stop_eta(sid, provider=provider)
        filtered = []
        for r in rows:
            eta = r.get('eta')
            if not eta:
                continue
            try:
                eta_dt = dateparser.parse(eta)
            except Exception:
                continue
            if eta_dt < now or eta_dt > horizon_dt:
                continue
            # annotate with parsed datetime for downstream
            r['_eta_dt'] = eta_dt.isoformat()
            filtered.append(r)

        snapshot['stops'].append({'stop_id': sid, 'rows': filtered})

    # save snapshot JSON
    ts = now.strftime('%Y%m%d_%H%M%S')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f'snapshot_{ts}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"Saved snapshot {path} (stop rows: {[len(s['rows']) for s in snapshot['stops']]})")
    return snapshot


def consolidate_snapshots(out_dir, summary_path):
    """Read all snapshot JSON files in out_dir and write a consolidated CSV of ETA rows."""
    files = sorted([f for f in os.listdir(out_dir) if f.startswith('snapshot_') and f.endswith('.json')])
    all_rows = []
    for fn in files:
        fp = os.path.join(out_dir, fn)
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                s = json.load(f)
        except Exception:
            continue
        snap_ts = s.get('timestamp')
        for stop in s.get('stops', []):
            sid = stop.get('stop_id')
            for r in stop.get('rows', []):
                all_rows.append({
                    'snapshot_ts': snap_ts,
                    'queried_stop_id': sid,
                    'route': r.get('route'),
                    'direction': r.get('dir') or r.get('direction') or r.get('bound'),
                    'eta': r.get('eta'),
                    'eta_seq': r.get('eta_seq'),
                    'data_timestamp': r.get('data_timestamp')
                })

    if not all_rows:
        print('No rows to consolidate.')
        return None
    df = pd.DataFrame(all_rows)
    df.to_csv(summary_path, index=False)
    print(f'Wrote consolidated summary to {summary_path} ({len(df)} rows)')
    return summary_path


def monitor_loop(stop_ids, provider, horizon_min, interval_sec, duration_min, out_dir):
    """Run polling loop for duration_min minutes, taking snapshots every interval_sec seconds."""
    start = datetime.now()
    end = start + timedelta(minutes=duration_min)
    print(f"Monitoring {stop_ids} with provider={provider} for {duration_min} minutes (interval {interval_sec}s)")
    i = 0
    while datetime.now() < end:
        i += 1
        print(f"Snapshot {i} at {datetime.now().isoformat()}")
        snapshot_two_stops(stop_ids, provider, horizon_min, out_dir)
        # sleep until next interval or until end
        t_remain = (end - datetime.now()).total_seconds()
        if t_remain <= 0:
            break
        sleep_for = min(interval_sec, t_remain)
        time.sleep(sleep_for)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--stop-ids', nargs=2, required=True, help='Two stop ids to monitor')
    p.add_argument('--provider', choices=['kmb', 'citybus'], default='kmb')
    p.add_argument('--horizon-min', type=int, default=60, help='Look-ahead horizon (minutes) for ETA filtering')
    p.add_argument('--interval-sec', type=int, default=30, help='Polling interval in seconds')
    p.add_argument('--duration-min', type=int, default=60, help='Total monitoring duration in minutes')
    p.add_argument('--out-dir', default=os.path.join(os.path.dirname(__file__), 'monitor_outputs'))
    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    monitor_loop(args.stop_ids, args.provider, args.horizon_min, args.interval_sec, args.duration_min, args.out_dir)
    # after monitoring, consolidate
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_path = os.path.join(args.out_dir, f'monitor_summary_{ts}.csv')
    consolidate_snapshots(args.out_dir, summary_path)


if __name__ == '__main__':
    main()
