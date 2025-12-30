# Complete Feedback Flow User Guide

## Overview

This guide explains the complete bidirectional feedback flow: how to edit diagrams in Google Slides and send feedback back to update the JSON model.

---

## 📋 Table of Contents

1. [Initial Setup](#initial-setup)
2. [Viewing Your Presentation](#viewing-your-presentation)
3. [Editing Diagrams in Google Slides](#editing-diagrams-in-google-slides)
4. [Extracting Feedback](#extracting-feedback)
5. [Processing Feedback](#processing-feedback)
6. [Complete Workflow Example](#complete-workflow-example)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Initial Setup

### Prerequisites

1. **Google Slides Presentation Created**
   - You should have received a presentation URL like:
     ```
     https://docs.google.com/presentation/d/PRESENTATION_ID
     ```

2. **Element Mapping File**
   - File: `element_mapping.json`
   - Maps shape IDs to element IDs for feedback extraction

3. **Python Environment**
   - Virtual environment activated
   - Dependencies installed

### Files You Need

```
Visualproj/
├── visualize_sysml.py          # Main pipeline
├── feedback_service.py          # Feedback extraction service
├── element_mapping.json         # Element ID mappings (generated)
└── OpsCon.json                 # Original JSON model
```

---

## 👀 Viewing Your Presentation

### Step 1: Open the Presentation

1. **Copy the presentation URL** from the pipeline output:
   ```
   https://docs.google.com/presentation/d/1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE
   ```

2. **Open in browser** - The link will open in Google Slides

3. **Review the diagrams**:
   - **Slide 1**: Full combined diagram with all relationships
   - **Slides 2-5**: Individual relationship diagrams

### Step 2: Understand the Structure

Each slide contains:
- **System Boundary**: Large rectangle enclosing all elements
- **Components**: Rectangles (parts/actors)
- **Functional Nodes**: Rounded rectangles (use cases)
- **Relationships**: Arrows connecting elements
- **Labels**: Text on each element

---

## ✏️ Editing Diagrams in Google Slides

### What You Can Edit

1. **Element Names**: Click on any shape and edit the text
2. **Element Positions**: Drag shapes to reposition
3. **Add Comments**: Right-click → Comment
4. **Add Text Boxes**: Insert → Text box

### Editing Steps

#### Option 1: Edit Element Names

1. **Click on a shape** (e.g., "Human", "Drone", etc.)
2. **Click the text** inside the shape
3. **Type your changes** (e.g., "Human" → "Human Operator")
4. **Click outside** to save

#### Option 2: Add Comments/Notes

1. **Right-click on a shape**
2. **Select "Comment"**
3. **Type your feedback** (e.g., "Should be renamed to Operator")
4. **Click "Comment"** to save

#### Option 3: Add Text Annotations

1. **Insert → Text box**
2. **Type your notes**
3. **Position near the relevant element**

### Example Edits

**Before:**
- Element: "Human"
- Element: "Drone"

**After Editing:**
- Element: "Human Operator" (renamed)
- Element: "UAV Drone" (renamed)
- Comment on "Aircraft": "Should include model number"

---

## 📤 Extracting Feedback

### Method 1: One-Time Feedback Extraction

Extract feedback after making edits:

```bash
cd /home/bit-and-bytes/Desktop/Visualproj

./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --output feedback.json \
  --mapping element_mapping.json
```

**Replace `PRESENTATION_ID`** with your actual presentation ID:
- From URL: `https://docs.google.com/presentation/d/1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE`
- Presentation ID: `1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE`

**Example:**
```bash
./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --output feedback.json \
  --mapping element_mapping.json
```

### Method 2: Continuous Monitoring

Monitor for changes in real-time:

```bash
./venv/bin/python3 feedback_service.py \
  PRESENTATION_ID \
  --monitor \
  --interval 10 \
  --mapping element_mapping.json \
  --output feedback.json
```

**Parameters:**
- `--monitor`: Enable continuous monitoring
- `--interval 10`: Check every 10 seconds
- `--mapping`: Element mapping file
- `--output`: Where to save feedback

**To stop monitoring**: Press `Ctrl+C`

---

## 📊 Understanding Feedback Output

### Feedback JSON Structure

The `feedback.json` file contains:

```json
{
  "presentation_id": "1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE",
  "presentation_title": "SysML System Model - Full Combined",
  "timestamp": 1234567890.0,
  "slides": [
    {
      "slide_index": 0,
      "slide_id": "slide_0",
      "elements": [
        {
          "element_id": "Human",
          "shape_id": "comp_p_Human",
          "shape_type": "RECTANGLE",
          "text_content": "Human Operator",
          "has_text_changes": true
        },
        {
          "element_id": "Drone",
          "shape_id": "comp_p_Drone",
          "shape_type": "RECTANGLE",
          "text_content": "UAV Drone",
          "has_text_changes": true
        }
      ]
    }
  ]
}
```

### Key Fields

- **`element_id`**: Original element name from JSON
- **`shape_id`**: Google Slides shape identifier
- **`text_content`**: Current text in the shape (after edits)
- **`has_text_changes`**: `true` if text was modified
- **`timestamp`**: When feedback was extracted

---

## 🔄 Processing Feedback

### Step 1: Review Feedback

```bash
cat feedback.json | python3 -m json.tool
```

### Step 2: Update JSON Model

Create a script to process feedback:

```python
# update_model_from_feedback.py
import json

# Load original model
with open('OpsCon.json', 'r') as f:
    model = json.load(f)

# Load feedback
with open('feedback.json', 'r') as f:
    feedback = json.load(f)

# Process each slide
for slide in feedback['slides']:
    for element in slide['elements']:
        if element['has_text_changes']:
            element_id = element['element_id']
            new_text = element['text_content']
            
            # Update parts
            for part in model['parts']:
                if part['name'] == element_id:
                    part['name'] = new_text
                    print(f"Updated part: {element_id} → {new_text}")
            
            # Update actors
            for actor in model['actors']:
                if actor['name'] == element_id:
                    actor['name'] = new_text
                    print(f"Updated actor: {element_id} → {new_text}")
            
            # Update use cases
            for uc in model['use_cases']:
                if uc['name'] == element_id:
                    uc['name'] = new_text
                    print(f"Updated use case: {element_id} → {new_text}")

# Save updated model
with open('OpsCon_updated.json', 'w') as f:
    json.dump(model, f, indent=2)

print("\n✓ Updated model saved to: OpsCon_updated.json")
```

**Run the update script:**
```bash
./venv/bin/python3 update_model_from_feedback.py
```

### Step 3: Regenerate Slides (Optional)

After updating the JSON, regenerate slides:

```bash
./venv/bin/python3 visualize_sysml.py \
  OpsCon_updated.json \
  --title "SysML System Model - Updated" \
  --presentation-id PRESENTATION_ID
```

---

## 🔁 Complete Workflow Example

### Scenario: User wants to rename "Human" to "Human Operator"

#### Step 1: User Edits in Google Slides

1. Open presentation: `https://docs.google.com/presentation/d/1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE`
2. Click on "Human" shape
3. Edit text to "Human Operator"
4. Save (automatic in Google Slides)

#### Step 2: Extract Feedback

```bash
cd /home/bit-and-bytes/Desktop/Visualproj

./venv/bin/python3 feedback_service.py \
  1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE \
  --output feedback.json \
  --mapping element_mapping.json
```

**Output:**
```
✓ Feedback saved to: feedback.json
```

#### Step 3: Review Feedback

```bash
cat feedback.json | grep -A 5 "Human"
```

**Shows:**
```json
{
  "element_id": "Human",
  "text_content": "Human Operator",
  "has_text_changes": true
}
```

#### Step 4: Update JSON Model

```bash
./venv/bin/python3 update_model_from_feedback.py
```

**Output:**
```
Updated part: Human → Human Operator
✓ Updated model saved to: OpsCon_updated.json
```

#### Step 5: Verify Changes

```bash
cat OpsCon_updated.json | grep -A 3 "Human Operator"
```

#### Step 6: Regenerate Slides (Optional)

```bash
./venv/bin/python3 visualize_sysml.py \
  OpsCon_updated.json \
  --title "SysML System Model - Updated" \
  --presentation-id 1yYKlGkhe1jTF64DAAdtRWFVSQ5Yqx-T2LsBb-jm6zgE
```

---

## 🔧 Troubleshooting

### Issue: "credentials.json not found"

**Solution:**
1. Download OAuth 2.0 credentials from Google Cloud Console
2. Save as `credentials.json` in project directory

### Issue: "Presentation ID not found"

**Solution:**
- Extract ID from URL: `https://docs.google.com/presentation/d/ID_HERE`
- Use only the ID part (between `/d/` and `/` or end of URL)

### Issue: "Element mapping not found"

**Solution:**
- Run the pipeline again to generate `element_mapping.json`
- Or use the mapping file from the original pipeline run

### Issue: "No changes detected"

**Possible causes:**
1. No edits were made in Google Slides
2. Edits were made but not saved
3. Wrong presentation ID

**Solution:**
- Verify edits in Google Slides
- Check presentation ID is correct
- Try extracting feedback again

### Issue: "Permission denied"

**Solution:**
1. Ensure you're authenticated with Google
2. Check that you have edit access to the presentation
3. Re-authenticate: Delete `token.json` and run again

---

## 📝 Quick Reference Commands

### Extract Feedback (One-time)
```bash
./venv/bin/python3 feedback_service.py PRESENTATION_ID \
  --output feedback.json \
  --mapping element_mapping.json
```

### Monitor for Changes
```bash
./venv/bin/python3 feedback_service.py PRESENTATION_ID \
  --monitor --interval 10 \
  --output feedback.json \
  --mapping element_mapping.json
```

### View Feedback
```bash
cat feedback.json | python3 -m json.tool
```

### Count Changes
```bash
cat feedback.json | grep -c "has_text_changes.*true"
```

---

## 🎯 Best Practices

1. **Save Frequently**: Google Slides auto-saves, but verify changes are saved
2. **Use Comments**: Add comments for complex feedback
3. **Extract Regularly**: Extract feedback after each editing session
4. **Backup JSON**: Keep backups of original JSON before updates
5. **Version Control**: Track changes in feedback.json files

---

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Verify all files are in place
3. Ensure Google Slides API is enabled
4. Check Python environment is activated

---

## ✅ Checklist

Before extracting feedback:

- [ ] Google Slides presentation is accessible
- [ ] Edits have been made and saved
- [ ] `element_mapping.json` file exists
- [ ] Python virtual environment is activated
- [ ] Google credentials are set up
- [ ] Presentation ID is correct

After extracting feedback:

- [ ] `feedback.json` file was created
- [ ] Review feedback for accuracy
- [ ] Process feedback to update JSON
- [ ] Verify updated JSON model
- [ ] (Optional) Regenerate slides with updated model

---

**Last Updated**: Based on pipeline version with full combined diagram support










