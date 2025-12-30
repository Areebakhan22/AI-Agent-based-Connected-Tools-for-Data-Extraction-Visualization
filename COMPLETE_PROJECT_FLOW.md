# Complete Project Flow: From SysML File to Final Diagram Image

## Overview
This document explains the **complete end-to-end flow** of how a SysML file is transformed into visual diagrams in Google Slides, including all LLM processing, parsing, layout calculation, and image generation steps.

---

## 🎯 Complete Flow Diagram

```
SysML File (.sysml)
    ↓
[STEP 1: File Reading]
    ↓
[STEP 2: LLM-Based Parsing]
    ├─→ LLM Service (Ollama)
    ├─→ Prompt Engineering
    ├─→ JSON Extraction
    └─→ Data Normalization
    ↓
[STEP 3: Data Validation]
    ↓
[STEP 4: JSON Model Processing]
    ├─→ Semantic Understanding (LLM)
    ├─→ Relationship Splitting
    └─→ Model Enrichment
    ↓
[STEP 5: Graph Layout Calculation]
    ├─→ NetworkX Graph Creation
    ├─→ Layout Algorithm Selection
    ├─→ Position Calculation
    └─→ Collision Detection
    ↓
[STEP 6: Google Slides Rendering]
    ├─→ Authentication
    ├─→ Presentation Creation
    ├─→ Shape Drawing (Rectangles, Circles, Ovals)
    ├─→ Arrow/Connector Drawing
    └─→ Text Labeling
    ↓
[FINAL OUTPUT: Google Slides Presentation with Visual Diagrams]
```

---

## 📋 Detailed Step-by-Step Process

### **STEP 1: File Reading & Input**

**File:** `main.py` → `llm_parser.py`

**What Happens:**
1. User runs: `python main.py OpsCon.sysml`
2. Script reads the `.sysml` file as plain text
3. Content is stored as a string variable

**Code Location:**
```python
# llm_parser.py, line 30-31
with open(file_path, 'r', encoding='utf-8') as f:
    sysml_content = f.read()
```

**Example Input:**
```sysml
package OpsCon {
    part def OpsCon_UAV_basedAircraftInspection {
        doc /* System for UAV-based aircraft inspection */
    }
    
    part Human;
    part Drone;
    
    actor Inspector;
    
    use case InspectAircraft {
        doc /* Use case for aircraft inspection */
    }
    
    connect Human to Inspector;
    connect Inspector to InspectAircraft;
}
```

---

### **STEP 2: LLM-Based Parsing (First LLM Call)**

**File:** `llm_parser.py` → `llm_service.py`

**What Happens:**

#### **2.1 LLM Service Initialization**
- Connects to Ollama server (localhost:11434)
- Verifies model availability (e.g., `llama3`)
- Checks if Ollama is running

**Code Location:**
```python
# llm_service.py, line 36-37
llm_service = LLMService(model=model)
data = llm_service.extract_sysml(sysml_content)
```

#### **2.2 Prompt Creation**
The LLM receives a **comprehensive prompt** that includes:

**Prompt Structure:**
```
System Message: "You are a SysML v2 expert. Extract structured information 
                 from SysML files and return valid JSON only."

User Message: 
- Full SysML file content
- Detailed extraction instructions
- Expected JSON structure
- Rules for parsing parts, actors, use cases, connections
- Individual relationship diagram mapping rules
```

**Key Prompt Instructions:**
1. Extract ALL parts (both "part def" and nested "part" declarations)
2. Mark top-level parts with `"is_top_level": true`
3. Mark nested parts with `"is_top_level": false` and set their `"parent"`
4. Extract ALL actors (declared with "actor" keyword)
5. Extract ALL use cases (declared with "use case" keyword)
6. Extract objectives from use cases
7. Extract ALL "connect X to Y" statements as connections
8. Build hierarchy mapping
9. Extract documentation from "doc" comments
10. Return ONLY JSON, no additional text

**Code Location:**
```python
# llm_service.py, line 116-191
def _create_extraction_prompt(self, sysml_content: str) -> str:
    prompt = f"""Analyze this SysML v2 file and extract all structured information.
    ...
    """
```

#### **2.3 LLM API Call**
- Sends prompt to Ollama API
- Uses `ollama.chat()` function
- Temperature: 0.1 (low for consistent, structured output)
- Model: `llama3` (or specified model)

**Code Location:**
```python
# llm_service.py, line 83-98
response = ollama.chat(
    model=self.model,
    messages=[...],
    options={'temperature': 0.1}
)
```

#### **2.4 Response Parsing**
- Extracts JSON from LLM response
- Handles markdown code blocks (```json ... ```)
- Removes any extra text around JSON
- Parses JSON string to Python dictionary

**Code Location:**
```python
# llm_service.py, line 193-228
def _parse_llm_response(self, response: str) -> Dict:
    # Remove markdown code blocks if present
    json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
    ...
    return json.loads(json_str)
```

#### **2.5 Data Normalization**
- Ensures all required fields exist
- Normalizes data types (strings, booleans, lists)
- Infers missing actors from connections
- Validates structure

**Code Location:**
```python
# llm_service.py, line 240-313
def _normalize_structure(self, data: Dict) -> Dict:
    normalized = {
        'parts': [],
        'actors': [],
        'use_cases': [],
        'hierarchy': {},
        'connections': []
    }
    ...
```

**Example LLM Output (JSON):**
```json
{
  "parts": [
    {
      "name": "OpsCon_UAV_basedAircraftInspection",
      "doc": "System for UAV-based aircraft inspection",
      "parent": null,
      "is_top_level": true
    },
    {
      "name": "Human",
      "doc": "",
      "parent": "OpsCon_UAV_basedAircraftInspection",
      "is_top_level": false
    }
  ],
  "actors": [
    {"name": "Inspector", "doc": ""}
  ],
  "use_cases": [
    {
      "name": "InspectAircraft",
      "doc": "Use case for aircraft inspection",
      "objectives": []
    }
  ],
  "hierarchy": {
    "OpsCon_UAV_basedAircraftInspection": ["Human", "Drone"]
  },
  "connections": [
    {"from": "Human", "to": "Inspector"},
    {"from": "Inspector", "to": "InspectAircraft"}
  ]
}
```

---

### **STEP 3: Data Validation**

**File:** `main.py` → `llm_parser.py`

**What Happens:**
1. Validates that all connections reference existing parts/actors
2. Warns about connections to unknown elements (may be actors)
3. Keeps all connections (even if they reference actors)

**Code Location:**
```python
# main.py, line 78
data['connections'] = validate_connections(data['parts'], data['connections'])
```

---

### **STEP 4: JSON Model Processing (Second LLM Call - Optional)**

**File:** `visualize_sysml.py` → `SemanticModelProcessor`

**What Happens:**

#### **4.1 Semantic Understanding (Second LLM Call)**
- Takes the parsed JSON model
- Uses LLM to semantically understand relationships
- Maps elements to diagram types:
  - Parts → Rectangles
  - Actors → Circles
  - Use Cases → Ovals/Ellipses
  - Subject → Round Rectangles

**Code Location:**
```python
# visualize_sysml.py, line 85-134
def understand_model(self, json_data: Dict) -> Dict:
    prompt = self._create_semantic_prompt(json_data)
    response = ollama.chat(model=self.model, messages=[...])
    ...
```

#### **4.2 Model Enrichment**
- Adds `element_types` mapping
- Adds `system_boundary` information
- Enriches model with semantic information

**Code Location:**
```python
# visualize_sysml.py, line 165-191
def _enrich_with_semantics(self, json_data: Dict, semantic_analysis: Dict) -> Dict:
    enriched['element_types'] = {}
    for part in json_data.get('parts', []):
        enriched['element_types'][part['name']] = 'part'
    ...
```

#### **4.3 Relationship Splitting**
- Splits model into sub-models:
  - **Full Combined Diagram**: All elements and relationships on one slide
  - **Individual Relationship Diagrams**: One slide per relationship

**Code Location:**
```python
# visualize_sysml.py, line 198-359
class RelationshipSplitter:
    def split_by_relationships(self, model: Dict) -> List[Dict]:
        # Creates full diagram + one per relationship
        ...
```

**Output:**
- List of sub-models, each representing one diagram/slide

---

### **STEP 5: Graph Layout Calculation**

**File:** `visualize_sysml.py` → `GraphLayoutEngine`

**What Happens:**

#### **5.1 NetworkX Graph Creation**
- Creates a directed graph (DiGraph) using NetworkX
- Nodes = Elements (parts, actors, use cases)
- Edges = Connections/Relationships
- Node attributes = Element types

**Code Location:**
```python
# visualize_sysml.py, line 738-857
def calculate_layout(self, sub_model: Dict) -> Dict:
    G = nx.DiGraph()
    # Add nodes
    for part in model.get('parts', []):
        G.add_node(part['name'], type='part')
    # Add edges
    for conn in model.get('connections', []):
        G.add_edge(conn['from'], conn['to'])
```

#### **5.2 Layout Algorithm Selection**
Three layout algorithms available:

**A. Hierarchical Layout** (Default)
- Use cases: Center-top area (horizontal arrangement)
- Components: Arranged around (left, right, bottom)
- Professional SysML-style organization

**B. Force-Directed Layout** (Spring Layout)
- Uses NetworkX `spring_layout()`
- Simulates physical forces (attraction/repulsion)
- Iterative refinement (100+ iterations)

**C. Individual Relationship Layout** (Specialized)
- Use Case: Center-right (Oval)
- Actor: Circle on Use Case edge (Port)
- Part: Bottom-left (Rectangle)

**Code Location:**
```python
# visualize_sysml.py, line 372-494
def _hierarchical_layout(self, G: nx.DiGraph, root: str) -> Dict:
    # Calculate positions for hierarchical layout
    ...
```

#### **5.3 Position Calculation**
- Calculates X, Y coordinates for each element
- Considers:
  - Slide dimensions (720x540 points)
  - Margins (50 points)
  - Element sizes (based on text length)
  - Spacing between elements

**Position Calculation Example:**
```python
# For use cases (center-top):
uc_y = margin_y + available_height * 0.25  # 25% from top
uc_start_x = margin_x + (available_width - total_uc_width) / 2  # Centered

# For parts (bottom):
part_y = content_y + content_height * 0.85  # 85% from top
```

#### **5.4 Collision Detection & Prevention**
- Checks for overlapping elements
- Adjusts positions if overlaps detected
- Ensures minimum spacing (80 points between nodes)

**Code Location:**
```python
# visualize_sysml.py, line 622-700
def _prevent_overlaps(self, pos: Dict, G: nx.DiGraph) -> Dict:
    # Check and resolve overlaps
    ...
```

#### **5.5 Layout Scaling**
- Scales positions to fit within slide bounds
- Ensures all elements are visible
- Maintains aspect ratio

**Code Location:**
```python
# visualize_sysml.py, line 700-737
def _scale_to_slide_bounds(self, pos: Dict, G: nx.DiGraph) -> Dict:
    # Scale positions to fit slide
    ...
```

**Output:**
```python
{
    'system_boundary': {
        'name': 'OpsCon_UAV_basedAircraftInspection',
        'x': 50, 'y': 50,
        'width': 620, 'height': 440
    },
    'elements': {
        'Human': {
            'type': 'part',
            'x': 100, 'y': 450,
            'width': 140, 'height': 60
        },
        'Inspector': {
            'type': 'actor',
            'x': 350, 'y': 200,
            'size': 55
        },
        'InspectAircraft': {
            'type': 'functional_node',
            'x': 400, 'y': 150,
            'width': 280, 'height': 75
        }
    }
}
```

---

### **STEP 6: Google Slides Rendering**

**File:** `visualize_sysml.py` → `SlidesRenderer`

**What Happens:**

#### **6.1 Authentication**
- OAuth 2.0 authentication with Google
- Uses `credentials.json` file
- Saves `token.json` for future use
- Opens browser for user consent (first time)

**Code Location:**
```python
# visualize_sysml.py, line 999-1022
def authenticate(self):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    ...
    self.service = build('slides', 'v1', credentials=creds)
```

#### **6.2 Presentation Creation**
- Creates new Google Slides presentation
- Or updates existing presentation (if ID provided)
- Gets presentation ID

**Code Location:**
```python
# visualize_sysml.py, line 1024-1038
def create_or_get_presentation(self, title: str, presentation_id: Optional[str] = None) -> str:
    if presentation_id:
        # Use existing
    else:
        presentation = self.service.presentations().create(body={'title': title}).execute()
```

#### **6.3 Slide Creation**
- Creates new slide for each diagram
- Or clears existing slide if updating

**Code Location:**
```python
# visualize_sysml.py, line 1054-1071
if slide_index < len(slides):
    page_id = slides[slide_index]['objectId']
    self._clear_slide(page_id)
else:
    # Create new slide
    self.service.presentations().batchUpdate(...)
```

#### **6.4 System Boundary Drawing**
- Draws outer rectangle (system boundary)
- Light gray background
- Dark border
- System name as text

**Code Location:**
```python
# visualize_sysml.py, line 1150-1213
def _draw_system_boundary(self, page_id: str, boundary: Dict) -> str:
    requests = [{
        'createShape': {
            'objectType': 'RECTANGLE',
            'size': {...},
            'transform': {...}
        }
    }, {
        'updateShapeProperties': {
            'shapeBackgroundFill': {...},
            'outline': {...}
        }
    }]
```

#### **6.5 Element Drawing (Shapes)**

For each element in the layout:

**A. Parts → Rectangles**
- White background
- Black border (2pt)
- Text label (element name)
- Position: From layout calculation

**B. Actors → Circles**
- Light yellow background (#FFF9C4)
- Black border (2pt)
- Text label
- Equal width/height (circle)

**C. Use Cases → Ovals/Ellipses**
- White background
- Black border (2pt)
- Text label
- Ellipse shape

**D. Subject → Round Rectangles**
- Light green background (#C8E6C9)
- Black border
- Rounded corners

**Code Location:**
```python
# visualize_sysml.py, line 1215-1291 (Components)
# visualize_sysml.py, line 1293-1359 (Use Cases)
# visualize_sysml.py, line 1361-1420 (Actors)
```

**Google Slides API Request Example:**
```python
requests = [{
    'createShape': {
        'objectId': 'comp_123_Human',
        'shapeType': 'RECTANGLE',
        'elementProperties': {
            'pageObjectId': page_id,
            'size': {
                'height': {'magnitude': 60, 'unit': 'PT'},
                'width': {'magnitude': 140, 'unit': 'PT'}
            },
            'transform': {
                'translateX': 100,
                'translateY': 450,
                'unit': 'PT'
            }
        }
    }
}, {
    'updateShapeProperties': {
        'objectId': 'comp_123_Human',
        'shapeProperties': {
            'shapeBackgroundFill': {
                'solidFill': {
                    'color': {'rgbColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
                }
            },
            'outline': {
                'outlineFill': {
                    'solidFill': {
                        'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                    }
                },
                'weight': {'magnitude': 2, 'unit': 'PT'}
            }
        }
    }
}, {
    'insertText': {
        'objectId': 'comp_123_Human',
        'text': 'Human',
        'insertionIndex': 0
    }
}]

self.service.presentations().batchUpdate(
    presentationId=self.presentation_id,
    body={'requests': requests}
).execute()
```

#### **6.6 Arrow/Connector Drawing**

For each connection/relationship:

**A. Calculate Connection Points**
- From element: Edge point (closest to target)
- To element: Edge point (closest to source)
- Uses connection sites for unbreakable arrows

**B. Draw Arrow**
- Line from source to target
- Arrowhead at target end
- Black color
- 2pt stroke width

**Code Location:**
```python
# visualize_sysml.py, line 1422-1580
def _draw_arrow(self, page_id: str, from_shape_id: str, to_shape_id: str, ...):
    # Calculate connection points
    from_point = self._get_connection_point(from_layout, to_layout)
    to_point = self._get_connection_point(to_layout, from_layout)
    
    # Create line with arrowhead
    requests = [{
        'createLine': {
            'objectId': line_id,
            'elementProperties': {
                'pageObjectId': page_id,
                'line': {
                    'startConnection': {
                        'connectedObjectId': from_shape_id,
                        'connectionSiteIndex': from_site
                    },
                    'endConnection': {
                        'connectedObjectId': to_shape_id,
                        'connectionSiteIndex': to_site
                    },
                    'lineCategory': 'STRAIGHT_LINE',
                    'lineFill': {...},
                    'endArrow': 'FILLED_ARROW'
                }
            }
        }
    }]
```

**Connection Sites:**
- Google Slides uses connection sites (0-7) on shapes
- Site 0 = Top, 1 = Right, 2 = Bottom, 3 = Left, etc.
- Ensures arrows stay connected when shapes move

#### **6.7 Element ID Metadata Storage**
- Stores mapping: `shape_id → element_id`
- Used for feedback extraction
- Saved to `element_mapping.json`

**Code Location:**
```python
# visualize_sysml.py, line 1104-1106
shape_ids[elem_name] = shape_id
self.element_mapping[shape_id] = element_id
```

---

### **STEP 7: Final Output**

**Result:**
- Google Slides presentation with visual diagrams
- Each diagram on a separate slide
- URL: `https://docs.google.com/presentation/d/{presentation_id}`

**What You See:**
1. **System Boundary**: Large rectangle containing all elements
2. **Parts**: Rectangles with names
3. **Actors**: Circles with names
4. **Use Cases**: Ovals with names
5. **Connections**: Arrows showing relationships
6. **Text Labels**: Element names on shapes

---

## 🔄 Alternative Flow: Regex Parser (Fallback)

If LLM is unavailable or `--no-llm` flag is used:

**File:** `llm_parser.py` → `_fallback_regex_parse()`

**What Happens:**
1. Uses regex patterns to extract:
   - `part def PatternName {` → Parts
   - `part ChildName;` → Nested parts
   - `connect X to Y` → Connections
   - `doc /* ... */` → Documentation

2. No LLM calls
3. Faster but less accurate
4. Same output format (JSON)

---

## 📊 Data Flow Summary

```
SysML Text
    ↓ [LLM Call #1: Extraction]
Structured JSON
    ↓ [LLM Call #2: Semantic Understanding]
Enriched JSON Model
    ↓ [Relationship Splitting]
List of Sub-Models
    ↓ [NetworkX Graph Creation]
Graph Objects
    ↓ [Layout Calculation]
Position Dictionary
    ↓ [Google Slides API]
Visual Shapes & Arrows
    ↓
Final Diagram Image (in Google Slides)
```

---

## 🛠️ Key Technologies Used

1. **Ollama/LLaMA**: Local LLM for semantic understanding
2. **NetworkX**: Graph layout algorithms
3. **NumPy**: Numerical calculations for positioning
4. **Google Slides API**: Shape rendering and drawing
5. **Python OAuth2**: Google authentication

---

## 📝 Important Files

- `main.py`: Entry point, orchestrates workflow
- `llm_parser.py`: First LLM parsing step
- `llm_service.py`: LLM API communication
- `visualize_sysml.py`: Complete pipeline (semantic processing, layout, rendering)
- `slides_generator.py`: Alternative simple generator
- `sysml_parser.py`: Regex fallback parser

---

## 🎨 Visual Output Details

**Shape Types:**
- **Rectangle**: Parts/Components (white background, black border)
- **Circle**: Actors (light yellow background, black border)
- **Ellipse/Oval**: Use Cases (white background, black border)
- **Round Rectangle**: Subject of Interest (light green background)

**Layout Strategy:**
- **Use Cases**: Center-top (horizontal row)
- **Actors**: Left and right sides (aligned with use cases)
- **Parts**: Bottom area (horizontal row)
- **System Boundary**: Outer container rectangle

**Arrow Style:**
- Black color
- 2pt stroke width
- Filled arrowhead at target
- Connected via connection sites (unbreakable)

---

## 🔍 Debugging & Inspection

**JSON Output Files:**
- `complete_slide.json`: Full diagram layout data
- `react_diagrams.json`: React-compatible diagram data
- `element_mapping.json`: Shape ID to element ID mapping

**Console Output:**
- Shows extracted parts and connections
- Displays LLM processing status
- Shows layout calculation progress
- Reports rendering completion

---

This completes the full flow from SysML file to final visual diagram in Google Slides!

