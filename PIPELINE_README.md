# SysML JSON → Google Slides Pipeline

A generic, reusable pipeline that transforms SysML-derived JSON system models into clean, dynamic component–relationship diagrams rendered in Google Slides, with bidirectional feedback support.

## Features

✅ **JSON Input Only**: Uses SysML-derived JSON as input (no regex or raw SysML parsing)  
✅ **LLM-Based Semantic Understanding**: Uses LLaMA/Ollama for semantic understanding and validation  
✅ **Relationship-Based Splitting**: Each relationship generates one diagram/slide  
✅ **Graph Layout Engine**: Uses NetworkX for dynamic, deterministic positioning  
✅ **Google Slides Rendering**: Renders diagrams with element_id metadata  
✅ **Bidirectional Feedback**: Extracts user edits from Slides and sends back as JSON  

## Architecture

```
JSON Model
    ↓
[SemanticModelProcessor] → LLM semantic understanding
    ↓
[RelationshipSplitter] → Split by relationships (one per slide)
    ↓
[GraphLayoutEngine] → NetworkX graph layout
    ↓
[SlidesRenderer] → Google Slides API rendering
    ↓
[FeedbackHandler] → Extract feedback from Slides
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Google Slides API:
   - Create a project in Google Cloud Console
   - Enable Google Slides API
   - Create OAuth 2.0 credentials (Desktop app)
   - Save as `credentials.json` in the project directory

3. Set up Ollama (for LLM):
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3
```

## Usage

### Basic Usage

1. **Convert SysML to JSON** (if needed):
```bash
python convert_to_json.py OpsCon.sysml --output OpsCon.json
```

2. **Run the pipeline**:
```bash
python visualize_sysml.py OpsCon.json --model llama3
```

### Advanced Usage

**Update existing presentation:**
```bash
python visualize_sysml.py OpsCon.json --presentation-id YOUR_PRESENTATION_ID
```

**Extract feedback:**
```bash
# First, get the element mapping file from visualize_sysml.py output
python feedback_service.py YOUR_PRESENTATION_ID --output feedback.json --mapping element_mapping.json
```

**Monitor for real-time feedback:**
```bash
python feedback_service.py YOUR_PRESENTATION_ID --monitor --interval 5 --mapping element_mapping.json
```

## JSON Input Format

The pipeline expects JSON in this format:

```json
{
  "parts": [
    {
      "name": "PartName",
      "doc": "description",
      "parent": "ParentName or null",
      "is_top_level": true or false
    }
  ],
  "actors": [
    {
      "name": "ActorName",
      "doc": "description"
    }
  ],
  "use_cases": [
    {
      "name": "UseCaseName",
      "doc": "description",
      "objectives": ["objective1", "objective2"]
    }
  ],
  "hierarchy": {
    "ParentName": ["Child1", "Child2"]
  },
  "connections": [
    {
      "from": "SourcePart",
      "to": "TargetPart"
    }
  ]
}
```

## Semantic Mappings

The LLM performs semantic mappings:
- **parts/actors** → components (rectangles)
- **use_cases** → functional nodes (rounded rectangles)
- **connections** → labeled edges (arrows)
- **system boundary** → enclosing rectangle

## Graph Layout

Uses NetworkX spring layout algorithm for dynamic positioning:
- System boundary encloses all elements
- Source and target elements positioned relative to relationship
- Deterministic layout (seed=42 for reproducibility)

## Feedback Format

Feedback is extracted as JSON:

```json
{
  "presentation_id": "...",
  "timestamp": 1234567890.0,
  "slides": [
    {
      "slide_index": 0,
      "elements": [
        {
          "element_id": "element_name",
          "shape_id": "shape_id",
          "text_content": "user edited text",
          "has_text_changes": true
        }
      ]
    }
  ]
}
```

## Components

### SemanticModelProcessor
- Uses LLM to semantically understand JSON models
- Validates relationships
- Enriches model with semantic mappings

### RelationshipSplitter
- Splits model into sub-models (one per relationship)
- Each sub-model contains: system + source + target

### GraphLayoutEngine
- Uses NetworkX for graph layout
- Calculates positions dynamically
- Enforces semantic layout (system boundary, source/target positioning)

### SlidesRenderer
- Renders diagrams using Google Slides API
- Stores element_id metadata on shapes
- Maintains consistent visual style

### FeedbackHandler
- Extracts user text from Slides
- Maps shape IDs to element IDs
- Returns feedback as JSON

## Example Workflow

1. **Generate JSON from SysML:**
```bash
python convert_to_json.py OpsCon.sysml
# Creates OpsCon.json
```

2. **Create Slides:**
```bash
python visualize_sysml.py OpsCon.json --title "System Model"
# Creates presentation and returns URL
```

3. **User edits in Google Slides** (manually)

4. **Extract feedback:**
```bash
python feedback_service.py PRESENTATION_ID --output feedback.json
```

5. **Process feedback** (integrate with your tool)

## Troubleshooting

**Ollama not found:**
- Install Ollama from https://ollama.ai
- Run `ollama pull llama3`
- Ensure Ollama is running: `ollama serve`

**Google Slides API errors:**
- Check `credentials.json` exists
- Verify OAuth 2.0 credentials are correct
- Re-authenticate if token expires

**NetworkX layout issues:**
- Ensure NetworkX is installed: `pip install networkx`
- For large graphs, consider adjusting layout parameters

## License

See main project license.

