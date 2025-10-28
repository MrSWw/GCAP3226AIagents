#!/usr/bin/env python3
"""
Run SimPy simulations using data pre-extracted into `kmb_extracted.json`.

Usage examples:
  python3 sim_from_extracted.py --stations "St. Martin" "CHONG SAN ROAD"
  python3 sim_from_extracted.py --stop-ids 3F24CFF9046300D9

The script will load ETA rows from the extracted JSON and, for each requested
station/stop, build an arrival schedule and run a short SimPy simulation.
"""
import argparse
import json
import os
import datetime
from dateutil import parser as dateparser
import simpy
import numpy as np

# reuse StopSimulation and build_schedule_from_eta logic by copying the
# minimal required implementation here to avoid import coupling.


def build_schedule_from_rows(rows, now: datetime.datetime, horizon_min: int = 120):
    schedule = []
    horizon_dt = now + datetime.timedelta(minutes=horizon_min)
    for row in rows:
        eta = row.get('eta')
        if not eta:
            continue
        try:
            eta_dt = dateparser.parse(eta)
        except Exception:
            continue
        if eta_dt < now:
            continue
        if eta_dt > horizon_dt:
            continue
        schedule.append({'when': eta_dt, 'route': row.get('route'), 'dir': row.get('direction') or row.get('dir'), 'raw': row})
    schedule.sort(key=lambda x: x['when'])
    return schedule


class StopSimulation:
    def __init__(self, env: simpy.Environment, schedule, passenger_rate_per_min: float = 0.5, bus_capacity: int = 70):
        self.env = env
        self.schedule = schedule
        self.passenger_rate = passenger_rate_per_min
        self.bus_capacity = bus_capacity
        self.queue = 0
        self.wait_times = []
        self.boarded_total = 0
        self.passenger_arrival_times = []

    def passenger_generator(self):
        while True:
            if self.passenger_rate <= 0:
                yield self.env.timeout(60)
                continue
            mean_min = 1.0 / self.passenger_rate
            isi = np.random.exponential(mean_min) * 60.0
            yield self.env.timeout(isi)
            self.queue += 1
            self.passenger_arrival_times.append(self.env.now)

    def bus_process(self, when_dt: datetime.datetime):
        yield self.env.timeout((when_dt - self.env.real_now).total_seconds())
        arriving = min(self.queue, self.bus_capacity)
        now = self.env.now
        for _ in range(arriving):
            if self.passenger_arrival_times:
                t_arr = self.passenger_arrival_times.pop(0)
                self.wait_times.append(now - t_arr)
        self.queue -= arriving
        self.boarded_total += arriving

    def run(self, until_seconds: int):
        self.env.real_now = datetime.datetime.now(datetime.timezone.utc).astimezone()
        self.env.process(self.passenger_generator())
        for ev in self.schedule:
            self.env.process(self.bus_process(ev['when']))
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
    p.add_argument('--stations', nargs='*', help='Station names to simulate (as in kmb_extracted.json)')
    p.add_argument('--stop-ids', nargs='*', help='Stop IDs to simulate (use extracted stop ids)')
    p.add_argument('--horizon', type=int, default=120, help='Horizon minutes for schedule')
    p.add_argument('--rate', type=float, default=0.5, help='Passenger arrival rate per minute')
    p.add_argument('--capacity', type=int, default=70, help='Bus capacity')
    args = p.parse_args()

    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'kmb_extracted.json')
    if not os.path.exists(data_path):
        print('Extracted data not found:', data_path)
        return
    with open(data_path, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    print('Now:', now.isoformat())

    # filter rows by requested stations or stop ids
    groups = {}
    if args.stop_ids:
        for sid in args.stop_ids:
            groups[sid] = [r for r in rows if r.get('stop_id') == sid]
    else:
        if not args.stations:
            print('Please provide --stations or --stop-ids')
            return
        for st in args.stations:
            groups[st] = [r for r in rows if (r.get('station') or '').lower() == st.lower()]

    for name, group_rows in groups.items():
        print(f"\n{name}: found {len(group_rows)} extracted rows")
        # build schedule from rows
        schedule = build_schedule_from_rows(group_rows, now, horizon_min=args.horizon)
        print(f'  Built schedule with {len(schedule)} arrivals within {args.horizon} minutes')
        if not schedule:
            print('  No upcoming ETAs found — skipping simulation for this group')
            continue

        env = simpy.Environment()
        sim = StopSimulation(env, schedule, passenger_rate_per_min=args.rate, bus_capacity=args.capacity)
        env.real_now = now
        horizon_seconds = args.horizon * 60
        sim.run(until_seconds=horizon_seconds)
        summarize(sim)


if __name__ == '__main__':
    main()
