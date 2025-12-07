# Final Project Visualizations

## Project: Bus Stop Merger Analysis - GCAP3226

This folder contains **27 visualizations** created throughout the project, including simulations, analysis charts, and animations.

---

## Primary Report Figures (Part 2: Data Analysis)

### Figure 1: Simulation Wait Time Comparison
**File**: `Figure1_Wait_Time_Comparison.png` or `03_KPI_Wait_Comparison.png`

Compares mean and 90th percentile wait times across baseline (separate stops) and merged stop scenarios.
- **Baseline**: Mean 583s (9.7 min), 90th percentile 1,045s (17.4 min)
- **Merged**: Mean 522s (8.7 min), 90th percentile 1,137s (19.0 min)
- **Trade-off**: 10.5% mean wait reduction vs. 8.8% increase in worst-case delays

### Figure 2: Travel Time Analysis (Boarded Passengers)
**File**: `Figure2_Travel_Time_Analysis.png` or `02_KPI_Travel_Boarded.png`

Total in-system time (wait + travel + boarding) for successfully boarded passengers.
- Demonstrates merging primarily affects queueing dynamics, not fundamental capacity
- Operational improvements require addressing root causes (service frequency, berth capacity)

### Figure 3: Walking Distance Impact
**File**: `Figure3_Walking_Distance_Impact.png` or `01_KPI_Walk_Comparison.png`

Quantifies the accessibility trade-off introduced by stop merging.
- Stop merging increases walking distance for passengers previously served by closer stop
- Equity trade-off: efficiency gains vs. accessibility losses
- Disproportionately affects elderly, mobility-impaired, and families with children

---

## Simulation Animations

**04-06: Bus Movement Visualizations**
- `04_Bus_Movement_1min.gif` - 1-minute interval animation
- `05_Bus_Movement_5min.gif` - 5-minute interval animation
- `06_Bus_Movement_10min.gif` - 10-minute interval animation

Animated visualizations showing real-time bus movement, bunching effects, and queue dynamics across baseline and merged scenarios.

---

## Simulation Results by Configuration

**07-09: Average Wait Time by Scenario**
- `07_Avg_Wait_Scenario_60min.png` - 60-minute simulation run results
- `08_Avg_Wait_Scenario_Results.png` - Comprehensive results summary
- `09_Avg_Wait_Scenario_0830.png` - 08:30 peak time configuration

Comparative views of wait time improvements and trade-offs across different simulation configurations.

---

## Travel Time Analysis

**10-12: Travel Time Distributions**
- `10_Travel_Boxplot.png` - Box plot comparison of inter-stop travel times
- `11_Travel_CDF.png` - Cumulative distribution function (CDF) analysis
- `12_Travel_Hist_Overlay.png` - Overlaid histogram showing peak vs. off-peak distributions

Demonstrates the 10.7% median travel time increase for Route 272A during morning peak (112s→124s).

---

## Summary & Subplot Visualizations

**13-14: Combined Analysis**
- `13_Queue_Time_Subplots.png` - Queue time distributions across routes and time periods
- `14_Waiting_Time_Subplots.png` - Multi-panel waiting time analysis

Aggregated views across all 19 monitored routes showing congestion patterns.

---

## Monitoring & Data Analysis Charts

**15-24: Detailed Empirical Analysis**
- `15_Mean_Wait_Cleaned.png` - Cleaned mean wait time series
- `16_Route_Counts_Top20.png` - Frequency distribution for top 20 routes
- `17_Counts_5min_Stop_B34F59A0270AEDA4.png` - 5-minute passenger counts (Stop B34F59A0270AEDA4)
- `18_Wait_Distribution.png` - Overall wait time distribution histogram
- `19_Combined_Mean_Wait.png` - Combined mean wait times across scenarios
- `20_Counts_10min_Stop_B34F59A0270AEDA4.png` - 10-minute passenger counts (Stop B34F59A0270AEDA4)
- `21_Counts_5min_Stop_3F24CFF9046300D9.png` - 5-minute passenger counts (Stop 3F24CFF9046300D9)
- `22_Wait_Hist_ETA_Seq.png` - Wait time histogram by ETA sequence
- `24_Counts_10min_Stop_3F24CFF9046300D9.png` - 10-minute passenger counts (Stop 3F24CFF9046300D9)

Detailed breakdown of empirical monitoring data collected via Data.Gov.HK API across 96-hour monitoring window (Nov 23-27, 2024).

---

## Data Sources & Technical Specifications

All visualizations are generated from reproducible simulations and empirical data analysis:

### Simulation Parameters
- **Bus Capacity**: 70 passengers per bus
- **Boarding Time**: 2-3 seconds (Octopus card tap time)
- **Berth Capacity**: 2 berths per stop
- **Passenger Arrivals**: Poisson distribution (scenario-adjusted rates)
- **Runtime**: 10,000 seconds simulated time per iteration
- **Replications**: 1,000 independent runs per scenario

### Empirical Data Collection
- **Period**: 96 hours continuous monitoring (November 23-27, 2024)
- **Data Source**: Hong Kong Data.Gov.HK KMB/CTB ETA API
- **Frequency**: 60-second query intervals
- **Routes Monitored**: 19 routes across 2 stops
- **Total ETA Records**: 68,402 snapshots
- **Peak Observation Window**: 06:30-08:30 HKT (morning rush)
- **Off-peak Window**: 08:30-09:21 HKT (mid-morning)

### Stops Analyzed
- **Stop 1**: St. Martin Road (B34F59A0270AEDA4)
- **Stop 2**: Chong San Road (3F24CFF9046300D9)
- **Distance**: 200 meters apart

### Validation & Robustness
- **Simulation Credibility**: Simulated vs. empirical wait times within 15% agreement
- **Sensitivity Analysis**: Boarding time variation (2.0-3.5s) → results robust within ±7%
- **Stress Testing**: Doubled passenger arrival rates to identify capacity breaking points
- **Data Quality**: Filtered negative travel times (skip-stops/API anomalies, 8.3%), excluded deep-night periods (23:00-05:00)

### Key Finding
**Route 272A** (busiest service, 33% of all vehicles):
- **Off-peak**: 112 seconds median inter-stop travel time
- **Peak**: 124 seconds median inter-stop travel time
- **Peak Uplift**: **+10.7% congestion increase** during morning rush

---

## File Organization

**Numbered Files (01-24)**: Comprehensive visualization collection
- Files with sequential numbering contain duplicates and variations for analysis flexibility

**Primary Report Figures**:
- `Figure1_Wait_Time_Comparison.png` (KPI comparison)
- `Figure2_Travel_Time_Analysis.png` (boarded passenger metrics)
- `Figure3_Walking_Distance_Impact.png` (equity trade-off analysis)

---

## Integration with Final Report

These visualizations support:
- **Part 2, Section 3.2**: Quantitative Analysis (272A +10.7% peak finding)
- **Part 2, Section 3.3**: Simulation Model (baseline vs. merged trade-offs)
- **Part 2, Section 3.5**: Visualizations and Reproducibility (detailed interpretation)

All figures include captions and policy implications in the main report text.

---

## Reproducibility

All underlying data and code are open-sourced:

- Python Scripts: `run_monitor_window.py`, `interstop_eta_compare.py`, `sim_merge_compare.py`
- CSV Exports: `interstop_peak_vs_offpeak_4days.csv`, `kpi_summary_table.csv`, simulation results
- Documentation: `MONITORING_DATES_SUMMARY.md`, inline code comments

Any researcher with access to the Hong Kong Data.Gov.HK API can:
1. Replicate the monitoring window (96 hours, Nov 23-27)
2. Re-run the pairing algorithm with identical filtering rules
3. Validate the 10.7% peak uplift finding
4. Extend simulations with alternative parameters

This transparency aligns with GCAP3226's core theme: participatory governance through open data and reproducible analysis.

---

**Project**: Bus Stop Merger Analysis for St. Martin Road & Chong San Road  
**Course**: GCAP3226 - Empowering Citizens Through Data  
**Date**: December 2025
