#!/bin/bash
# Daily job: ingest fresh data then run paper trader
# Runs weekdays at 2pm PT (5pm ET, 1 hour after market close)

cd "/Users/jerrymao/Documents/Jiren Mao/trading"
source venv/bin/activate

echo "=== $(date) ==="
echo "--- Ingesting data ---"
python data/ingest.py

# Paper trader disabled — re-enable when strategy is validated
# echo "--- Running paper trader ---"
# python paper/trader.py

echo "--- Done ---"
