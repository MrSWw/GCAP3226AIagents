#!/usr/bin/env python3
"""Animate bus arrivals for current vs two merged scenarios.

Reads a monitor CSV (with columns including `queried_stop_id` and `eta`),
builds schedules for two selected stops and produces a 2-hour animation
comparing: `pre` (current separate stops), `post1` (merged stop half/half),
and `post2` (merged single stop). The animation approximates bus movement
by showing approaching buses in a short approach window before ETA.

Usage (example):
    python3 animate_bus_movements.py \
      --input /path/to/monitor_summary_both_*.csv \
      --stops 3F24CFF9046300D9 B34F59A0270AEDA4 \
      --horizon 120 \
      --out animation.mp4

"""
from __future__ import annotations
import argparse
import os
from datetime import timedelta
from typing import List, Dict

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd


def load_schedules(csv_path: str, stop_ids: List[str], horizon_min: int = 120):
    df = pd.read_csv(csv_path)
    df = df[df['queried_stop_id'].isin(stop_ids)]
    df = df.dropna(subset=['eta'])
    df['eta_dt'] = pd.to_datetime(df['eta'])
    min_eta = df['eta_dt'].min()
    env_start = min_eta - pd.Timedelta(minutes=5)
    horizon_dt = env_start + pd.Timedelta(minutes=horizon_min)
    schedules: Dict[str, List[float]] = {}
    for sid in stop_ids:
        sub = df[df['queried_stop_id'] == sid]
        etas = sorted(sub['eta_dt'].unique())
        etas = [e.to_pydatetime() for e in etas if e.to_pydatetime() <= horizon_dt]
        offsets = [float((e - env_start).total_seconds()) for e in etas if e >= env_start]
        schedules[sid] = sorted(offsets)
    return env_start.to_pydatetime(), schedules


def build_events_for_scenarios(schedules: Dict[str, List[float]]):
    # pre: separate stops; post: merged stop (union)
    stop_ids = list(schedules.keys())
    pre_events = []
    for i, sid in enumerate(stop_ids):
        for t in schedules[sid]:
            pre_events.append({'t': t, 'stop_idx': i, 'stop_id': sid})

    merged = sorted(list(set(sum([schedules[s] for s in stop_ids], []))))
    post_events = []
    for t in merged:
        post_events.append({'t': t, 'stop_idx': 0, 'stop_id': '_merged_'})

    # For visualization we will use three lanes (pre, post1, post2)
    return {'pre': pre_events, 'post1': post_events, 'post2': post_events}


def animate(events_by_scenario: Dict[str, List[Dict]], horizon_s: int, out_path: str, env_start_str: str):
    # lanes: pre, post1, post2 (y positions)
    lanes = ['pre', 'post1', 'post2']
    lane_y = {lanes[i]: 2 - i for i in range(len(lanes))}  # top to bottom

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_xlim(0, 1.05)
    ax.set_ylim(-0.5, 2.5)
    ax.set_yticks(list(lane_y.values()))
    ax.set_yticklabels(['Current (pre)', 'Post1 (merged)', 'Post2 (merged)'])
    ax.set_title(f'Bus arrivals animation (start: {env_start_str})')

    # draw stops markers for pre (two stops at x=1.0 positions slightly separated),
    # and merged stop at x=1.0 center
    stop_x_pre = [0.92, 1.0]
    ax.text(0.92, lane_y['pre'] + 0.15, 'Stop A', ha='center', fontsize=9)
    ax.text(1.0, lane_y['pre'] + 0.15, 'Stop B', ha='center', fontsize=9)
    ax.plot([0.92], [lane_y['pre']], marker='s', color='k')
    ax.plot([1.0], [lane_y['pre']], marker='s', color='k')

    ax.text(0.96, lane_y['post1'] + 0.15, 'Merged', ha='center', fontsize=9)
    ax.plot([0.96], [lane_y['post1']], marker='s', color='k')
    ax.text(0.96, lane_y['post2'] + 0.15, 'Merged', ha='center', fontsize=9)
    ax.plot([0.96], [lane_y['post2']], marker='s', color='k')

    # parameters for approach visualization
    approach_window = 10 * 60.0  # show approach for 10 minutes before arrival
    dwell = 30.0  # seconds to show bus at stop

    scatters = {lane: ax.scatter([], [], s=80, label=lane) for lane in lanes}

    times_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

    # prepare events arrays
    evs = {lane: sorted([e['t'] for e in events_by_scenario[lane]]) for lane in lanes}

    def init():
        for s in scatters.values():
            s.set_offsets(np.empty((0, 2)))
        times_text.set_text('')
        return list(scatters.values()) + [times_text]

    def frame(i):
        # i is frame index in seconds
        t = i
        pts = {lane: [] for lane in lanes}
        for lane in lanes:
            for ev_t in evs[lane]:
                # if bus is approaching or at stop
                dt = ev_t - t
                if -dwell <= dt <= approach_window:
                    # position: when dt>0 approaching from x=0.05 to stop_x
                    if dt > 0:
                        frac = 1.0 - (dt / approach_window)
                        x = 0.05 + frac * (0.9)
                        y = lane_y[lane]
                    else:
                        # at stop
                        x = 0.96 if lane != 'pre' else (0.92 if ev_t % 2 == 0 else 1.0)
                        y = lane_y[lane]
                    pts[lane].append([x, y])

        for lane in lanes:
            arr = np.array(pts[lane]) if pts[lane] else np.empty((0, 2))
            scatters[lane].set_offsets(arr)
        times_text.set_text(f't = {int(t/60)} min')
        return list(scatters.values()) + [times_text]

    fps = 10
    total_frames = int(horizon_s)
    ani = animation.FuncAnimation(fig, frame, frames=range(0, total_frames, 1), init_func=init, blit=True)

    # save
    out_ext = os.path.splitext(out_path)[1].lower()
    print('Saving animation to', out_path)
    if out_ext in ['.mp4', '.m4v']:
        # matplotlib versions expose writers differently; attempt safe access
        Writer = None
        try:
            Writer = animation.writers['ffmpeg']
        except Exception:
            Writer = None
        if Writer is None:
            print('ffmpeg writer not available; trying to save as GIF')
            gif_path = out_path.replace('.mp4', '.gif')
            ani.save(gif_path, writer='pillow', fps=fps)
            print('Saved GIF to', gif_path)
        else:
            writer = Writer(fps=fps)
            ani.save(out_path, writer=writer)
    else:
        ani.save(out_path, writer='pillow', fps=fps)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=False, default=os.path.join(os.path.dirname(__file__), '..', '..', 'monitor_outputs_1hr', 'monitor_summary_both_20251105_070549.csv'))
    p.add_argument('--stops', nargs=2, required=False, help='Two queried_stop_id values (default: first two in CSV)')
    p.add_argument('--horizon', type=int, default=120, help='horizon in minutes')
    p.add_argument('--out', default=os.path.join(os.path.dirname(__file__), 'bus_movement_2h.mp4'))
    args = p.parse_args()

    env_start, schedules = load_schedules(args.input, args.stops if args.stops else list(pd.read_csv(args.input)['queried_stop_id'].unique())[:2], horizon_min=args.horizon)
    print('Loaded schedules for stops:', list(schedules.keys()))
    events = build_events_for_scenarios(schedules)
    horizon_s = args.horizon * 60
    animate(events, horizon_s, args.out, env_start.isoformat())


if __name__ == '__main__':
    main()
