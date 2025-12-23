# Quick Feedback Guide

## 🚀 Quick Start (3 Steps)

### Step 1: Edit in Google Slides
1. Open your presentation URL
2. Click on any element (shape) to edit
3. Change the text as needed
4. Save (auto-saves in Google Slides)

### Step 2: Extract Feedback
```bash
cd /home/bit-and-bytes/Desktop/Visualproj

./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --output feedback.json \
  --mapping element_mapping.json
```

**Replace `1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE` with your presentation ID**

### Step 3: Update JSON Model
```bash
./venv/bin/python3 update_model_from_feedback.py \
  OpsCon.json \
  feedback.json
```

---

## 📋 Your Current Presentation

**URL:** https://docs.google.com/presentation/d/1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE

**Presentation ID:** `1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE`

**Element Mapping:** `element_mapping.json`

---

## 🔄 Complete Command Reference

### Extract Feedback (One-time)
```bash
./venv/bin/python3 feedback_service.py \
  YOUR_PRESENTATION_ID \
  --output feedback.json \
  --mapping element_mapping.json
```

### Monitor for Changes (Real-time)
```bash
./venv/bin/python3 feedback_service.py \
  YOUR_PRESENTATION_ID \
  --monitor \
  --interval 10 \
  --output feedback.json \
  --mapping element_mapping.json
```

### Update Model from Feedback
```bash
./venv/bin/python3 update_model_from_feedback.py \
  OpsCon.json \
  feedback.json
```

### View Feedback
```bash
cat feedback.json | python3 -m json.tool
```

---

## 📖 Full Documentation

See `FEEDBACK_USER_GUIDE.md` for complete details.



