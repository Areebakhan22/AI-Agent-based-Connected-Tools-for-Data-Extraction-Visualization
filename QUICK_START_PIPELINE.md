# Quick Start: SysML JSON → Google Slides Pipeline

## Prerequisites

1. **Install dependencies:**
```bash
pip install -r requirements.txt
pip install networkx  # If not already installed
```

2. **Set up Google Slides API:**
   - Download `credentials.json` from Google Cloud Console
   - Place in project directory

3. **Set up Ollama (optional, for LLM):**
```bash
ollama pull llama3
```

## Quick Start

### Step 1: Convert SysML to JSON

If you have a SysML file:
```bash
python convert_to_json.py OpsCon.sysml --output OpsCon.json
```

Or use the provided `OpsCon.json` file.

### Step 2: Generate Google Slides

```bash
python visualize_sysml.py OpsCon.json --title "System Model"
```

This will:
- Load the JSON model
- Use LLM for semantic understanding
- Split by relationships (one slide per relationship)
- Calculate graph layouts
- Render to Google Slides
- Save element mapping for feedback

**Output:**
- Google Slides presentation URL
- `element_mapping.json` file

### Step 3: Extract Feedback (Optional)

After users edit the slides:
```bash
python feedback_service.py PRESENTATION_ID --output feedback.json --mapping element_mapping.json
```

For continuous monitoring:
```bash
python feedback_service.py PRESENTATION_ID --monitor --interval 5 --mapping element_mapping.json
```

## Example Workflow

```bash
# 1. Convert SysML to JSON
python convert_to_json.py OpsCon.sysml

# 2. Generate slides
python visualize_sysml.py OpsCon.json --title "My System Model"

# Output:
# ✓ Created presentation: 1a2b3c4d5e6f7g8h9i0j
# ✓ View at: https://docs.google.com/presentation/d/1a2b3c4d5e6f7g8h9i0j
# ✓ Element mapping saved to: element_mapping.json

# 3. (User edits slides in browser)

# 4. Extract feedback
python feedback_service.py 1a2b3c4d5e6f7g8h9i0j --output feedback.json --mapping element_mapping.json

# Output:
# ✓ Feedback saved to: feedback.json
```

## Command Line Options

### visualize_sysml.py

```bash
python visualize_sysml.py JSON_FILE [OPTIONS]

Options:
  --model MODEL              Ollama model name (default: llama3)
  --presentation-id ID       Update existing presentation
  --title TITLE             Presentation title (default: SysML Visualization)
  --feedback-output PATH    Save feedback JSON (also saves mapping)
```

### feedback_service.py

```bash
python feedback_service.py PRESENTATION_ID [OPTIONS]

Options:
  --output, -o PATH         Output JSON file (default: feedback.json)
  --mapping, -m PATH        Element mapping JSON file
  --monitor                 Monitor for changes continuously
  --interval SECONDS        Polling interval (default: 5)
```

## Troubleshooting

**"Ollama not found"**
- Install from https://ollama.ai
- Run `ollama pull llama3`
- Start server: `ollama serve`

**"credentials.json not found"**
- Create OAuth 2.0 credentials in Google Cloud Console
- Download as `credentials.json`

**"NetworkX not found"**
- Install: `pip install networkx`

**No connections in model**
- Pipeline will create a single slide with all elements
- System boundary will still be rendered

## Next Steps

- Integrate feedback JSON with your tool
- Customize layout algorithms
- Add more semantic mappings
- Extend feedback processing










