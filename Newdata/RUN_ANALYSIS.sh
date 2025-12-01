#!/bin/bash
# Quick script to run inter-stop analysis and display results

cd /workspaces/GCAP3226AIagents

echo "====================================================================="
echo "Running inter-stop ETA analysis (Peak vs Off-peak)"
echo "====================================================================="
echo ""

source .venv/bin/activate

python vibeCoding101/PartX_simulation/tools/interstop_eta_compare.py

echo ""
echo "====================================================================="
echo "Analysis complete! Results:"
echo "====================================================================="
echo ""

if [ -f "Newdata/interstop_peak_vs_offpeak.csv" ]; then
    echo "📊 CSV Summary (first 15 rows):"
    echo "---------------------------------------------------------------------"
    head -15 Newdata/interstop_peak_vs_offpeak.csv
    echo ""
fi

if [ -f "Newdata/interstop_peak_vs_offpeak.md" ]; then
    echo "📝 Markdown Summary:"
    echo "---------------------------------------------------------------------"
    cat Newdata/interstop_peak_vs_offpeak.md
    echo ""
fi

echo "====================================================================="
echo "Full files saved:"
echo "  - Newdata/interstop_peak_vs_offpeak.csv"
echo "  - Newdata/interstop_peak_vs_offpeak.md"
echo "====================================================================="
