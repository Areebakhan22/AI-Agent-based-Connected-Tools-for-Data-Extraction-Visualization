# Continuous Monitoring Test Guide

## 🧪 Quick Test

### Test 1: Short Monitoring Session (30 seconds)

```bash
cd /home/bit-and-bytes/Desktop/Visualproj

./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor \
  --interval 5 \
  --max-iterations 6 \
  --output feedback_test.json \
  --mapping element_mapping.json
```

**What happens:**
- Monitors for 30 seconds (6 checks × 5 seconds)
- Detects any changes you make in Google Slides
- Shows detailed change information
- Saves feedback to `feedback_test.json`

**Steps:**
1. Run the command above
2. Open your presentation: https://docs.google.com/presentation/d/1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE
3. Edit any element (e.g., change "Human" to "Human Operator")
4. Watch the terminal - it will detect the change within 5 seconds!

---

## 📋 Test Scenarios

### Scenario 1: Single Element Edit

**Test:**
1. Start monitoring (command above)
2. In Google Slides, click on "Human" element
3. Change text to "Human Operator"
4. Save (auto-saves)

**Expected Output:**
```
[HH:MM:SS] Check #2 - Extracting feedback... ✓ CHANGES DETECTED!
  → 1 change(s) found
    • Slide 1: 'Human' 'Human' → 'Human Operator'

  Statistics:
    • Total checks: 2
    • Changes detected: 1
    • Elements modified: 1
    • Monitoring time: 10.2s
```

### Scenario 2: Multiple Element Edits

**Test:**
1. Start monitoring
2. Edit multiple elements:
   - "Human" → "Human Operator"
   - "Drone" → "UAV Drone"
   - "Aircraft" → "Target Aircraft"

**Expected Output:**
```
✓ CHANGES DETECTED!
  → 3 change(s) found
    • Slide 1: 'Human' 'Human' → 'Human Operator'
    • Slide 1: 'Drone' 'Drone' → 'UAV Drone'
    • Slide 1: 'Aircraft' 'Aircraft' → 'Target Aircraft'
```

### Scenario 3: No Changes

**Test:**
1. Start monitoring
2. Don't make any edits

**Expected Output:**
```
[HH:MM:SS] Check #1 - Extracting feedback... ✓ No changes
  Waiting 5 seconds until next check...

[HH:MM:SS] Check #2 - Extracting feedback... ✓ No changes
  Waiting 5 seconds until next check...
```

---

## 🔧 Advanced Testing

### Test with Custom Interval

```bash
# Check every 2 seconds (faster detection)
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor \
  --interval 2 \
  --max-iterations 10 \
  --output feedback_test.json \
  --mapping element_mapping.json
```

### Test with Quiet Mode

```bash
# Less verbose output (just dots for no changes)
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor \
  --interval 5 \
  --quiet \
  --output feedback_test.json \
  --mapping element_mapping.json
```

### Test Unlimited Monitoring

```bash
# Monitor indefinitely (until Ctrl+C)
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor \
  --interval 10 \
  --output feedback.json \
  --mapping element_mapping.json
```

---

## 📊 Understanding Output

### Normal Operation

```
======================================================================
CONTINUOUS MONITORING MODE
======================================================================
Presentation ID: 1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE
Polling interval: 5 seconds
Output file: feedback_test.json
Max iterations: 6
======================================================================

[14:30:15] Check #1 - Extracting feedback... ✓ No changes
  Waiting 5 seconds until next check...

[14:30:20] Check #2 - Extracting feedback... ✓ CHANGES DETECTED!
  → 1 change(s) found
    • Slide 1: 'Human' 'Human' → 'Human Operator'

  Statistics:
    • Total checks: 2
    • Changes detected: 1
    • Elements modified: 1
    • Monitoring time: 10.2s

  Waiting 5 seconds until next check...
```

### When Changes Detected

- **Timestamp**: When the check was performed
- **Change count**: Number of elements modified
- **Details**: Old text → New text for each change
- **Statistics**: Running totals and monitoring time

### When Stopped (Ctrl+C)

```
======================================================================
MONITORING STOPPED BY USER
======================================================================

Final Statistics:
  • Total checks: 5
  • Changes detected: 2
  • Elements modified: 3
  • Total monitoring time: 25.3s (0.4 minutes)
  • Last feedback saved to: feedback_test.json

✓ Monitoring stopped gracefully
======================================================================
```

---

## ✅ Verification Steps

### 1. Verify Feedback File

```bash
cat feedback_test.json | python3 -m json.tool
```

**Check for:**
- `timestamp` field (when extracted)
- `slides` array with elements
- `text_content` matches your edits
- `has_text_changes` is `true` for modified elements

### 2. Verify Change Detection

```bash
# Count changes
cat feedback_test.json | grep -c "has_text_changes.*true"

# View specific changes
cat feedback_test.json | grep -A 3 "Human Operator"
```

### 3. Test Update Script

```bash
# Update model from feedback
./venv/bin/python3 update_model_from_feedback.py \
  OpsCon.json \
  feedback_test.json
```

---

## 🐛 Troubleshooting

### Issue: "No changes detected" when edits were made

**Possible causes:**
1. Edits not saved in Google Slides
2. Wrong presentation ID
3. Element mapping mismatch

**Solutions:**
- Verify edits are saved (check Google Slides)
- Verify presentation ID is correct
- Check element_mapping.json exists and is current

### Issue: "Error during extraction"

**Possible causes:**
1. Network issues
2. Authentication expired
3. API quota exceeded

**Solutions:**
- Check internet connection
- Re-authenticate (delete token.json and run again)
- Wait a few minutes and retry

### Issue: Changes detected but wrong element

**Possible causes:**
1. Element mapping is outdated
2. Multiple elements with same name

**Solutions:**
- Regenerate element_mapping.json
- Check element IDs in mapping file

---

## 📝 Test Checklist

Before testing:
- [ ] Google Slides presentation is accessible
- [ ] `element_mapping.json` exists
- [ ] Python virtual environment is activated
- [ ] Google credentials are set up
- [ ] Presentation ID is correct

During testing:
- [ ] Monitoring starts successfully
- [ ] Can see status messages
- [ ] Can make edits in Google Slides
- [ ] Changes are detected
- [ ] Feedback file is created/updated

After testing:
- [ ] Feedback file contains changes
- [ ] Statistics are accurate
- [ ] Can stop monitoring gracefully (Ctrl+C)
- [ ] Final statistics are shown

---

## 🎯 Quick Test Commands

### 30-Second Test (Recommended for first test)
```bash
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor --interval 5 --max-iterations 6 \
  --output feedback_test.json \
  --mapping element_mapping.json
```

### 1-Minute Test
```bash
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --monitor --interval 5 --max-iterations 12 \
  --output feedback_test.json \
  --mapping element_mapping.json
```

### Use Test Script
```bash
./test_monitoring.sh
```

---

**Ready to test!** Start with the 30-second test above. 🚀



