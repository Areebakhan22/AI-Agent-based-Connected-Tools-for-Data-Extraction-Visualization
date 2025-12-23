# Pipeline Implementation Summary

## Overview

A complete, generic, reusable pipeline that transforms SysML-derived JSON system models into Google Slides diagrams with bidirectional feedback support.

## Components Built

### 1. **visualize_sysml.py** - Main Pipeline
- **SemanticModelProcessor**: Uses LLM (Ollama/LLaMA) for semantic understanding
- **RelationshipSplitter**: Splits model by relationships (one diagram per relationship)
- **GraphLayoutEngine**: Uses NetworkX for dynamic, deterministic graph layout
- **SlidesRenderer**: Renders diagrams via Google Slides API with element_id metadata
- **FeedbackHandler**: Extracts user feedback from Slides

### 2. **feedback_service.py** - Feedback Service
- Standalone service for extracting feedback
- Supports continuous monitoring
- Maps shape IDs to element IDs

### 3. **convert_to_json.py** - Helper Script
- Converts existing SysML files to JSON format
- Compatible with existing parser infrastructure

### 4. **Documentation**
- `PIPELINE_README.md`: Complete documentation
- `QUICK_START_PIPELINE.md`: Quick start guide
- `PIPELINE_SUMMARY.md`: This file

## Key Features

✅ **JSON Input Only**: No regex or raw SysML parsing  
✅ **LLM Semantic Understanding**: AI-driven model interpretation  
✅ **Relationship-Based Splitting**: One slide per relationship  
✅ **Graph Layout**: NetworkX spring layout for dynamic positioning  
✅ **Element Metadata**: Stores element_id on each shape  
✅ **Bidirectional Feedback**: Slides → JSON feedback extraction  
✅ **Edge Case Handling**: Handles no connections, missing elements, etc.  

## Architecture Flow

```
JSON Model
    ↓
[SemanticModelProcessor] → LLM semantic understanding & validation
    ↓
[RelationshipSplitter] → Split into sub-models (one per relationship)
    ↓
[GraphLayoutEngine] → NetworkX graph layout calculation
    ↓
[SlidesRenderer] → Google Slides API rendering
    ↓
[FeedbackHandler] → Extract user edits as JSON
```

## Usage Example

```bash
# 1. Convert SysML to JSON
python convert_to_json.py OpsCon.sysml

# 2. Generate slides
python visualize_sysml.py OpsCon.json --title "System Model"

# 3. Extract feedback (after user edits)
python feedback_service.py PRESENTATION_ID --output feedback.json --mapping element_mapping.json
```

## File Structure

```
visualize_sysml.py          # Main pipeline (1000+ lines)
feedback_service.py         # Feedback extraction service
convert_to_json.py          # Helper: SysML → JSON
OpsCon.json                 # Example JSON input
element_mapping.json        # Generated: shape_id → element_id mapping
feedback.json              # Generated: user feedback
PIPELINE_README.md          # Full documentation
QUICK_START_PIPELINE.md     # Quick start guide
```

## Dependencies

- `networkx`: Graph layout
- `ollama`: LLM integration
- `google-api-python-client`: Google Slides API
- `google-auth-oauthlib`: OAuth authentication

## Testing

Test with provided `OpsCon.json`:
```bash
python visualize_sysml.py OpsCon.json
```

## Next Steps

1. Install NetworkX: `pip install networkx`
2. Test with sample JSON
3. Customize layout algorithms if needed
4. Integrate feedback processing with your tool

## Notes

- Element IDs are stored in a mapping file for feedback extraction
- Graph layout is deterministic (seed=42)
- Handles edge cases: no connections, missing elements, etc.
- Supports both new and existing Google Slides presentations



