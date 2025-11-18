```markdown
# Dynamic bus arrival visualization — instructions

## Purpose
Read bus ETA data (live or historical snapshots), generate dynamic visualizations that show buses arriving/leaving stops and number of buses queueing, and save plots/animations into the simulation output folder.

## Inputs
- Primary (live): eTBus API endpoint used by the notebook: `https://data.etabus.gov.hk/v1/transport/kmb/stop-eta/{stop_id}`
- Historical / fallback CSVs (preferred when running off-peak):
  - `vibeCoding101/PartX_simulation/monitor_outputs_*/monitor_summary*.csv`
  - `presentation/simulation/all_etas_two_stops.csv` (pre-extracted for the two stations)
  - `presentation/simulation/all_etas_now_until_0930.csv` (example time-window extract)

## Process overview
1. Try to fetch real-time ETA via API for each `stop_id` used by the notebook.
2. If real-time ETAs are missing or sparse (common off-peak), fallback to historical monitor_snapshot CSVs or pre-extracted ETA CSVs.
3. Convert ETA timestamps into simulation schedule or use frequency-estimation (interval → freq) for stochastic SimPy bus arrival generation.
4. Run SimPy simulation(s) for configured `NUM_SIMULATIONS` and `SIM_TIME` to produce waiting/queue/dwell statistics.
5. Produce visual outputs (plots, violin/histograms, bar charts) and save into `presentation/simulation/`.

## Fallback strategy (recommended)
- Primary: use live API when available.
- Fallback: use historical monitor_summary CSVs (glob pattern below) to estimate route frequency or to supply ETA schedule.
  - Example glob: `/workspaces/GCAP3226AIagents/vibeCoding101/PartX_simulation/monitor_outputs_*/monitor_summary*.csv`
- Final fallback: synthetic default frequencies if neither live nor historical data exist.

## Files produced (examples)
- `presentation/simulation/kpi_wait_comparison.png`
- `presentation/simulation/kpi_travel_boarded.png`
- `presentation/simulation/kpi_walk_comparison.png`
- `presentation/simulation/all_etas_two_stops.csv` (extracted ETA rows)
- `vibeCoding101/PartX_simulation/simulation_results_baseline_stop_{stop_id}_morning_peak1.csv`
- `vibeCoding101/PartX_simulation/simulation_results_allocated_stop_{stop_id}_morning_peak1.csv`

## How to run (examples)
- Run the notebook interactively in Jupyter/VS Code: open `vibeCoding101/PartX_simulation/07_code_2scenarios.ipynb` and run cells top→bottom.
- Run the KPI plotting script (no notebook required):
```bash
python3 presentation/simulation/plot_kpi_comparison.py
```
- If you want notebook runs to use fallback CSVs, set the snapshots glob or CSV path in the notebook helper cell (example variable name `SNAPSHOT_GLOB`).

## Example fallback integration (code snippet)
Add or replace the `get_real_time_routes` call in the notebook with a wrapper that falls back to historical CSVs. Example implementation is documented in the repo README and README for `07_code_2scenarios`.

## Notes & troubleshooting
- Off-peak behaviour: ETA lists from the API may be empty or have null values — use fallback.
- Required Python packages: `pandas`, `numpy`, `simpy`, `matplotlib`, `seaborn`, (optional `scipy` for certain visuals). Install in the notebook kernel if missing: `%pip install scipy`.
- If generated CSVs/plots are not appearing, check `presentation/simulation/` for outputs and inspect notebook logs for fallback warnings.

## Next steps you can ask for
- I can wire the notebook to use the historical fallback automatically and re-run with `NUM_SIMULATIONS=200` to reproduce KPI tables.
- I can produce a small CLI script that builds a route-frequency CSV from all `monitor_summary*.csv` files and place it under `presentation/simulation/` for the notebook to consume.

Output folder: `/workspaces/GCAP3226AIagents/presentation/simulation`
```
input: /workspaces/GCAP3226AIagents/presentation all data from API on bus arrival time 
process: generate a dynamic visualization showing buses arriving and leaving the bus stops indicating number of buses queueing - create and run the python program in the folder below and create a md file to document what has been done
output: /workspaces/GCAP3226AIagents/presentation/simulation