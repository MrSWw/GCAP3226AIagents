 #!/usr/bin/env python3
"""
Run a 1-hour monitor for two stops, consolidate snapshots and produce two CSVs:
 - monitor_summary_{ts}.csv  (all ETA rows)
 - monitor_summary_both_{ts}.csv (only rows where the same route appears at the same snapshot for both stops)

Usage: run without args (script hardcodes the two stop ids from your workspace).
"""
from pathlib import Path
import time
from datetime import datetime

WORKDIR = Path(__file__).resolve().parent
OUT_DIR = WORKDIR / 'monitor_outputs_1hr'
OUT_DIR.mkdir(exist_ok=True)

import monitor_two_stations as m2s
import pandas as pd

# Configuration (per your request)
STOP_IDS = ['3F24CFF9046300D9', 'B34F59A0270AEDA4']
PROVIDER = 'kmb'
HORIZON_MIN = 60
INTERVAL_SEC = 30
DURATION_MIN = 60


def run_monitor_and_postprocess():
    print(f"Starting monitor for {DURATION_MIN} minutes: stops={STOP_IDS}, interval={INTERVAL_SEC}s")
    # Run the monitoring loop which saves snapshot JSON files into OUT_DIR
    m2s.monitor_loop(STOP_IDS, PROVIDER, HORIZON_MIN, INTERVAL_SEC, DURATION_MIN, str(OUT_DIR))

    # After monitoring, consolidate snapshots (this writes the consolidated CSV)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    summary_path = OUT_DIR / f'monitor_summary_{ts}.csv'
    print('Consolidating snapshots to', summary_path)
    m2s.consolidate_snapshots(str(OUT_DIR), str(summary_path))

    # Wait briefly to ensure file is flushed
    time.sleep(1)

    if not summary_path.exists():
        print('ERROR: consolidated CSV not found at', summary_path)
        return

    # Read consolidated CSV and produce the "both" file
    print('Loading consolidated CSV for post-processing...')
    df = pd.read_csv(summary_path)

    # Normalize snapshot timestamp column name (monitor_two_stations uses 'snapshot_ts')
    if 'snapshot_ts' not in df.columns and 'snapshot_local' in df.columns:
        df['snapshot_ts'] = df['snapshot_local']

    # Determine (snapshot_ts, route) pairs that appear for both stops
    pairs = df.groupby(['snapshot_ts','route'])['queried_stop_id'].nunique().reset_index()
    both_pairs = pairs[pairs['queried_stop_id'] >= 2][['snapshot_ts','route']]

    if both_pairs.empty:
        print('No matching route seen in both stops at the same snapshot timestamps.')
    else:
        # Merge to get full rows matching those pairs
        merged = df.merge(both_pairs, on=['snapshot_ts','route'], how='inner')
        both_path = OUT_DIR / f'monitor_summary_both_{ts}.csv'
        merged.to_csv(both_path, index=False)
        print('Wrote both-stops CSV to', both_path)

    print('All done. Outputs in', OUT_DIR)


if __name__ == '__main__':
    run_monitor_and_postprocess()
