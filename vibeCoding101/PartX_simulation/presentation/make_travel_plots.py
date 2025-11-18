#!/usr/bin/env python3
"""
Generate comparison plots for travel deltas (peak vs offpeak).
Produces:
- travel_hist_overlay.png
- travel_boxplot.png
- travel_cdf.png

Reads CSVs from presentation/travel_time_comparison/
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent
IN = BASE / 'travel_time_comparison'
OUT = BASE / 'figures'
OUT.mkdir(exist_ok=True)

peak_csv = IN / 'travel_deltas_peak.csv'
off_csv = IN / 'travel_deltas_offpeak.csv'

if not peak_csv.exists() or not off_csv.exists():
    raise SystemExit('Input CSVs not found in ' + str(IN))

peak = pd.read_csv(peak_csv)
off = pd.read_csv(off_csv)

# delta_s column may exist
for df in (peak, off):
    if 'delta_s' not in df.columns:
        # try lower/upper
        raise SystemExit('delta_s column not found')

peak_vals = peak['delta_s'].values
off_vals = off['delta_s'].values

# Histogram overlay
plt.figure(figsize=(8,4.5))
bins = np.linspace(0, max(peak_vals.max(), off_vals.max(), 200), 50)
plt.hist(off_vals, bins=bins, alpha=0.6, label=f'Off-peak (n={len(off_vals)})', density=False)
plt.hist(peak_vals, bins=bins, alpha=0.6, label=f'Peak (n={len(peak_vals)})', density=False)
plt.xlabel('Travel time between stops (s)')
plt.ylabel('Frequency')
plt.title('Peak vs Off-peak: Travel Time Distribution')
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / 'travel_hist_overlay.png', dpi=150)
plt.close()

# Boxplot
plt.figure(figsize=(6,4))
plt.boxplot([off_vals, peak_vals], labels=['Off-peak','Peak'], showfliers=True)
plt.ylabel('Travel time (s)')
plt.title('Travel time: Off-peak vs Peak (boxplot)')
plt.tight_layout()
plt.savefig(OUT / 'travel_boxplot.png', dpi=150)
plt.close()

# ECDF / CDF
def ecdf(data):
    x = np.sort(data)
    y = np.arange(1, len(x)+1) / len(x)
    return x, y

x_off, y_off = ecdf(off_vals)
x_peak, y_peak = ecdf(peak_vals)
plt.figure(figsize=(8,4.5))
plt.plot(x_off, y_off, label='Off-peak')
plt.plot(x_peak, y_peak, label='Peak')
plt.xlabel('Travel time (s)')
plt.ylabel('ECDF')
plt.title('ECDF of travel times: Peak vs Off-peak')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(OUT / 'travel_cdf.png', dpi=150)
plt.close()

print('Wrote figures to', OUT)
