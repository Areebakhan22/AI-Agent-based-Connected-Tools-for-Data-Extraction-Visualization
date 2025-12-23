#!/bin/bash
# Quick script to start real-time feedback monitoring

PRESENTATION_ID="1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4"

echo "=========================================="
echo "Starting Real-Time Feedback Monitoring"
echo "=========================================="
echo ""
echo "Presentation ID: $PRESENTATION_ID"
echo "Polling interval: 5 seconds"
echo ""
echo "INSTRUCTIONS:"
echo "1. Keep this terminal open"
echo "2. Open your presentation in browser:"
echo "   https://docs.google.com/presentation/d/$PRESENTATION_ID"
echo "3. Edit any element in Google Slides"
echo "4. Watch this terminal for change detection"
echo "5. Press Ctrl+C to stop"
echo ""
echo "Starting monitoring in 3 seconds..."
sleep 3

./venv/bin/python3 feedback_service.py \
  $PRESENTATION_ID \
  --monitor \
  --interval 5 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
