Simulation of KMB bus arrivals at specified stops using the ETA APIs

This folder contains a small Python simulation that:
- finds stop IDs by name using the KMB stop list API
- fetches real-time ETA data for the stop
- schedules bus arrivals into a SimPy discrete-event simulation
- simulates passenger arrival (Poisson) and boarding, and reports wait-time statistics

Usage (example):

python sim_kmb_stops.py --stops "St. Martin Road" "Chong San Road" --horizon 120

If the container cannot reach the public API, the script will print a helpful error and instructions to provide stop IDs manually.

Files:
- `sim_kmb_stops.py` - the simulation script
- `requirements.txt` - required Python packages

Notes:
- The script uses the public etabus KMB endpoints described in `3e82f8bc.md`.
- The simulation uses simple, configurable passenger arrival rates and bus capacities; tune parameters for experiments.
