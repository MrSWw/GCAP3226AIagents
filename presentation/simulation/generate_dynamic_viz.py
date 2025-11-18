#!/usr/bin/env python3
"""
Generate a simple dynamic visualization (GIF) showing bus arrivals/departures
for selected stops using ETA CSV data. 

Behavior:
- Default input: `presentation/simulation/all_etas_two_stops.csv` (if present)
- Fallback: glob over monitor_summary CSVs under `vibeCoding101/PartX_simulation/monitor_outputs_*/`.
- For each ETA entry we create an arrival event; departure = arrival + DWELL_SEC.
- Animation: for each timestep show active buses at each stop and a bar chart of queue lengths.

Output:
- `presentation/simulation/dynamic_buses.gif`
- `presentation/simulation/dynamic_buses_snapshot.png` (final frame)

Requirements: pandas, numpy, matplotlib, pillow
"""
import os
import glob
import math
import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Defaults (can be overridden with CLI args)
OUTDIR = os.path.dirname(__file__)
DEFAULT_ETA_CSV = os.path.join(OUTDIR, 'all_etas_two_stops.csv')
DEFAULT_MONITOR_GLOB = '/workspaces/GCAP3226AIagents/vibeCoding101/PartX_simulation/monitor_outputs_*/monitor_summary*.csv'
DEFAULT_DWELL = 20  # seconds each bus stays at stop (simple fixed dwell)
DEFAULT_STEP = 5  # animation frame step in seconds
DEFAULT_FPS = 5
DEFAULT_GIF = os.path.join(OUTDIR, 'dynamic_buses.gif')
DEFAULT_SNAP = os.path.join(OUTDIR, 'dynamic_buses_snapshot.png')

# Helper: read ETA CSV (expected columns: stop_id, route, eta, snapshot_ts ...)

def read_eta_source(eta_csv=None, monitor_glob=None):
    # prefer default extracted CSV
    csv_path = eta_csv or DEFAULT_ETA_CSV
    if os.path.exists(csv_path):
        print(f"Using ETA CSV: {csv_path}")
        df = pd.read_csv(csv_path)
    else:
        # fallback: search monitor_summary files
        monitor_pattern = monitor_glob or DEFAULT_MONITOR_GLOB
        print(f"Default ETA CSV not found — searching monitor_summary CSVs using pattern: {monitor_pattern}")
        files = sorted(glob.glob(monitor_pattern))
        if not files:
            raise FileNotFoundError('No ETA CSV or monitor_summary files found')
        pieces = []
        for f in files:
            try:
                d = pd.read_csv(f)
                pieces.append(d)
            except Exception:
                continue
        if not pieces:
            raise FileNotFoundError('No readable monitor_summary CSVs found')
        df = pd.concat(pieces, ignore_index=True)
    return df


def prepare_events(df, stop_ids=None, dwell_sec=DEFAULT_DWELL):
    # Normalize column names
    if 'eta' not in df.columns:
        # try common alternatives
        if 'ETA' in df.columns:
            df['eta'] = df['ETA']
    df = df.copy()
    df = df.dropna(subset=['eta'])
    # parse eta to timezone-aware datetimes if possible
    df['eta_dt'] = pd.to_datetime(df['eta'], utc=True, errors='coerce')
    # If parse failed (no timezone), try without utc
    df.loc[df['eta_dt'].isna(), 'eta_dt'] = pd.to_datetime(df.loc[df['eta_dt'].isna(), 'eta'], errors='coerce')
    df = df.dropna(subset=['eta_dt'])

    # If stop filter provided, filter
    if stop_ids is not None:
        df = df[df['stop_id'].isin(stop_ids)]

    # group per stop
    stops = sorted(df['stop_id'].unique())
    events = []
    for stop in stops:
        sub = df[df['stop_id'] == stop]
        for _, row in sub.iterrows():
            t = row['eta_dt']
            # ensure datetime is naive or timezone consistent
            if t.tzinfo is not None:
                t = t.tz_convert(None).tz_localize(None)
            arrival = t
            departure = arrival + timedelta(seconds=dwell_sec)
            events.append({'stop_id': stop, 'route': row.get('route',''), 'arrival': arrival, 'departure': departure})
    # sort events by arrival
    events = sorted(events, key=lambda x: x['arrival'])
    return stops, events


def build_timeline(events, start=None, end=None, frame_step_sec=DEFAULT_STEP):
    if not events:
        raise ValueError('No events to build timeline')
    if start is None:
        start = min(e['arrival'] for e in events) - timedelta(seconds=60)
    if end is None:
        end = max(e['departure'] for e in events) + timedelta(seconds=60)
    total_seconds = int((end - start).total_seconds())
    times = [start + timedelta(seconds=i) for i in range(0, total_seconds+1, frame_step_sec)]
    return start, end, times


def animate_buses(stops, events, times, out_gif=DEFAULT_GIF, snapshot=DEFAULT_SNAP, fps=DEFAULT_FPS):
    stop_y = {stop: i for i, stop in enumerate(stops)}
    fig = plt.figure(figsize=(10,5))
    ax_map = plt.subplot2grid((1,3),(0,0), colspan=1)
    ax_bar = plt.subplot2grid((1,3),(0,1), colspan=2)

    ax_map.set_ylim(-0.5, len(stops)-0.5)
    ax_map.set_xlim(0,1)
    ax_map.set_xticks([])
    ax_map.set_yticks(list(range(len(stops))))
    ax_map.set_yticklabels(stops)
    ax_map.set_title('Active buses at stops (markers represent buses)')

    bars = ax_bar.bar(stops, [0]*len(stops))
    ax_bar.set_ylim(0, max(5, max(1, math.ceil(len(events)/len(stops)) + 2)))
    ax_bar.set_title('Number of buses currently at stop')
    ax_bar.set_ylabel('Count')

    time_text = fig.suptitle('')

    def frame(i):
        t = times[i]
        # find active events
        active = [e for e in events if e['arrival'] <= t < e['departure']]
        counts = {s:0 for s in stops}
        ax_map.cla()
        ax_map.set_ylim(-0.5, len(stops)-0.5)
        ax_map.set_xlim(0,1)
        ax_map.set_xticks([])
        ax_map.set_yticks(list(range(len(stops))))
        ax_map.set_yticklabels(stops)
        ax_map.set_title('Active buses at stops (markers represent buses)')
        for a in active:
            counts[a['stop_id']] += 1
            y = stop_y[a['stop_id']]
            # place marker
            ax_map.plot(0.5, y, marker='s', markersize=12, color='tab:blue')
            ax_map.text(0.52, y, str(a.get('route','')), va='center', fontsize=8)
        # update bars
        ax_bar.cla()
        ax_bar.bar(stops, [counts[s] for s in stops], color='tab:orange')
        ax_bar.set_ylim(0, max(5, max(1, math.ceil(len(events)/len(stops)) + 2)))
        ax_bar.set_title('Number of buses currently at stop')
        ax_bar.set_ylabel('Count')
        ax_bar.set_xticklabels(stops, rotation=45)
        time_text.set_text(f'Time: {t.strftime("%Y-%m-%d %H:%M:%S")}')
        return []

    anim = FuncAnimation(fig, frame, frames=len(times), interval=1000//fps)
    print('Rendering GIF (this may take some seconds) ->', out_gif)
    try:
        writer = PillowWriter(fps=fps)
        anim.save(out_gif, writer=writer)
        print('Saved GIF:', out_gif)
    except Exception as e:
        print('Failed to save GIF:', e)
    # save final snapshot
    frame(-1 if len(times)>0 else 0)
    fig.savefig(snapshot, dpi=150)
    print('Saved snapshot:', snapshot)


def main(args=None):
    parser = argparse.ArgumentParser(description='Generate dynamic bus arrival visualization')
    parser.add_argument('--eta-csv', help='Path to ETA CSV to use (overrides default)')
    parser.add_argument('--monitor-glob', help='Glob pattern for monitor_summary CSV fallback')
    parser.add_argument('--dwell', type=int, default=DEFAULT_DWELL, help='Dwell time in seconds')
    parser.add_argument('--step', type=int, default=DEFAULT_STEP, help='Frame step in seconds')
    parser.add_argument('--fps', type=int, default=DEFAULT_FPS, help='GIF frames-per-second')
    parser.add_argument('--out-gif', default=DEFAULT_GIF, help='Output GIF path')
    parser.add_argument('--out-snap', default=DEFAULT_SNAP, help='Output snapshot PNG path')
    ns = parser.parse_args(args=args)

    df = read_eta_source(eta_csv=ns.eta_csv, monitor_glob=ns.monitor_glob)
    # notebook has stop ids for two stations; we can optionally restrict to those
    # try to infer stop_id column
    if 'stop_id' not in df.columns:
        # try alternatives
        possible = [c for c in df.columns if 'stop' in c.lower()]
        if possible:
            df = df.rename(columns={possible[0]:'stop_id'})
    stops, events = prepare_events(df, dwell_sec=ns.dwell)
    if not events:
        print('No ETA events found after parsing')
        return
    start, end, times = build_timeline(events, frame_step_sec=ns.step)
    print(f'Timeline from {start} to {end}, frames: {len(times)}')
    animate_buses(stops, events, times, out_gif=ns.out_gif, snapshot=ns.out_snap, fps=ns.fps)

if __name__ == '__main__':
    main()

if __name__ == '__main__':
    main()
