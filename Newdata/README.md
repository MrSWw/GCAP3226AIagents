# 23 November Data Collection

**Start Date**: November 23, 2025  
**Duration**: 96 hours (4 days)  
**End Date**: November 27, 2025

---

## 📁 Files in This Directory

### CSV Files

- **`monitor_hour_XX_YYYYMMDD_HHMMSS.csv`** - Hourly CSV files containing all ETA records collected during that hour
- **`monitor_summary_YYYYMMDD_HHMMSS.csv`** - Final consolidated CSV with all data (created at end)

### Log File

- **`monitoring_log.txt`** - Continuous log file updated every snapshot with:
  - Timestamp of each snapshot
  - Progress updates (every 10 snapshots)
  - Hourly CSV save confirmations
  - Route counts and record statistics
  - Final summary statistics

---

## 📊 Data Collection Details

- **Stops Monitored**:
  - St. Martin Road (PA206): `3F24CFF9046300D9`
  - Chong San Road (PA212): `B34F59A0270AEDA4`

- **Routes Monitored** (19 routes, Outbound direction only):
  - 272A, 272X, 271B, 274, 274P, 65X, 82D, 900, 64X
  - 74D, 74P, 96, A47X, NA47, 272P, 900X, 907D, 263C, 73D

- **Settings**:
  - Polling interval: 30 seconds
  - Look-ahead horizon: 60 minutes
  - Direction filter: Outbound (O) only

---

## 📝 Log File Format

The log file (`monitoring_log.txt`) is continuously updated with entries like:

```
[2025-11-23 23:26:35] ======================================================================
[2025-11-23 23:26:35] MONITORING SESSION STARTED
[2025-11-23 23:26:35] ======================================================================
[2025-11-23 23:26:35] Starting monitoring: ['3F24CFF9046300D9', 'B34F59A0270AEDA4']
[2025-11-23 23:26:35] Provider: kmb | Duration: 5760 minutes | Interval: 30s
[2025-11-23 23:26:40] Snapshot 10 | Elapsed: 0.1min | Remaining: 5759.9min | Total records: 45 | Routes: 3
[2025-11-23 23:27:40] Hour 1 CSV saved: monitor_hour_01_20251123_232740.csv | Routes: 5 | Records: 120
```

---

## 🔍 View Live Data

### View Live Log:
```bash
tail -f monitoring_log.txt
```

### Check Latest CSV:
```bash
ls -lt *.csv | head -1
```

### Count Records in Latest CSV:
```bash
wc -l monitor_hour_*.csv | tail -1
```

---

## 📈 Expected Data Volume

- **Duration**: 96 hours = 5,760 minutes
- **Interval**: 30 seconds
- **Expected snapshots**: ~11,520 snapshots
- **Expected hourly CSV files**: ~96 files
- **Expected total records**: Varies by route activity

---

*Directory created: November 23, 2025*

