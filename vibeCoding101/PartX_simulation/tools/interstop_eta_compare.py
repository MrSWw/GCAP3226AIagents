#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime, time
from pathlib import Path
import csv


def parse_iso_ts(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s)
    except Exception:
        if "+" in s:
            s = s.split("+")[0]
        return datetime.fromisoformat(s)


def is_peak(dt: datetime, peak_ranges: list[tuple[time, time]]) -> bool | None:
    """Returns True for peak, False for off-peak, None if outside analysis window"""
    t = dt.time()
    for start, end in peak_ranges:
        if start <= t <= end:
            return True
    return False

def is_in_analysis_window(dt: datetime, offpeak_ranges: list[tuple[time, time]], peak_ranges: list[tuple[time, time]]) -> bool:
    """Check if time is within either peak or off-peak analysis windows"""
    t = dt.time()
    for start, end in offpeak_ranges:
        if start <= t <= end:
            return True
    for start, end in peak_ranges:
        if start <= t <= end:
            return True
    return False


def parse_peak_ranges(s: str) -> list[tuple[time, time]]:
    # format: "06:30-08:30,17:00-19:00"
    out = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        a, b = part.split("-")
        ah, am = map(int, a.split(":"))
        bh, bm = map(int, b.split(":"))
        out.append((time(ah, am), time(bh, bm)))
    return out


def load_rows(csv_path: Path):
    with csv_path.open("r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def analyze(input_csv: Path, stop1: str, stop2: str, peak_ranges: list[tuple[time, time]], offpeak_ranges: list[tuple[time, time]], out_csv: Path, out_md: Path):
    # Build per snapshot+route map for quick pairing
    # key: (snapshot_ts, route) -> {stop_id: {seq: eta_dt}}
    data = {}
    for row in load_rows(input_csv):
        try:
            snap = parse_iso_ts(row.get("snapshot_ts", ""))
        except Exception:
            continue
        # Filter: only include times within analysis windows
        if not is_in_analysis_window(snap, offpeak_ranges, peak_ranges):
            continue
        route = row.get("route", "")
        direction = row.get("direction", "")
        if direction and direction != "O":
            continue
        stop_id = row.get("queried_stop_id", "")
        if stop_id not in (stop1, stop2):
            continue
        eta_str = row.get("eta", "")
        if not eta_str:
            continue
        try:
            eta = parse_iso_ts(eta_str)
        except Exception:
            continue
        try:
            seq = int(row.get("eta_seq", ""))
        except Exception:
            seq = None
        if seq is None:
            continue

        key = (snap, route)
        m = data.get(key)
        if m is None:
            m = {}
            data[key] = m
        sm = m.get(stop_id)
        if sm is None:
            sm = {}
            m[stop_id] = sm
        sm[seq] = eta

    # Pair stop1 and stop2 by same snapshot, same route, same seq
    rows = []
    for (snap, route), m in data.items():
        s1 = m.get(stop1, {})
        s2 = m.get(stop2, {})
        for seq in set(s1.keys()).intersection(s2.keys()):
            eta1 = s1[seq]
            eta2 = s2[seq]
            # Estimated inter-stop travel time at this snapshot (seconds)
            travel_sec = (eta2 - eta1).total_seconds()
            # Filter negative travel times (data anomalies)
            if travel_sec < 0:
                continue
            rows.append({
                "snapshot_ts": snap.isoformat(),
                "route": route,
                "seq": seq,
                "stop1_eta": eta1.isoformat(),
                "stop2_eta": eta2.isoformat(),
                "travel_sec": travel_sec,
                "peak_or_offpeak": "peak" if is_peak(snap, peak_ranges) else "off-peak",
            })

    # Aggregate per route & peak/off-peak
    agg = {}
    for r in rows:
        key = (r["route"], r["peak_or_offpeak"])
        a = agg.get(key)
        if a is None:
            a = {"count": 0, "vals": []}
            agg[key] = a
        a["count"] += 1
        a["vals"].append(r["travel_sec"])

    def stats(vals):
        if not vals:
            return ("", "", "", "")
        s = sorted(vals)
        n = len(s)
        mean = sum(s) / n
        med = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2
        return (round(mean, 2), round(med, 2), round(s[0], 2), round(s[-1], 2))

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["route", "peak_or_offpeak", "samples", "travel_mean_sec", "travel_median_sec", "travel_min_sec", "travel_max_sec"])
        for (route, label), a in sorted(agg.items()):
            mean, med, mn, mx = stats(a["vals"])
            w.writerow([route, label, a["count"], mean, med, mn, mx])

    with out_md.open("w", encoding="utf8") as f:
        f.write("# Inter-stop ETA Comparison (Daytime Only)\n\n")
        f.write("This compares estimated inter-stop travel time between stop1 and stop2 by subtracting ETA at stop1 from ETA at stop2 at the same snapshot and sequence.\n\n")
        f.write("**Analysis windows**: Peak vs daytime off-peak only (excludes nighttime)\n")
        f.write("**Note**: Negative travel times (data anomalies) have been filtered out\n\n")
        f.write("## Peak vs Off-peak Summary\n\n")
        for (route, label), a in sorted(agg.items()):
            mean, med, mn, mx = stats(a["vals"])
            f.write(f"- {route} [{label}]: mean={mean}s median={med}s min={mn}s max={mx}s (n={a['count']})\n")
        
        # Add congestion impact analysis
        f.write("\n## Congestion Impact (Peak vs Off-peak)\n\n")
        routes = set(r for (r, _) in agg.keys())
        impact = []
        for route in sorted(routes):
            peak_vals = agg.get((route, "peak"), {}).get("vals", [])
            offpeak_vals = agg.get((route, "off-peak"), {}).get("vals", [])
            if peak_vals and offpeak_vals:
                peak_med = sorted(peak_vals)[len(peak_vals)//2]
                offpeak_med = sorted(offpeak_vals)[len(offpeak_vals)//2]
                if offpeak_med > 0:
                    pct_increase = ((peak_med - offpeak_med) / offpeak_med) * 100
                    diff_sec = peak_med - offpeak_med
                    impact.append((pct_increase, route, peak_med, offpeak_med, diff_sec))
        
        impact.sort(reverse=True)
        for pct, route, p_med, o_med, diff in impact:
            f.write(f"- **{route}**: {pct:+.1f}% ({o_med:.0f}s → {p_med:.0f}s, diff: {diff:+.0f}s)\n")


def main():
    ap = argparse.ArgumentParser(description="Compare inter-stop ETA travel time for two stops and summarize peak vs off-peak")
    ap.add_argument("--input", type=str, default="/workspaces/GCAP3226AIagents/Newdata/realtime_monitoring.csv")
    ap.add_argument("--stop1", type=str, default="3F24CFF9046300D9")
    ap.add_argument("--stop2", type=str, default="B34F59A0270AEDA4")
    ap.add_argument("--peak-ranges", type=str, default="06:30-08:30")
    ap.add_argument("--offpeak-ranges", type=str, default="08:30-09:21", help="Daytime off-peak ranges (post morning peak)")
    ap.add_argument("--out-csv", type=str, default="/workspaces/GCAP3226AIagents/Newdata/interstop_peak_vs_offpeak.csv")
    ap.add_argument("--out-md", type=str, default="/workspaces/GCAP3226AIagents/Newdata/interstop_peak_vs_offpeak.md")
    args = ap.parse_args()

    peak_ranges = parse_peak_ranges(args.peak_ranges)
    offpeak_ranges = parse_peak_ranges(args.offpeak_ranges)
    analyze(
        input_csv=Path(args.input),
        stop1=args.stop1,
        stop2=args.stop2,
        peak_ranges=peak_ranges,
        offpeak_ranges=offpeak_ranges,
        out_csv=Path(args.out_csv),
        out_md=Path(args.out_md),
    )


if __name__ == "__main__":
    main()
