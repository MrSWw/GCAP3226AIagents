"""
use_notebook_data.py

Load station stop IDs (extracted from the notebook) and attempt to fetch KMB API data
for those stops, then save a consolidated JSON/CSV for later use in the simulation.

This is intentionally small and self-contained so you can run it quickly.
"""
import requests
import json
from datetime import datetime
import os
import sys
import pandas as pd


def get_kmb_data(stop_id):
    url = f"https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}"
    try:
        print(f"Fetching data for stop ID: {stop_id}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"Request error for {stop_id}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {stop_id}: {e}")
        return None


def process_data(data, stop_id):
    if not data or not data.get('data'):
        print(f"No data for {stop_id}")
        return []
    routes = data['data']
    out = []
    for route in routes:
        out.append({
            'stop_id': stop_id,
            'route': route.get('route'),
            'direction': route.get('dir'),
            'eta': route.get('eta'),
            'eta_seq': route.get('eta_seq'),
            'data_timestamp': route.get('data_timestamp')
        })
    return out


def main():
    base_dir = os.path.dirname(__file__)
    stations_path = os.path.join(base_dir, 'kmb_stations.json')
    out_json = os.path.join(base_dir, 'kmb_extracted.json')
    out_csv = os.path.join(base_dir, f'kmb_extracted_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

    if not os.path.exists(stations_path):
        print(f"Stations file not found: {stations_path}")
        sys.exit(1)

    with open(stations_path, 'r', encoding='utf-8') as f:
        stations = json.load(f)

    all_rows = []

    # iterate stations and stops
    for station_name, stop_ids in stations.items():
        print('\n' + '='*10 + f' {station_name} ' + '='*10)
        for sid in stop_ids:
            raw = get_kmb_data(sid)
            rows = process_data(raw, sid)
            for r in rows:
                r['station'] = station_name
            all_rows.extend(rows)

    if all_rows:
        # save JSON and CSV
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(all_rows, f, ensure_ascii=False, indent=2)
        df = pd.DataFrame(all_rows)
        df.to_csv(out_csv, index=False)
        print(f"Saved {len(all_rows)} records to:\n  {out_json}\n  {out_csv}")
    else:
        print("No records retrieved. Check network or API responses.")


if __name__ == '__main__':
    main()
