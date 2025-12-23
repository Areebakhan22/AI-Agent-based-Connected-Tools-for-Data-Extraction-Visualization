# Real-Time Feedback Monitoring Guide

## 🚀 Quick Start

### Step 1: Start Monitoring

Open a terminal and run:

```bash
cd /home/bit-and-bytes/Desktop/Visualproj

./venv/bin/python3 feedback_service.py \
  1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4 \
  --monitor \
  --interval 5 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

**Replace `1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4` with your presentation ID**

### Step 2: Open Presentation in Browser

Open your Google Slides presentation in another window:
```
https://docs.google.com/presentation/d/1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4
```

### Step 3: Make Edits

1. Click on any element (e.g., "Human", "Drone", etc.)
2. Edit the text (e.g., "Human" → "Human Operator")
3. Save (auto-saves in Google Slides)

### Step 4: Watch Terminal

Within 5 seconds (or your set interval), you'll see:

```
[14:30:15] Check #2 - Extracting feedback... ✓ CHANGES DETECTED!
  → 1 change(s) found
    • Slide 1: 'Human' 'Human' → 'Human Operator'

  Statistics:
    • Total checks: 2
    • Changes detected: 1
    • Elements modified: 1
    • Monitoring time: 10.2s
```

### Step 5: Stop Monitoring

Press `Ctrl+C` to stop gracefully. You'll see final statistics.

---

## 📋 Command Options

### Basic Monitoring (5-second intervals)

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

### Fast Monitoring (2-second intervals)

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --interval 2 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

### Slow Monitoring (10-second intervals)

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --interval 10 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

### Limited Monitoring (10 checks, then stop)

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --interval 5 \
  --max-iterations 10 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

### Quiet Mode (less verbose)

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --interval 5 \
  --quiet \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

---

## 📊 Understanding Output

### Normal Operation (No Changes)

```
[14:30:10] Check #1 - Extracting feedback... ✓ Baseline established (first check)
  Waiting 5 seconds until next check...

[14:30:15] Check #2 - Extracting feedback... ✓ No changes
  Waiting 5 seconds until next check...
```

### When Changes Detected

```
[14:30:20] Check #3 - Extracting feedback... ✓ CHANGES DETECTED!
  → 2 change(s) found
    • Slide 1: 'Human' 'Human' → 'Human Operator'
    • Slide 1: 'Drone' 'Drone' → 'UAV Drone'

  Statistics:
    • Total checks: 3
    • Changes detected: 1
    • Elements modified: 2
    • Monitoring time: 15.3s

  Waiting 5 seconds until next check...
```

### When Stopped (Ctrl+C)

```
======================================================================
MONITORING STOPPED BY USER
======================================================================

Final Statistics:
  • Total checks: 8
  • Changes detected: 3
  • Elements modified: 5
  • Total monitoring time: 40.2s (0.7 minutes)
  • Last feedback saved to: feedback_realtime.json

✓ Monitoring stopped gracefully
======================================================================
```

---

## 🧪 Test Scenarios

### Test 1: Single Edit Detection

1. Start monitoring
2. Edit one element in Google Slides
3. Wait 5 seconds
4. Verify change is detected

**Expected:** Change detected within one interval

### Test 2: Multiple Edits

1. Start monitoring
2. Edit 3-4 elements quickly
3. Wait for next check
4. Verify all changes detected

**Expected:** All changes shown in one detection

### Test 3: Continuous Editing

1. Start monitoring
2. Edit elements every 10 seconds
3. Watch terminal for each detection

**Expected:** Each edit detected in subsequent checks

---

## 💡 Tips for Best Results

1. **Keep Browser Open**: Have Google Slides open while monitoring
2. **Save Changes**: Ensure edits are saved (auto-save is usually instant)
3. **Wait for Check**: Changes detected at next polling interval
4. **Check Feedback File**: `feedback_realtime.json` updates automatically
5. **Use Appropriate Interval**: 
   - Fast edits: 2-3 seconds
   - Normal use: 5 seconds
   - Occasional edits: 10 seconds

---

## 🔧 Troubleshooting

### Issue: Changes not detected

**Possible causes:**
- Edits not saved in Google Slides
- Wrong presentation ID
- Element mapping outdated

**Solutions:**
- Verify edits are saved (check Google Slides)
- Verify presentation ID matches
- Regenerate element_mapping.json if needed

### Issue: "Error during extraction"

**Solutions:**
- Check internet connection
- Verify Google authentication
- Wait a moment and retry

### Issue: Too many false positives

**Solutions:**
- Increase interval (--interval 10)
- Check if elements are being auto-modified
- Verify element_mapping.json is correct

---

## 📝 Example Workflow

```bash
# Terminal 1: Start monitoring
./venv/bin/python3 feedback_service.py \
  1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4 \
  --monitor --interval 5 \
  --output feedback_realtime.json \
  --mapping element_mapping.json

# Browser: Open presentation and make edits
# Terminal: Watch for change detection

# When done, press Ctrl+C in terminal
# Then process feedback:
./venv/bin/python3 update_model_from_feedback.py \
  OpsCon.json feedback_realtime.json
```

---

## 🎯 Quick Reference

**Your Current Presentation:**
- ID: `1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4`
- URL: https://docs.google.com/presentation/d/1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4

**Quick Command:**
```bash
./venv/bin/python3 feedback_service.py \
  1IIzjGeIlJXDvoKvst8VPKt32tGZ4OlrJlcrLQmXUxx4 \
  --monitor --interval 5 \
  --output feedback_realtime.json \
  --mapping element_mapping.json
```

**Stop:** Press `Ctrl+C`

---

Ready to test! Start monitoring and make edits in Google Slides! 🚀



