# Project Flow Summary: SysML to Google Slides Converter

## Overview
This project converts SysML (System Modeling Language) files into visual diagrams in Google Slides or PowerPoint presentations using LLM-based parsing and automated layout generation.

---

## Complete Project Flow

### **Phase 1: Input (SysML File)**
```
OpsCon.sysml (text file)
    ↓
Contains:
- part definitions (components)
- connections (relationships)
- actors (external entities)
- use cases (system behaviors)
```

### **Phase 2: Parsing (Two Methods)**

#### **Method A: LLM-Based Parsing (Primary)**
```
SysML Text File
    ↓
[llm_service.py] → Sends to Ollama (local LLM)
    ↓
LLM receives prompt with SysML content
    ↓
LLM extracts structured JSON:
{
  "parts": [...],
  "actors": [...],
  "use_cases": [...],
  "connections": [...],
  "hierarchy": {...}
}
    ↓
[llm_parser.py] → Validates and structures data
```

**How LLM Works:**
1. **LLM Service** (`llm_service.py`):
   - Connects to local Ollama server
   - Sends SysML content with extraction instructions
   - Uses prompt engineering to guide LLM to extract:
     - Part names and descriptions
     - Parent-child relationships (hierarchy)
     - Connection relationships (from → to)
     - Actors and use cases
   - Returns structured JSON response

2. **LLM Parser** (`llm_parser.py`):
   - Calls LLM service
   - Validates extracted data
   - Fills in missing relationships
   - Falls back to regex if LLM fails

#### **Method B: Regex-Based Parsing (Fallback)**
```
SysML Text File
    ↓
[sysml_parser.py] → Pattern matching with regex
    ↓
Extracts:
- part def patterns
- connect patterns
- nested part patterns
    ↓
Structured JSON output (same format as LLM)
```

**When Regex is Used:**
- `--no-llm` flag is set
- Ollama server is not running
- LLM parsing fails
- Quick testing without LLM setup

---

### **Phase 3: Layout Calculation**

```
Parsed JSON Data
    ↓
[slides_generator.py → calculate_professional_layout()]
    ↓
Step-by-step layout algorithm:
```

#### **Layout Algorithm Steps:**

**Step 1: Calculate Element Sizes**
- Measures text content for each element
- Estimates width/height based on:
  - Text length
  - Font size (11pt default)
  - Word wrapping
- Creates size dictionaries for parts, actors, use cases

**Step 2: Define Layout Zones**
```
┌─────────────────────────────────┐
│      System Boundary Box        │
│                                 │
│  ┌─────────┐                   │
│  │ Actors  │  Use Cases Center │
│  │ (Sides) │                   │
│  └─────────┘                   │
│                                 │
│         Parts (Bottom)          │
│                                 │
└─────────────────────────────────┘
```

- **Use Cases**: Center area (40% from top)
- **Actors**: Left and right sides
- **Parts**: Bottom area (85% from top)

**Step 3: Position Elements with Collision Detection**

1. **Position Use Cases** (center, horizontal row)
   - Calculate total width needed
   - Center horizontally
   - Check overlaps with existing elements
   - Adjust spacing if needed

2. **Position Actors** (sides)
   - Left side actors: vertical stack on left
   - Right side actors: vertical stack on right
   - Check overlaps

3. **Position Parts** (bottom)
   - Horizontal row at bottom
   - Center horizontally
   - Check overlaps
   - Move down if collision detected

4. **Handle Missing Elements** (SoI, etc.)
   - Default positions for elements not explicitly positioned
   - Collision detection and adjustment

**Step 4: Connection Mapping**
- Builds connection map showing relationships
- Used for arrow routing later

---

### **Phase 4: Visualization Generation**

```
Layout Dictionary
    ↓
[slides_generator.py → generate_slides()]
    ↓
Google Slides API Operations:
```

#### **Generation Process:**

1. **Authentication**
   - OAuth 2.0 with Google Cloud
   - Creates/updates presentation

2. **Clear Existing Content**
   - Removes all existing shapes from slide
   - Sets white background

3. **Draw System Boundary**
   - Large rectangle with title
   - Light gray fill, dark border

4. **Draw Elements** (in order):
   - **Parts** → Rectangles (white fill, black border)
   - **Use Cases** → Rounded rectangles (light blue fill)
   - **Actors** → Circles (light yellow fill)
   - Each element:
     - Creates shape via API
     - Sets position from layout
     - Adds text label
     - Styles with colors/borders

5. **Draw Connections**
   - For each connection in data:
     - Finds source and target shapes
     - Calculates connection points (edges of shapes)
     - Draws thin rectangle (horizontal or vertical)
     - Adds arrowhead triangle
     - Styles as black line

6. **Return Presentation URL**

---

## Why Diagrams Might Look Messed Up/Overlapping

### **Root Causes:**

1. **Fixed Layout Zones**
   - Elements are forced into specific zones (center, sides, bottom)
   - If too many elements in one zone, they can crowd
   - No dynamic zone resizing

2. **Simple Collision Detection**
   - Only checks for overlap AFTER positioning
   - Moves elements DOWN if overlap detected
   - Doesn't reposition horizontally or reorganize layout
   - Can push elements outside visible area

3. **Fixed Sizing Calculations**
   - Text size estimation is approximate
   - Doesn't account for actual rendered text size
   - May underestimate element sizes

4. **Connection Issues**
   - Connections reference elements that might not exist in layout
   - Missing elements default to bottom, causing crowding
   - Arrows may point to wrong locations if elements moved

5. **No Layout Optimization**
   - Doesn't use graph layout algorithms (e.g., force-directed, hierarchical)
   - No consideration of connection topology for positioning
   - Elements positioned independently, not as a connected graph

6. **Limited Space Management**
   - Doesn't calculate total space needed upfront
   - Places elements sequentially without global view
   - Can exceed slide boundaries

### **Specific Overlap Scenarios:**

- **Too Many Parts**: All parts forced to bottom row → horizontal crowding
- **Too Many Use Cases**: Center row gets crowded → overlaps horizontally
- **Many Actors**: Side stacks get tall → may exceed boundary
- **Large Text Labels**: Estimated size too small → elements overlap
- **Missing Elements in Connections**: Default positions cause overlaps with real elements

---

## Complete Data Flow Diagram

```
┌─────────────┐
│ OpsCon.sysml│
│  (Text File)│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     Parsing Phase               │
├─────────────────────────────────┤
│                                 │
│  Option 1: LLM Parser           │
│  ├─→ llm_service.py             │
│  │   └─→ Ollama (local LLM)     │
│  │       └─→ Semantic extraction │
│  │                               │
│  Option 2: Regex Parser         │
│  ├─→ sysml_parser.py            │
│  │   └─→ Pattern matching        │
│  │                               │
│  └─→ Structured JSON Data       │
│      {                           │
│        parts: [...],             │
│        actors: [...],            │
│        use_cases: [...],         │
│        connections: [...],       │
│        hierarchy: {...}          │
│      }                           │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   Layout Calculation Phase      │
├─────────────────────────────────┤
│  slides_generator.py            │
│  calculate_professional_layout()│
│                                 │
│  1. Calculate element sizes     │
│  2. Define layout zones         │
│  3. Position elements           │
│     - Use cases (center)        │
│     - Actors (sides)            │
│     - Parts (bottom)            │
│  4. Collision detection         │
│  5. Build connection map        │
│                                 │
│  → Layout Dictionary            │
│    {                            │
│      system_boundary: {...},    │
│      elements: {                │
│        'PartName': {            │
│          type, x, y,            │
│          width, height          │
│        }                        │
│      }                          │
│    }                            │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│  Visualization Generation Phase │
├─────────────────────────────────┤
│  slides_generator.py            │
│  generate_slides()              │
│                                 │
│  1. Authenticate Google API     │
│  2. Create/Update presentation  │
│  3. Clear existing content      │
│  4. Draw system boundary        │
│  5. Draw elements:              │
│     - Parts (rectangles)        │
│     - Use cases (rounded rects) │
│     - Actors (circles)          │
│  6. Draw connections (arrows)   │
│  7. Return presentation URL     │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│      Output                     │
├─────────────────────────────────┤
│  Google Slides Presentation     │
│  OR                             │
│  PowerPoint (.pptx) file        │
│                                 │
│  URL:                           │
│  docs.google.com/presentation/  │
│  d/{presentation_id}            │
└─────────────────────────────────┘
```

---

## Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **Main Orchestrator** | `main.py` | Coordinates entire flow, CLI interface |
| **LLM Service** | `llm_service.py` | Communicates with Ollama LLM |
| **LLM Parser** | `llm_parser.py` | Extracts data using LLM |
| **Regex Parser** | `sysml_parser.py` | Fallback regex-based extraction |
| **Layout Calculator** | `slides_generator.py` | Calculates element positions |
| **Google Slides Generator** | `slides_generator.py` | Generates Google Slides via API |
| **PowerPoint Generator** | `pptx_generator.py` | Generates .pptx files |

---

## Command Line Usage

```bash
# With LLM (default)
python main.py OpsCon.sysml --format google

# Without LLM (regex only)
python main.py OpsCon.sysml --format google --no-llm

# Update existing Google Slides
python main.py OpsCon.sysml --format google \
  --google-slides-url "https://docs.google.com/presentation/d/ID/edit"

# Generate PowerPoint instead
python main.py OpsCon.sysml --format pptx --no-llm
```

---

## Summary

**What the project does:**
- Converts SysML text files into visual diagrams
- Uses LLM for intelligent parsing (with regex fallback)
- Automatically calculates layouts
- Generates Google Slides or PowerPoint presentations

**Why overlaps occur:**
- Simple layout algorithm with fixed zones
- Basic collision detection (only moves down)
- No graph layout optimization
- Fixed positioning strategy doesn't adapt to content density
- Text size estimation may be inaccurate

**The approach:**
- Prioritizes **correctness** (all elements shown) over **aesthetics** (clean layout)
- This is intentional for Milestone 1 (basic functionality)
- Future improvements would add better layout algorithms











