#!/usr/bin/env python3
"""Simulate KMB traffic at named stops using etabus KMB APIs.

This script will:
- find stop IDs matching provided stop names (case-insensitive)
- fetch stop ETA data for those stops
- build an arrival schedule from ETAs and run a SimPy simulation where
  passengers arrive (Poisson) and board arriving buses up to capacity

Outputs a short summary of average wait times and boardings.
"""
from __future__ import annotations
import argparse
import requests
import datetime
import time
from dateutil import parser as dateparser
import simpy
import numpy as np
import pandas as pd
from typing import List, Dict, Any

BASES = {
    'kmb': 'https://data.etabus.gov.hk',
    'citybus': 'https://rt.data.gov.hk'
}

def fetch_stop_list(provider: str = 'kmb') -> List[Dict[str, Any]]:
    if provider == 'kmb':
        url = BASES['kmb'] + '/v1/transport/kmb/stop'
    else:
        url = BASES['citybus'] + '/v1/transport/citybus-nwfb/stop'
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    j = r.json()
    # j['data'] expected
    return j.get('data', [])

def find_stops_by_name(names: List[str], provider: str = 'kmb') -> Dict[str, List[Dict[str,Any]]]:
    stops = fetch_stop_list(provider=provider)
    out = {n: [] for n in names}
    for s in stops:
        name_en = (s.get('name_en') or '').lower()
        name_tc = (s.get('name_tc') or '').lower()
        name_sc = (s.get('name_sc') or '').lower()
        for n in names:
            key = n.lower()
            if key in name_en or key in name_tc or key in name_sc:
                out[n].append(s)
    return out

def fetch_stop_eta(stop_id: str, provider: str = 'kmb') -> List[Dict[str,Any]]:
    if provider == 'kmb':
        url = f"{BASES['kmb']}/v1/transport/kmb/stop-eta/{stop_id}"
    else:
        url = f"{BASES['citybus']}/v1/transport/citybus-nwfb/stop-eta/{stop_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    j = r.json()
    return j.get('data', [])


def fetch_stop_by_id(stop_id: str, provider: str = 'kmb') -> Dict[str,Any]:
    """Fetch stop metadata by stop id."""
    if provider == 'kmb':
        url = f"{BASES['kmb']}/v1/transport/kmb/stop/{stop_id}"
    else:
        url = f"{BASES['citybus']}/v1/transport/citybus-nwfb/stop/{stop_id}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    j = r.json()
    return j.get('data')

def build_schedule_from_eta(eta_rows: List[Dict[str,Any]], now: datetime.datetime, horizon_min: int=120) -> List[Dict[str,Any]]:
    schedule = []
    horizon_dt = now + datetime.timedelta(minutes=horizon_min)
    for row in eta_rows:
        eta = row.get('eta')
        if not eta:
            continue
        try:
            eta_dt = dateparser.parse(eta)
        except Exception:
            continue
        if eta_dt < now:
            # skip past arrivals
            continue
        if eta_dt > horizon_dt:
            continue
        schedule.append({
            'when': eta_dt,
            'route': row.get('route'),
            'service_type': row.get('service_type'),
            'dir': row.get('dir') or row.get('direction') or row.get('bound'),
            'raw': row,
        })
    schedule.sort(key=lambda x: x['when'])
    return schedule

class StopSimulation:
    def __init__(self, env: simpy.Environment, schedule: List[Dict[str,Any]], passenger_rate_per_min: float=0.5, bus_capacity:int=70):
        self.env = env
        self.schedule = schedule
        self.passenger_rate = passenger_rate_per_min
        self.bus_capacity = bus_capacity
        self.queue = 0
        self.wait_times = []
        self.boarded_total = 0
        # record arrival times of passengers for wait calculations
        self.passenger_arrival_times: List[float] = []

    def passenger_generator(self):
        # exponential interarrival (minutes -> seconds)
        while True:
            if self.passenger_rate <= 0:
                yield self.env.timeout(60)
                continue
            mean_min = 1.0 / self.passenger_rate
            isi = np.random.exponential(mean_min) * 60.0
            yield self.env.timeout(isi)
            self.queue += 1
            self.passenger_arrival_times.append(self.env.now)

    def bus_process(self, when_dt: datetime.datetime, info: Dict[str,Any]):
        # convert when_dt to env time (seconds from now)
        # assume env starts at time 0 mapped to real now
        yield self.env.timeout((when_dt - self.env.real_now).total_seconds())
        arriving = min(self.queue, self.bus_capacity)
        boarded = arriving
        # compute wait times for those boarded (FIFO)
        now = self.env.now
        for _ in range(boarded):
            if self.passenger_arrival_times:
                t_arr = self.passenger_arrival_times.pop(0)
                self.wait_times.append(now - t_arr)
        self.queue -= boarded
        self.boarded_total += boarded

    def run(self, until_seconds: int):
        # set attribute to map real now
        self.env.real_now = datetime.datetime.now(datetime.timezone.utc).astimezone()  # aware
        # start passenger generator
        self.env.process(self.passenger_generator())
        # schedule buses
        for ev in self.schedule:
            self.env.process(self.bus_process(ev['when'], ev))
        self.env.run(until=until_seconds)

def summarize(sim: StopSimulation):
    avg_wait = float(np.mean(sim.wait_times)) if sim.wait_times else 0.0
    median_wait = float(np.median(sim.wait_times)) if sim.wait_times else 0.0
    print('\nSimulation summary:')
    print(f'  Total boarded: {sim.boarded_total}')
    print(f'  Remaining queue: {sim.queue}')
    print(f'  Average wait (s): {avg_wait:.1f}')
    print(f'  Median wait (s): {median_wait:.1f}')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stops', nargs='+', help='Stop names to search (e.g. "St. Martin Road" "Chong San Road")')
    p.add_argument('--stop-ids', nargs='*', help='Stop IDs to use directly (bypass name search)')
    p.add_argument('--provider', choices=['kmb','citybus'], default='kmb', help='API provider to use (kmb or citybus)')
    p.add_argument('--horizon', type=int, default=120, help='Simulation horizon in minutes')
    p.add_argument('--rate', type=float, default=0.5, help='Passenger arrival rate (per minute)')
    p.add_argument('--capacity', type=int, default=70, help='Bus capacity')
    args = p.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    print(f'Now: {now.isoformat()}')

    matches = {}
    # If stop ids supplied, fetch each stop by id
    if args.stop_ids:
        for sid in args.stop_ids:
            try:
                s = fetch_stop_by_id(sid, provider=args.provider)
                if s:
                    matches[sid] = [s]
                else:
                    matches[sid] = []
            except Exception as e:
                print(f'Failed to fetch stop info for id {sid}:', e)
                matches[sid] = []
    else:
        if not args.stops:
            print('Please provide --stops or --stop-ids')
            return
        try:
            matches = find_stops_by_name(args.stops)
        except Exception as e:
            print('Failed to fetch stop list from API:', e)
            print('If network is blocked, obtain stop IDs manually and run simulation with --stop-ids option.')
            return

    for name, items in matches.items():
        print(f"\nFound {len(items)} matching stops for '{name}':")
        for i,s in enumerate(items[:5]):
            print(f"  {i+1}. {s.get('name_en')} / {s.get('name_tc')}  id={s.get('stop')} lat={s.get('lat')} long={s.get('long')}")
        if not items:
            print('  (no matches)')

    # For each stop, fetch ETA and run a separate short simulation
    for name, items in matches.items():
        if not items:
            continue
        # pick top match (first)
        stop = items[0]
        stop_id = stop.get('stop')
        print(f"\nFetching ETA for stop {stop_id} ({stop.get('name_en')})")
        try:
            etas = fetch_stop_eta(stop_id, provider=args.provider)
        except Exception as e:
            print('Failed to fetch stop ETA:', e)
            continue
        print(f'  Retrieved {len(etas)} ETA rows')
        schedule = build_schedule_from_eta(etas, now, horizon_min=args.horizon)
        print(f'  Built schedule with {len(schedule)} upcoming arrivals within {args.horizon} minutes')

        # convert schedule times to env times relative to now
        env = simpy.Environment()
        sim = StopSimulation(env, schedule, passenger_rate_per_min=args.rate, bus_capacity=args.capacity)
        # run for horizon in seconds
        horizon_seconds = args.horizon * 60
        # set env 'real_now' so bus_process can compute offsets
        env.real_now = now
        try:
            sim.run(until_seconds=horizon_seconds)
        except Exception as e:
            print('Simulation error:', e)
            continue
        summarize(sim)

if __name__ == '__main__':
    main()
