#!/usr/bin/env python3
"""
Fetch real-time ETA rows for specific route(s) at two specified stops.

Usage example:
  python3 fetch_route_pair_eta.py \
    --stop-ids 3F24CFF9046300D9 B34F59A0270AEDA4 \
    --routes 272A 272X \
    --provider kmb

Outputs JSON and CSV files into the same folder with a timestamp.
"""
import argparse
import requests
import os
import json
from datetime import datetime
import pandas as pd

BASES = {
    'kmb': 'https://data.etabus.gov.hk',
    'citybus': 'https://rt.data.gov.hk'
}


def fetch_stop_meta(stop_id, provider='kmb'):
    if provider == 'kmb':
        url = f"{BASES['kmb']}/v1/transport/kmb/stop/{stop_id}"
    else:
        url = f"{BASES['citybus']}/v1/transport/citybus-nwfb/stop/{stop_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json().get('data')


def fetch_stop_eta(stop_id, provider='kmb'):
    if provider == 'kmb':
        url = f"{BASES['kmb']}/v1/transport/kmb/stop-eta/{stop_id}"
    else:
        # Citybus ETA endpoints sometimes require route parameters; we'll try the stop-eta path
        url = f"{BASES['citybus']}/v1/transport/citybus-nwfb/stop-eta/{stop_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json().get('data', [])


def filter_routes(eta_rows, routes):
    routes_set = set(r.upper() for r in routes)
    out = []
    for row in eta_rows:
        route = (row.get('route') or '').upper()
        if route in routes_set:
            out.append(row)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stop-ids', nargs=2, required=True, help='Two stop ids to compare')
    p.add_argument('--routes', nargs='+', required=True, help='One or more route numbers to filter (e.g. 272A)')
    p.add_argument('--provider', choices=['kmb','citybus'], default='kmb')
    p.add_argument('--outdir', default=os.path.dirname(__file__))
    args = p.parse_args()

    out_rows = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for sid in args.stop_ids:
        try:
            meta = fetch_stop_meta(sid, provider=args.provider)
        except Exception as e:
            print(f'Warning: failed to fetch metadata for {sid}: {e}')
            meta = None

        try:
            etas = fetch_stop_eta(sid, provider=args.provider)
        except Exception as e:
            print(f'Warning: failed to fetch ETA for {sid}: {e}')
            etas = []

        filtered = filter_routes(etas, args.routes)
        for row in filtered:
            out = {
                'queried_stop_id': sid,
                'stop_name_en': meta.get('name_en') if meta else None,
                'stop_name_tc': meta.get('name_tc') if meta else None,
                'route': row.get('route'),
                'direction': row.get('dir') or row.get('direction') or row.get('bound'),
                'eta': row.get('eta'),
                'eta_seq': row.get('eta_seq'),
                'data_timestamp': row.get('data_timestamp')
            }
            out_rows.append(out)

    if not out_rows:
        print('No ETA rows found for the specified routes at the two stops.')
        return

    out_json = os.path.join(args.outdir, f'route_pair_eta_{timestamp}.json')
    out_csv = os.path.join(args.outdir, f'route_pair_eta_{timestamp}.csv')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=2)
    df = pd.DataFrame(out_rows)
    df.to_csv(out_csv, index=False)

    print(f'Wrote {len(out_rows)} rows to:\n  {out_json}\n  {out_csv}\n')
    # print a concise summary grouped by stop
    for sid in args.stop_ids:
        rows_for_sid = [r for r in out_rows if r['queried_stop_id'] == sid]
        print(f"Stop {sid} - {len(rows_for_sid)} matching ETA rows")
        for r in rows_for_sid:
            print(f"  Route {r['route']} eta={r['eta']} (seq={r['eta_seq']})")


if __name__ == '__main__':
    main()
