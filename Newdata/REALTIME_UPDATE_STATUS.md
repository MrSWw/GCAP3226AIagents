# Real-Time Monitoring Update Status

## Summary
The monitoring script has been updated to save CSV files and update the log file **in real-time** whenever buses are detected.

## Changes Made

### 1. Real-Time CSV Updates
- **File**: `realtime_monitoring.csv`
- **Location**: `/raw_data/23Nov/realtime_monitoring.csv`
- **Behavior**: Updated immediately when buses are detected (every 30 seconds when data is available)
- **Format**: Same as before, with columns:
  - `snapshot_ts`: Timestamp when data was collected
  - `queried_stop_id`: Stop ID (3F24CFF9046300D9 for St. Martin, B34F59A0270AEDA4 for Chong San)
  - `route`: Bus route number
  - `direction`: Direction (O for Outbound)
  - `eta`: Estimated arrival time
  - `eta_seq`: Sequence number (1, 2, 3, etc.)
  - `data_timestamp`: API data timestamp

### 2. Real-Time Log Updates
- **File**: `monitoring_log.txt`
- **Location**: `/raw_data/23Nov/monitoring_log.txt`
- **Behavior**: Updated immediately when buses are detected
- **Format**: Each bus detection is logged with:
  - Timestamp
  - Route number
  - Stop name (St. Martin PA206 or Chong San PA212)
  - ETA
  - Sequence number

### 3. Log File Flushing
- Added `f.flush()` to ensure log entries are written to disk immediately
- This ensures the log file is always up-to-date when viewed

## Current Status

**Monitoring Process**: Running (PID: 17177)
**Last Update**: 2025-11-23 23:39:42
**Routes Detected**: 272A (and others as they appear)

## Example Log Entries

```
[2025-11-23 23:39:42] 🚌 Route 272A detected at St. Martin PA206 | ETA: 2025-11-23T23:55:08+08:00 | Seq: 1
[2025-11-23 23:39:42] 🚌 Route 272A detected at Chong San PA212 | ETA: 2025-11-23T23:55:53+08:00 | Seq: 1
```

## Files Being Updated

1. **`realtime_monitoring.csv`**: Continuously appended with new bus detections
2. **`monitoring_log.txt`**: Continuously updated with log entries
3. **Hourly CSV files**: Still saved every hour as backup
4. **Final consolidated CSV**: Saved at the end of monitoring session

## How to Monitor

### View Log File in Real-Time
```bash
tail -f /Users/simonwang/Documents/Usage/GCAP3226/Team6_BusStopMerge/02_Data_Collection/raw_data/23Nov/monitoring_log.txt
```

### View CSV File
```bash
tail -f /Users/simonwang/Documents/Usage/GCAP3226/Team6_BusStopMerge/02_Data_Collection/raw_data/23Nov/realtime_monitoring.csv
```

### Check Monitoring Process
```bash
ps aux | grep monitor_with_csv
```

## Notes

- The script polls the API every 30 seconds
- Only buses with ETAs within the next 60 minutes are recorded
- Only Outbound (O) direction buses are monitored
- Only the 19 specified routes are monitored
- Both CSV and log files are updated immediately when buses are detected

