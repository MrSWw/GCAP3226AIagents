#!/usr/bin/env python3
"""Simulate pre-merge vs two post-merge variants and report KPIs.

Scenarios:
- pre: two separate stops (no walking)
- post1: "half-half" merged scenario (post-merge 1) — passengers walk to merged stop, half get short walk, half long walk
- post2: "merge to single stop" (post-merge 2) — all passengers walk same walk_time

This reads a consolidated monitor CSV (with columns including
`queried_stop_id` and `eta`) to build bus arrival schedules, then
simulates passenger arrivals as Poisson processes and bus boarding as
capacity-limited FIFO. Outputs CSV/JSON summaries and simple PNG plots.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import random
import statistics
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_eta_schedules(csv_path: str, stop_ids: List[str], horizon_min: int = 120):
    df = pd.read_csv(csv_path)
    # ensure eta parsed
    df = df[df['queried_stop_id'].isin(stop_ids)]
    df = df.dropna(subset=['eta'])
    df['eta_dt'] = pd.to_datetime(df['eta'])
    # choose reference start as min eta minus 5 minutes to allow passenger arrivals
    min_eta = df['eta_dt'].min()
    env_start = (min_eta - pd.Timedelta(minutes=5)).to_pydatetime()
    horizon_dt = env_start + timedelta(minutes=horizon_min)
    schedules = {}
    for sid in stop_ids:
        sub = df[df['queried_stop_id'] == sid]
        # keep unique ETAs
        etas = sorted(sub['eta_dt'].unique())
        # filter by horizon
        etas = [e.to_pydatetime() for e in etas if e.to_pydatetime() <= horizon_dt]
        # convert to seconds offset relative to env_start
        offsets = [int((e - env_start).total_seconds()) for e in etas if e >= env_start]
        schedules[sid] = sorted(offsets)
    return env_start, schedules


def generate_passenger_arrivals(rate_per_min: float, horizon_seconds: int, rng: np.random.Generator):
    arrivals = []
    if rate_per_min <= 0:
        return arrivals
    scale = 60.0 / rate_per_min
    t = 0.0
    while True:
        isi = rng.exponential(scale=scale)
        t += isi
        if t > horizon_seconds:
            break
        arrivals.append(int(t))
    return arrivals


def run_one_replication(schedules: Dict[str, List[int]],
                       scenario: str,
                       rate_per_min: float,
                       capacity: int,
                       base_dwell: float,
                       alpha: float,
                       walk_time_post2: int,
                       short_walk: int,
                       long_walk: int,
                       half_prob: float,
                       in_vehicle_time_s: float,
                       horizon_seconds: int,
                       rng: np.random.Generator):
    # Generate passenger arrivals per original stop
    passengers = []  # list of dict: {'orig_stop', 'merged_arrival', 'walk_s'}
    for sid in schedules.keys():
        arrs = generate_passenger_arrivals(rate_per_min, horizon_seconds, rng)
        for a in arrs:
            if scenario == 'pre':
                walk = 0
                merged_arrival = a
            elif scenario == 'post1':
                # half-half: assign short or long walk randomly
                if rng.random() < half_prob:
                    walk = short_walk
                else:
                    walk = long_walk
                merged_arrival = a + walk
            else:  # post2
                walk = walk_time_post2
                merged_arrival = a + walk
            passengers.append({'orig': sid, 'arrival': merged_arrival, 'walk': walk})

    # Build bus arrival schedule
    # For pre scenario, buses service each stop separately (we will treat as independent buses per stop)
    if scenario == 'pre':
        # run two independent single-stop sims and aggregate
        results = {'waits': [], 'walks': [], 'dwell_times': [], 'boarded_total': 0, 'remaining_queue': 0}
        for sid, sch in schedules.items():
            # find passengers that belong to this stop
            p_times = sorted([p['arrival'] for p in passengers if p['orig'] == sid])
            bus_times = sorted(sch)
            waits, dwell_list, boarded = simulate_boarding_loop(p_times, bus_times, capacity, base_dwell, alpha)
            results['waits'].extend(waits)
            results['walks'].extend([0] * len(waits))
            results['dwell_times'].extend(dwell_list)
            results['boarded_total'] += boarded
            results['remaining_queue'] += max(0, len(p_times) - boarded - len(waits))
        return results

    # For merged scenarios, combine schedule and combined passenger queue
    merged_bus_times = sorted(sum([sch for sch in schedules.values()], []))
    # sort passengers by merged arrival time
    p_times = sorted([p['arrival'] for p in passengers])
    p_walks = [p['walk'] for p in sorted(passengers, key=lambda x: x['arrival'])]

    waits, dwell_list, boarded = simulate_boarding_loop(p_times, merged_bus_times, capacity, base_dwell, alpha)
    total_walk = sum(p_walks)
    return {'waits': waits, 'walks': p_walks, 'dwell_times': dwell_list, 'boarded_total': boarded, 'remaining_queue': max(0, len(p_times) - boarded)}


def simulate_boarding_loop(p_times: List[int], bus_times: List[int], capacity: int, base_dwell: float, alpha: float):
    # p_times and bus_times are in seconds from env start
    queue = deque(sorted(p_times))
    waits = []
    dwell_list = []
    boarded_total = 0
    # Make a mutable copy of bus_times because we may add dwell delays to subsequent buses
    bus_times = list(bus_times)
    i = 0
    while i < len(bus_times):
        bt = bus_times[i]
        # board up to capacity from queue whose arrival <= bt
        boarding = 0
        while queue and queue[0] <= bt and boarding < capacity:
            at = queue.popleft()
            waits.append(bt - at)
            boarding += 1
        boarded_total += boarding
        dwell = base_dwell + alpha * boarding
        dwell_list.append(dwell)
        # shift subsequent buses by dwell to model knock-on delay
        for j in range(i+1, len(bus_times)):
            bus_times[j] += int(dwell)
        i += 1
    return waits, dwell_list, boarded_total


def summarize_replications(rep_results: List[Dict[str, Any]], in_vehicle_time_s: float):
    # compute KPIs across replications
    n = len(rep_results)
    avg_waits = [np.mean(r['waits']) if r['waits'] else 0.0 for r in rep_results]
    median_waits = [np.median(r['waits']) if r['waits'] else 0.0 for r in rep_results]
    p90_waits = [np.percentile(r['waits'], 90) if r['waits'] else 0.0 for r in rep_results]
    total_walks = [sum(r['walks']) for r in rep_results]
    total_passengers = [len(r['walks']) for r in rep_results]
    avg_total_travel = []
    for r in rep_results:
        travel_times = []
        for w, walk in zip(r['waits'], r['walks'][:len(r['waits'])]):
            travel_times.append(w + walk + in_vehicle_time_s)
        avg_total_travel.append(np.mean(travel_times) if travel_times else 0.0)

    summary = {
        'n_reps': n,
        'avg_wait_mean': float(np.mean(avg_waits)),
        'avg_wait_ci': list(np.percentile(avg_waits, [2.5, 97.5])),
        'median_wait_mean': float(np.mean(median_waits)),
        'p90_wait_mean': float(np.mean(p90_waits)),
        'total_walk_mean': float(np.mean(total_walks)),
        'total_walk_ci': list(np.percentile(total_walks, [2.5,97.5])),
        'avg_total_travel_mean': float(np.mean(avg_total_travel)),
        'avg_total_travel_ci': list(np.percentile(avg_total_travel, [2.5,97.5])),
        'mean_boarded': float(np.mean([r['boarded_total'] for r in rep_results])),
        'mean_remaining_queue': float(np.mean([r['remaining_queue'] for r in rep_results])),
        'mean_dwell': float(np.mean([np.mean(r['dwell_times']) if r['dwell_times'] else 0.0 for r in rep_results])),
    }
    return summary


def plot_summary(summaries: Dict[str, Any], out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    # bar chart of avg wait
    names = list(summaries.keys())
    vals = [summaries[n]['avg_wait_mean'] for n in names]
    plt.figure()
    plt.bar(names, vals)
    plt.ylabel('Avg wait (s)')
    plt.title('Average wait by scenario')
    plt.savefig(os.path.join(out_dir, 'avg_wait_by_scenario.png'))
    plt.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input-csv', default=os.path.join(os.path.dirname(__file__), '..', '..', 'monitor_outputs_1hr', 'monitor_summary_both_20251105_070549.csv'))
    p.add_argument('--stop-ids', nargs=2, required=False,
                   help='Two queried_stop_id values to simulate (default picks first two in CSV)')
    p.add_argument('--rate', type=float, default=0.5, help='passenger arrival rate per stop (per minute)')
    p.add_argument('--capacity', type=int, default=70)
    p.add_argument('--base-dwell', type=float, default=10.0)
    p.add_argument('--alpha', type=float, default=2.0)
    p.add_argument('--walk-post2', type=int, default=120, help='walk time (s) for post-merge2')
    p.add_argument('--short-walk', type=int, default=60, help='short walk time (s) used in post1 half')
    p.add_argument('--long-walk', type=int, default=180, help='long walk time (s) used in post1 half')
    p.add_argument('--half-prob', type=float, default=0.5, help='probability of being short-walk in post1')
    p.add_argument('--replications', type=int, default=200)
    p.add_argument('--horizon-min', type=int, default=120)
    p.add_argument('--out-dir', default=os.path.join(os.path.dirname(__file__), '..', 'simulation_results'))
    args = p.parse_args()

    df_all = pd.read_csv(args.input_csv)
    # default stop ids: pick top two unique queried_stop_id
    stops = args.stop_ids if args.stop_ids else list(df_all['queried_stop_id'].unique())[:2]
    print('Using stop ids:', stops)

    env_start, schedules = load_eta_schedules(args.input_csv, stops, horizon_min=args.horizon_min)
    print('Env start at', env_start.isoformat())

    # load in-vehicle baseline from previous travel_time_summary if present
    tt_json = os.path.join(os.path.dirname(__file__), '..', 'travel_time_comparison', 'travel_time_summary.json')
    if os.path.exists(tt_json):
        with open(tt_json) as fh:
            j = json.load(fh)
            # use peak mean if available else offpeak
            in_vehicle = j.get('summary', {}).get('peak', {}).get('mean_s') or j.get('summary', {}).get('offpeak', {}).get('mean_s') or 80.0
    else:
        in_vehicle = 80.0

    horizon_seconds = args.horizon_min * 60

    scenarios = ['pre', 'post1', 'post2']
    rng = np.random.default_rng(seed=12345)

    os.makedirs(args.out_dir, exist_ok=True)
    replications = max(1, args.replications)

    full_summaries = {}

    for scenario in scenarios:
        rep_results = []
        # for speed: if many replications, run smaller pilot first
        for r in range(replications):
            rep = run_one_replication(schedules, scenario, args.rate, args.capacity, args.base_dwell, args.alpha,
                                      args.walk_post2, args.short_walk, args.long_walk, args.half_prob,
                                      in_vehicle, horizon_seconds, rng)
            rep_results.append(rep)
        summary = summarize_replications(rep_results, in_vehicle)
        full_summaries[scenario] = summary
        # write per-scenario JSON
        with open(os.path.join(args.out_dir, f'summary_{scenario}.json'), 'w') as fh:
            json.dump({'scenario': scenario, 'summary': summary}, fh, indent=2)

    # plots
    plot_summary(full_summaries, args.out_dir)
    # write overall
    with open(os.path.join(args.out_dir, 'summaries_all.json'), 'w') as fh:
        json.dump(full_summaries, fh, indent=2)

    print('Wrote results to', args.out_dir)


if __name__ == '__main__':
    main()
