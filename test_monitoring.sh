#!/bin/bash
# Test script for continuous monitoring

echo "=========================================="
echo "Testing Continuous Monitoring"
echo "=========================================="
echo ""
echo "This will monitor your presentation for 30 seconds"
echo "with 5-second intervals (6 checks total)."
echo ""
echo "INSTRUCTIONS:"
echo "1. Open your Google Slides presentation in another window"
echo "2. Edit any element (change text)"
echo "3. Watch this terminal for change detection"
echo ""
echo "Press Enter to start monitoring..."
read

./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor \
  --interval 5 \
  --max-iterations 6 \
  --output feedback_test.json \
  --mapping element_mapping.json

echo ""
echo "=========================================="
echo "Monitoring test completed!"
echo "Check feedback_test.json for results"
echo "=========================================="
