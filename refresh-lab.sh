#!/bin/bash

# 🧠 The Sub-1:15/3:15 Lab Automation Pipeline
# This script executes the full data transformation sequence.

echo "🚀 Starting Lab Sync..."

# 1. Update the Dashboard (Visuals)
echo "📊 Building Dashboard..."
python3 scripts/build-dashboard.py

# 2. Update Simplified Logs (No API Cost)
echo "📝 Generating Simplified Logs..."
python3 scripts/build-simplified-logs.py

# 3. Update Detailed Logs (Gemini API - Quota Sensitive)
echo "🧠 Generating Detailed Clinical Logs..."
python3 scripts/build-detailed-logs.py

# 4. Run the Performance Audit (Gemini API - Quota Sensitive)
# Note: This also triggers ui_manager.py automatically
echo "🔬 Running Performance Audit..."
python3 scripts/build-performance-audit.py

echo "✅ Lab Refresh Complete. Ready for Git Push."