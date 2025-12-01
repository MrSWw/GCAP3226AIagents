#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import csv


def parse_iso_ts(s: str) -> datetime:
    # Normalize to offset-aware (+08:00) if missing timezone
    dt = None
    try:
        dt = datetime.fromisoformat(s)
    except Exception:
        # Fallback: strip trailing timezone then parse
        if "+" in s:
            s = s.split("+")[0]
        dt = datetime.fromisoformat(s)
    # If naive, assume Asia/Hong_Kong (+08:00) by adding offset
    if dt.tzinfo is None:
        # append +08:00 by re-parsing with suffix
        try:
            dt = datetime.fromisoformat(s + "+08:00")
        except Exception:
            pass
    return dt


def load_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def within_window(ts: datetime, start: datetime, end: datetime) -> bool:
    # Align timezone awareness: if any is naive, coerce to same offset as start
    if start.tzinfo and ts.tzinfo is None:
        ts = ts.replace(tzinfo=start.tzinfo)
    if end.tzinfo and ts.tzinfo is None:
        ts = ts.replace(tzinfo=end.tzinfo)
    return start <= ts <= end


def sec_diff(later: datetime, earlier: datetime) -> float:
    return (later - earlier).total_seconds()


def summarize(input_csv: Path, out_csv: Path, out_md: Path, start_ts: str, end_ts: str):
    start = parse_iso_ts(start_ts)
    end = parse_iso_ts(end_ts)

    # Aggregations keyed by (stop_id, route)
    agg = {}

    for row in load_rows(input_csv):
        try:
            snapshot_ts = parse_iso_ts(row.get("snapshot_ts", ""))
        except Exception:
            continue
        if not within_window(snapshot_ts, start, end):
            continue

        stop_id = row.get("queried_stop_id", "")
        route = row.get("route", "")
        direction = row.get("direction", "")
        if direction and direction != "O":
            # only outbound (as per collection settings)
            continue
        eta_str = row.get("eta", "")
        eta_seq = row.get("eta_seq", "")
        if not eta_str:
            continue
        try:
            eta = parse_iso_ts(eta_str)
        except Exception:
            continue

        key = (stop_id, route)
        a = agg.get(key)
        if a is None:
            a = {
                "stop_id": stop_id,
                "route": route,
                "snapshots": 0,
                "wait_samples_sec": [],  # eta_seq=1 only
                "headway_samples_sec": [],  # seq2 - seq1 when both present in same snapshot
                "first_eta": None,
                "last_eta": None,
                "first_snapshot": None,
                "last_snapshot": None,
            }
            agg[key] = a

        a["snapshots"] += 1
        # update first/last eta and snapshot
        if a["first_snapshot"] is None or snapshot_ts < a["first_snapshot"]:
            a["first_snapshot"] = snapshot_ts
        if a["last_snapshot"] is None or snapshot_ts > a["last_snapshot"]:
            a["last_snapshot"] = snapshot_ts
        if a["first_eta"] is None or eta < a["first_eta"]:
            a["first_eta"] = eta
        if a["last_eta"] is None or eta > a["last_eta"]:
            a["last_eta"] = eta

        # wait time sample for seq=1
        try:
            seq_val = int(eta_seq)
        except Exception:
            seq_val = None

        if seq_val == 1:
            a["wait_samples_sec"].append(sec_diff(eta, snapshot_ts))

        # For headway, we need seq1 & seq2 in same snapshot: collect per-snapshot temporary
        snap_key = (key, snapshot_ts)
        # Store minimal info in a lightweight cache inside agg
        cache = a.setdefault("_snap_cache", {})
        snap = cache.get(snap_key)
        if snap is None:
            snap = {}
            cache[snap_key] = snap
        snap[seq_val] = eta

    # Compute headways from cached seq1 & seq2 in same snapshots
    for key, a in agg.items():
        cache = a.get("_snap_cache", {})
        for (k, snap_ts), snap in cache.items():
            eta1 = snap.get(1)
            eta2 = snap.get(2)
            if eta1 and eta2:
                a["headway_samples_sec"].append(sec_diff(eta2, eta1))
        # remove cache to avoid bloating output
        if "_snap_cache" in a:
            del a["_snap_cache"]

    # Write CSV summary
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "stop_id",
            "route",
            "snapshots",
            "wait_mean_sec",
            "wait_median_sec",
            "wait_min_sec",
            "wait_max_sec",
            "headway_mean_sec",
            "headway_median_sec",
            "headway_min_sec",
            "headway_max_sec",
            "first_snapshot",
            "last_snapshot",
        ])

        def stats(arr):
            if not arr:
                return ("", "", "", "")
            arr_sorted = sorted(arr)
            n = len(arr_sorted)
            mean = sum(arr_sorted) / n
            median = arr_sorted[n // 2] if n % 2 == 1 else (arr_sorted[n // 2 - 1] + arr_sorted[n // 2]) / 2
            return (round(mean, 2), round(median, 2), round(arr_sorted[0], 2), round(arr_sorted[-1], 2))

        for (stop_id, route), a in sorted(agg.items()):
            wait_mean, wait_median, wait_min, wait_max = stats(a["wait_samples_sec"])
            head_mean, head_median, head_min, head_max = stats(a["headway_samples_sec"])
            w.writerow([
                stop_id,
                route,
                a["snapshots"],
                wait_mean,
                wait_median,
                wait_min,
                wait_max,
                head_mean,
                head_median,
                head_min,
                head_max,
                a["first_snapshot"].isoformat() if a["first_snapshot"] else "",
                a["last_snapshot"].isoformat() if a["last_snapshot"] else "",
            ])

    # Write Markdown summary (top lines and notes)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf8") as f:
        f.write(f"# Peak Hour Summary ({start_ts} to {end_ts})\n\n")
        f.write("This report summarizes outbound wait times (eta_seq=1) and headways (seq2 - seq1) per stop/route.\n\n")
        f.write("## Key Metrics\n")
        f.write("- wait_mean_sec: average of (ETA - snapshot_ts) for eta_seq=1\n")
        f.write("- headway_mean_sec: average of (eta_seq=2 - eta_seq=1) when both exist in same snapshot\n\n")
        f.write("## Top Routes by Mean Wait (eta_seq=1)\n\n")

        # Build quick ranking
        ranking = []
        for (stop_id, route), a in agg.items():
            arr = a["wait_samples_sec"]
            if arr:
                mean = sum(arr) / len(arr)
                ranking.append((mean, stop_id, route))
        ranking.sort(reverse=True)
        for mean, stop_id, route in ranking[:20]:
            f.write(f"- {stop_id} {route}: {round(mean,2)} sec\n")

        f.write("\nFor complete data, see the CSV summary.\n")


def main():
    ap = argparse.ArgumentParser(description="Generate peak hour summary from realtime_monitoring.csv")
    ap.add_argument("--input", type=str, default="/workspaces/GCAP3226AIagents/Newdata/realtime_monitoring.csv")
    ap.add_argument("--start", type=str, default="2025-11-24T06:30:00+08:00")
    ap.add_argument("--end", type=str, default="2025-11-24T08:30:00+08:00")
    ap.add_argument("--out-csv", type=str, default="/workspaces/GCAP3226AIagents/Newdata/peak_summary_20251124_0630_0830.csv")
    ap.add_argument("--out-md", type=str, default="/workspaces/GCAP3226AIagents/Newdata/peak_summary_20251124_0630_0830.md")
    args = ap.parse_args()

    summarize(
        input_csv=Path(args.input),
        out_csv=Path(args.out_csv),
        out_md=Path(args.out_md),
        start_ts=args.start,
        end_ts=args.end,
    )


if __name__ == "__main__":
    main()
