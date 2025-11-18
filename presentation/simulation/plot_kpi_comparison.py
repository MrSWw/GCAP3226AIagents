#!/usr/bin/env python3
"""
Simple KPI visualization script for pre / post1 / post2 scenarios.
Saves PNG files into `presentation/simulation/`.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

OUTDIR = os.path.dirname(__file__)
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR, exist_ok=True)

# KPI numbers (from user-provided table)
rows = [
    {
        'scenario': 'pre',
        'n_reps': 200,
        'avg_wait_mean': 240.56,
        'median_wait_mean': 197.87,
        'p90_wait_mean': 540.31,
        'total_walk_mean': 0.0,
        'avg_total_travel_mean': 321.43,
        'mean_boarded': 103.23,
        'mean_remaining_queue': 0.0,
        'mean_dwell': 11.32
    },
    {
        'scenario': 'post1 (half-half)',
        'n_reps': 200,
        'avg_wait_mean': 157.39,
        'median_wait_mean': 75.44,
        'p90_wait_mean': 434.39,
        'total_walk_mean': 14423.1,
        'avg_total_travel_mean': 357.86,
        'mean_boarded': 117.345,
        'mean_remaining_queue': 2.84,
        'mean_dwell': 11.49
    },
    {
        'scenario': 'post2 (merge one)',
        'n_reps': 200,
        'avg_wait_mean': 158.14,
        'median_wait_mean': 74.21,
        'p90_wait_mean': 435.22,
        'total_walk_mean': 14451.0,
        'avg_total_travel_mean': 359.01,
        'mean_boarded': 117.62,
        'mean_remaining_queue': 2.805,
        'mean_dwell': 11.50
    }
]

df = pd.DataFrame(rows)
# derived metric: walk per boarded passenger (s)
df['walk_per_passenger_s'] = df['total_walk_mean'] / df['mean_boarded']

sns.set(style='whitegrid')

# 1) Waiting metrics comparison: avg / median / p90
plt.figure(figsize=(9,6))
bar_width = 0.25
x = np.arange(len(df))
plt.bar(x - bar_width, df['avg_wait_mean'], width=bar_width, label='Avg Wait (s)', color='tab:blue')
plt.bar(x, df['median_wait_mean'], width=bar_width, label='Median Wait (s)', color='tab:cyan')
plt.bar(x + bar_width, df['p90_wait_mean'], width=bar_width, label='P90 Wait (s)', color='tab:purple')
plt.xticks(x, df['scenario'], rotation=20)
plt.ylabel('Seconds')
plt.title('Waiting Time Comparison (Avg / Median / P90)')
plt.legend()
plt.tight_layout()
out1 = os.path.join(OUTDIR, 'kpi_wait_comparison.png')
plt.savefig(out1, dpi=150)
plt.close()

# 2) Travel time and boarded / remaining queue
fig, ax1 = plt.subplots(figsize=(9,6))
ax2 = ax1.twinx()

ax1.bar(x - 0.15, df['avg_total_travel_mean'], width=0.3, label='Avg Total Travel (s)', color='tab:orange')
ax2.bar(x + 0.15, df['mean_boarded'], width=0.3, label='Mean Boarded (persons)', color='tab:green')

ax1.set_xlabel('Scenario')
ax1.set_ylabel('Avg Total Travel (s)', color='tab:orange')
ax2.set_ylabel('Mean Boarded (persons)', color='tab:green')
ax1.set_xticks(x)
ax1.set_xticklabels(df['scenario'], rotation=20)
ax1.set_title('Average Total Travel Time and Mean Boarded')

# legends
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax1.legend(h1+h2, l1+l2, loc='upper left')

plt.tight_layout()
out2 = os.path.join(OUTDIR, 'kpi_travel_boarded.png')
plt.savefig(out2, dpi=150)
plt.close()

# 3) Walk totals and walk per passenger
plt.figure(figsize=(9,6))
plt.bar(x - 0.1, df['total_walk_mean'], width=0.2, label='Total Walk (s per rep)', color='tab:gray')
plt.bar(x + 0.1, df['walk_per_passenger_s'], width=0.2, label='Estimated Walk / passenger (s)', color='tab:red')
plt.xticks(x, df['scenario'], rotation=20)
plt.ylabel('Seconds')
plt.title('Total Walk (per-rep) and Walk per Passenger (estimated)')
plt.legend()
plt.tight_layout()
out3 = os.path.join(OUTDIR, 'kpi_walk_comparison.png')
plt.savefig(out3, dpi=150)
plt.close()

# 4) Mean dwell & remaining queue as table saved
summary = df[['scenario','n_reps','avg_wait_mean','median_wait_mean','p90_wait_mean','avg_total_travel_mean','mean_boarded','mean_remaining_queue','mean_dwell','walk_per_passenger_s']]
summary_csv = os.path.join(OUTDIR, 'kpi_summary_table.csv')
summary.to_csv(summary_csv, index=False)

print('Generated files:')
print(out1)
print(out2)
print(out3)
print(summary_csv)

if __name__ == '__main__':
    # Running as script
    pass
