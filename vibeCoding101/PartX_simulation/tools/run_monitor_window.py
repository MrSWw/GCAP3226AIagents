#!/usr/bin/env python3
"""
Run monitoring (HTTP GET or file snapshot) repeatedly between a specified start and end time
in a given local timezone (default Asia/Hong_Kong). Saves snapshots into a timestamped
output folder under `monitor_outputs_{date}`.

Example (run for 24 Nov 2025, 06:30-08:30 HKT, polling every 60s):

python tools/run_monitor_window.py \
  --date 2025-11-24 --start 06:30 --end 08:30 \
  --mode http --url "https://example.com/eta_snapshot" \
  --interval 60

Or to use a local CSV as a test snapshot source (mode=file):

python tools/run_monitor_window.py --date 2025-11-24 --start 06:30 --end 08:30 \
  --mode file --file-path presentation/simulation/all_etas_now_until_0930.csv --interval 60

The script will wait until the start time if invoked earlier, or run immediately if current time
is within the window. Uses system timezone awareness via `zoneinfo` (Python 3.9+).
"""

from __future__ import annotations
import argparse
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
import time as time_module
from pathlib import Path
import sys
import requests
import shutil
import json
from typing import List


def parse_hhmm(s: str) -> time:
    try:
        hh, mm = s.split(":")
        return time(int(hh), int(mm))
    except Exception:
        raise argparse.ArgumentTypeError(f"Invalid time format: {s}. Use HH:MM")


def now_tz(tz: ZoneInfo) -> datetime:
    return datetime.now(tz)


def ensure_out_dir(base: Path, dt: date) -> Path:
    name = f"monitor_outputs_{dt.isoformat()}"
    out = base / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def save_response(resp: requests.Response, out_dir: Path, prefix: str, idx: int) -> Path:
    content_type = resp.headers.get("Content-Type", "")
    ts = datetime.now().astimezone().isoformat().replace(':', '-')
    if "json" in content_type:
        p = out_dir / f"{prefix}_{ts}_{idx}.json"
        with p.open("w", encoding="utf8") as f:
            json.dump(resp.json(), f, ensure_ascii=False, indent=2)
    elif "csv" in content_type or resp.text.startswith("stop_id"):
        p = out_dir / f"{prefix}_{ts}_{idx}.csv"
        p.write_text(resp.text, encoding="utf8")
    else:
        # default to raw
        p = out_dir / f"{prefix}_{ts}_{idx}.txt"
        p.write_bytes(resp.content)
    return p


def copy_file_snapshot(src: Path, out_dir: Path, prefix: str, idx: int) -> Path:
    ts = datetime.now().astimezone().isoformat().replace(':', '-')
    dst = out_dir / f"{prefix}_{ts}_{idx}{src.suffix}"
    shutil.copy(src, dst)
    return dst


def run_monitor_window(
    target_date: date,
    start_time: time,
    end_time: time,
    tz_name: str,
    interval: int,
    mode: str,
    urls: List[str],
    file_path: str | None,
    out_base: Path,
    timeout: int,
):
    tz = ZoneInfo(tz_name)
    # build start/end datetimes in tz
    start_dt = datetime.combine(target_date, start_time).replace(tzinfo=tz)
    end_dt = datetime.combine(target_date, end_time).replace(tzinfo=tz)
    now = now_tz(tz)

    if end_dt <= start_dt:
        raise SystemExit("End time must be after start time")

    out_dir = ensure_out_dir(out_base, target_date)
    log_file = out_dir / "monitor_log.csv"
    if not log_file.exists():
        log_file.write_text("snapshot_ts,mode,item,filepath,status,notes\n", encoding="utf8")

    print(f"Monitoring window: {start_dt.isoformat()} -> {end_dt.isoformat()} ({tz_name})")
    # wait until start if necessary
    if now < start_dt:
        wait_secs = (start_dt - now).total_seconds()
        print(f"Current time {now.isoformat()} before start; sleeping {int(wait_secs)} seconds until start.")
        try:
            time_module.sleep(wait_secs)
        except KeyboardInterrupt:
            print("Interrupted while waiting for start; exiting.")
            return

    # run until end
    idx = 0
    while True:
        now = now_tz(tz)
        if now >= end_dt:
            print("Reached end of window; exiting.")
            break

        snapshot_ts = now.isoformat()
        print(f"[{snapshot_ts}] Taking snapshot (mode={mode}) idx={idx}")
        saved_paths = []
        if mode == "http":
            if not urls:
                print("No URLs provided for http mode; skipping this iteration.")
            else:
                for i, u in enumerate(urls):
                    try:
                        resp = requests.get(u, timeout=timeout)
                        p = save_response(resp, out_dir, prefix="http", idx=i)
                        saved_paths.append(p)
                        log_file.write_text(f"{snapshot_ts},http,{u},{p},{resp.status_code},OK\n", encoding="utf8", append=False) if False else None
                        # append to file
                        with log_file.open("a", encoding="utf8") as lf:
                            lf.write(f"{snapshot_ts},http,{u},{p},{resp.status_code},OK\n")
                    except Exception as e:
                        with log_file.open("a", encoding="utf8") as lf:
                            lf.write(f"{snapshot_ts},http,{u},,ERROR,{str(e)}\n")
                        print(f"Failed to GET {u}: {e}")
        elif mode == "file":
            if not file_path:
                print("No --file-path provided for file mode; skipping.")
            else:
                src = Path(file_path)
                if not src.exists():
                    print(f"Source file does not exist: {src}; skipping.")
                    with log_file.open("a", encoding="utf8") as lf:
                        lf.write(f"{snapshot_ts},file,{src},,ERROR,not_found\n")
                else:
                    try:
                        p = copy_file_snapshot(src, out_dir, prefix="file", idx=idx)
                        saved_paths.append(p)
                        with log_file.open("a", encoding="utf8") as lf:
                            lf.write(f"{snapshot_ts},file,{src},{p},OK,copied\n")
                    except Exception as e:
                        with log_file.open("a", encoding="utf8") as lf:
                            lf.write(f"{snapshot_ts},file,{src},,ERROR,{str(e)}\n")
                        print(f"Failed to copy {src}: {e}")
        else:
            print(f"Unknown mode: {mode}; supported: http, file")

        idx += 1
        # compute sleep until next interval but ensure we don't overshoot end_dt
        now = now_tz(tz)
        next_time = now + timedelta(seconds=interval)
        if next_time > end_dt:
            # sleep only until end
            sleep_secs = max(0, (end_dt - now).total_seconds())
        else:
            sleep_secs = interval
        if sleep_secs > 0:
            try:
                time_module.sleep(sleep_secs)
            except KeyboardInterrupt:
                print("Interrupted by user; exiting.")
                break

    print(f"Monitoring completed. Outputs in: {out_dir}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Run monitoring between start/end time in local TZ and save snapshots.")
    p.add_argument("--date", type=str, default=None, help="Target date YYYY-MM-DD (default: tomorrow)")
    p.add_argument("--start", type=parse_hhmm, default=parse_hhmm("06:30"), help="Start time HH:MM (local tz)")
    p.add_argument("--end", type=parse_hhmm, default=parse_hhmm("08:30"), help="End time HH:MM (local tz)")
    p.add_argument("--tz", type=str, default="Asia/Hong_Kong", help="Timezone name, e.g. Asia/Hong_Kong")
    p.add_argument("--interval", type=int, default=60, help="Polling interval in seconds")
    p.add_argument("--mode", type=str, default="file", choices=("http", "file"), help="Snapshot mode: http or file")
    p.add_argument("--url", action="append", help="URL to GET (repeatable). Used with --mode http")
    p.add_argument("--file-path", type=str, help="Local file to copy for file-mode snapshots (used for testing)")
    p.add_argument("--out-base", type=str, default=".", help="Base folder to write monitor_outputs_{date}")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")

    args = p.parse_args(argv)

    if args.date is None:
        # default to tomorrow in local tz
        tz = ZoneInfo(args.tz)
        tomorrow = (datetime.now(tz) + timedelta(days=1)).date()
        target_date = tomorrow
    else:
        target_date = datetime.fromisoformat(args.date).date()

    out_base = Path(args.out_base)

    run_monitor_window(
        target_date=target_date,
        start_time=args.start,
        end_time=args.end,
        tz_name=args.tz,
        interval=args.interval,
        mode=args.mode,
        urls=args.url or [],
        file_path=args.file_path,
        out_base=out_base,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
