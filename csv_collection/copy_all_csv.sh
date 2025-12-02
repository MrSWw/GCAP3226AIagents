#!/bin/bash
# Script to copy all CSV files to csv_collection folder

SOURCE_DIR="/workspaces/GCAP3226AIagents"
TARGET_DIR="/workspaces/GCAP3226AIagents/csv_collection"

echo "Copying CSV files from presentation/simulation..."
mkdir -p "$TARGET_DIR/presentation_simulation"
cp "$SOURCE_DIR/presentation/simulation"/*.csv "$TARGET_DIR/presentation_simulation/" 2>/dev/null

echo "Copying CSV files from Newdata..."
mkdir -p "$TARGET_DIR/Newdata"
cp "$SOURCE_DIR/Newdata"/*.csv "$TARGET_DIR/Newdata/" 2>/dev/null

echo "Copying CSV files from vibeCoding101/PartX_simulation..."
mkdir -p "$TARGET_DIR/vibeCoding101_PartX_simulation"
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation"/*.csv "$TARGET_DIR/vibeCoding101_PartX_simulation/" 2>/dev/null

echo "Copying CSV files from vibeCoding101/PartX_simulation/presentation/travel_time_comparison..."
mkdir -p "$TARGET_DIR/vibeCoding101_travel_time_comparison"
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation/presentation/travel_time_comparison"/*.csv "$TARGET_DIR/vibeCoding101_travel_time_comparison/" 2>/dev/null

echo "Copying CSV files from vibeCoding101/PartX_simulation/monitor_outputs_until_0830..."
mkdir -p "$TARGET_DIR/monitor_outputs_until_0830"
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation/monitor_outputs_until_0830"/*.csv "$TARGET_DIR/monitor_outputs_until_0830/" 2>/dev/null
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation/monitor_outputs_until_0830/presentation/simulation"/*.csv "$TARGET_DIR/monitor_outputs_until_0830/" 2>/dev/null

echo "Copying CSV files from vibeCoding101/PartX_simulation/monitor_outputs_60min..."
mkdir -p "$TARGET_DIR/monitor_outputs_60min"
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation/monitor_outputs_60min"/*.csv "$TARGET_DIR/monitor_outputs_60min/" 2>/dev/null

echo "Copying CSV files from vibeCoding101/PartX_simulation/monitor_outputs_1hr..."
mkdir -p "$TARGET_DIR/monitor_outputs_1hr"
cp "$SOURCE_DIR/vibeCoding101/PartX_simulation/monitor_outputs_1hr"/*.csv "$TARGET_DIR/monitor_outputs_1hr/" 2>/dev/null

echo ""
echo "All CSV files copied successfully!"
echo "Total CSV files copied:"
find "$TARGET_DIR" -name "*.csv" | wc -l
