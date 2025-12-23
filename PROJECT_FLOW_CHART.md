# Project Flow Chart: SysML to Google Slides

## 📊 Complete Project Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: SysML File                            │
│                  (e.g., OpsCon.sysml)                           │
│                                                                 │
│  Contains:                                                      │
│  • part def (components)                                        │
│  • actors (external entities)                                   │
│  • use cases (system behaviors)                                 │
│  • connect (relationships)                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: PARSING                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  Method A: LLM   │         │  Method B: Regex │            │
│  │  (Primary)       │         │  (Fallback)       │            │
│  ├──────────────────┤         ├──────────────────┤            │
│  │ llm_service.py   │         │ sysml_parser.py   │            │
│  │    ↓             │         │    ↓              │            │
│  │ Ollama LLM       │         │ Pattern Matching │            │
│  │    ↓             │         │    ↓              │            │
│  │ Semantic Extract │         │ Regex Extract     │            │
│  └────────┬─────────┘         └────────┬─────────┘            │
│           │                             │                       │
│           └─────────────┬───────────────┘                       │
│                         ▼                                       │
│              ┌─────────────────────┐                            │
│              │  Structured JSON     │                            │
│              │  {                  │                            │
│              │    parts: [...],     │                            │
│              │    actors: [...],    │                            │
│              │    use_cases: [...], │                            │
│              │    connections: [...],│                            │
│              │    hierarchy: {...}  │                            │
│              │  }                  │                            │
│              └─────────────────────┘                            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 2: LAYOUT CALCULATION                        │
├─────────────────────────────────────────────────────────────────┤
│  slides_generator.py → calculate_professional_layout()          │
│                                                                 │
│  1. Calculate Element Sizes                                     │
│     • Text dimensions estimation                                │
│     • Width/Height based on content                             │
│                                                                 │
│  2. Define Layout Zones                                         │
│     ┌─────────────────────────────────────┐                    │
│     │     System Boundary Box              │                    │
│     │                                     │                    │
│     │  ┌──────┐        ┌──────┐          │                    │
│     │  │Actor │  Use Cases  │Actor│      │                    │
│     │  │(Left)│  (Center)   │(Right)│    │                    │
│     │  └──────┘        └──────┘          │                    │
│     │                                     │                    │
│     │         Parts (Bottom)              │                    │
│     │                                     │                    │
│     └─────────────────────────────────────┘                    │
│                                                                 │
│  3. Position Elements                                           │
│     • Use Cases: Center (40% from top)                          │
│     • Actors: Left & Right sides                                │
│     • Parts: Bottom (85% from top)                              │
│                                                                 │
│  4. Collision Detection                                         │
│     • Check overlaps                                            │
│     • Adjust positions                                          │
│                                                                 │
│  5. Build Connection Map                                        │
│     • Map relationships for arrows                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│            PHASE 3: SLIDE GENERATION                            │
├─────────────────────────────────────────────────────────────────┤
│  slides_generator.py → generate_slides()                        │
│                                                                 │
│  1. Authenticate Google Slides API                              │
│  2. Create/Update Presentation                                  │
│  3. Clear Existing Content                                      │
│  4. Draw Elements on Slide                                      │
│  5. Draw Connections (Arrows)                                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT                                      │
│            Google Slides Presentation                            │
│         (Single Slide with All Elements)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 What Goes on Each Slide

### **Multi-Slide Structure** (visualize_sysml.py Implementation)

The project generates **MULTIPLE slides** with different content:

---

## 📊 **SLIDE 1 (First Slide - Index 0): Full Combined Diagram**

**Contains:** ALL elements and ALL relationships in one complete diagram

### **What's on Slide 1:**
- ✅ **System Boundary** (large rectangle container)
- ✅ **ALL Parts** (all components from the model)
- ✅ **ALL Actors** (all external entities)
- ✅ **ALL Use Cases** (all system behaviors)
- ✅ **ALL Connections** (all relationship arrows)

### **Purpose:**
- Complete overview of the entire system
- Shows all relationships at once
- Best for understanding the big picture

### **Layout:**
- Uses hierarchical layout algorithm
- Elements arranged in zones (use cases center, actors sides, parts bottom)
- All connections drawn between all related elements

---

## 📊 **SLIDE 2+ (Other Slides - Index 1+): Individual Relationship Diagrams**

**Contains:** Only the elements involved in ONE specific relationship

### **What's on Each Individual Slide:**
- ✅ **System Boundary** (same container)
- ✅ **Source Element** (the "from" element in the relationship)
- ✅ **Target Element** (the "to" element in the relationship)
- ✅ **ONE Connection** (the arrow for this specific relationship)

### **Purpose:**
- Focus on a single relationship
- Easier to understand individual connections
- Better for detailed analysis

### **Layout:**
- Uses simple or force-directed layout (depending on number of elements)
- Only shows elements relevant to that relationship
- Cleaner, less cluttered view

### **Example:**
If you have 5 relationships, you'll get:
- **Slide 1**: Full combined (all 5 relationships)
- **Slide 2**: Relationship 1 only
- **Slide 3**: Relationship 2 only
- **Slide 4**: Relationship 3 only
- **Slide 5**: Relationship 4 only
- **Slide 6**: Relationship 5 only

---

### **Single Slide Structure** (slides_generator.py - Alternative Implementation)

**Note:** The `slides_generator.py` (used by `main.py`) generates **ONE slide** containing all SysML elements:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SLIDE 1: Complete Diagram                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  System Boundary Box (Large Rectangle)                    │ │
│  │  Title: System Name (e.g., "OpsCon_UAV_basedAircraft...") │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │                                                       │ │ │
│  │  │  ┌──────┐                                            │ │ │
│  │  │  │Actor │                                            │ │ │
│  │  │  │(Left)│                                            │ │ │
│  │  │  └──┬───┘                                            │ │ │
│  │  │     │                                                │ │ │
│  │  │     │    ┌─────────────────────┐                      │ │ │
│  │  │     └───▶│  Use Case 1       │◀────┐                │ │ │
│  │  │          │  (Rounded Rect)    │     │                │ │ │
│  │  │          └─────────────────────┘     │                │ │ │
│  │  │                                        │                │ │ │
│  │  │          ┌─────────────────────┐       │                │ │ │
│  │  │          │  Use Case 2       │◀──────┘                │ │ │
│  │  │          │  (Rounded Rect)    │                        │ │ │
│  │  │          └─────────────────────┘                        │ │ │
│  │  │                                        ┌──────┐         │ │ │
│  │  │                                        │Actor │         │ │ │
│  │  │                                        │(Right)│        │ │ │
│  │  │                                        └──────┘         │ │ │
│  │  │                                                         │ │ │
│  │  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │ │ │
│  │  │  │ Part 1 │  │ Part 2 │  │ Part 3 │  │ Part 4 │       │ │ │
│  │  │  │(Rect)  │  │(Rect)  │  │(Rect)  │  │(Rect)  │       │ │ │
│  │  │  └────────┘  └────────┘  └────────┘  └────────┘       │ │ │
│  │  │                                                         │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  │                                                             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Element Types on Slide

### **1. System Boundary**
- **Shape**: Large Rectangle
- **Position**: Covers most of slide (8% margin)
- **Style**: Light gray fill, dark border (2pt)
- **Content**: System name as title (bold, 14pt)
- **Purpose**: Container for all system elements

### **2. Parts (Components)**
- **Shape**: Rectangle
- **Position**: Bottom area (85% from top of content)
- **Style**: White fill, black border (1.5pt)
- **Text**: Part name (centered, 11pt)
- **Layout**: Horizontal row, centered
- **Examples**: "Human", "Drone", "Aircraft", "Environment"

### **3. Use Cases**
- **Shape**: Rounded Rectangle
- **Position**: Center area (40% from top of content)
- **Style**: White fill, black border (1.5pt)
- **Text**: Use case name (centered, 11pt)
- **Layout**: Horizontal row, centered
- **Examples**: "InspectAircraftAutomatically"

### **4. Actors**
- **Shape**: Circle (Ellipse)
- **Position**: Left and Right sides
- **Style**: White fill, black border (1.5pt)
- **Text**: Actor name (centered, 10pt)
- **Layout**: Vertical stacks on sides
- **Alignment**: Aligned with connected use cases
- **Examples**: "DroneOperator", "CandidateAircraft", "InspectionEnvironment"

### **5. Connections (Arrows)**
- **Shape**: Thin Rectangle (line) + Triangle (arrowhead)
- **Style**: Black line (2pt thickness)
- **Routing**: Connects from source edge to target edge
- **Types**:
  - **Part → Actor**: Association
  - **Actor → Use Case**: Participation
  - **Part → Subject**: Association
  - **Subject → Use Case**: Subject relationship (dashed)

---

## 🎨 Layout Zones Breakdown

### **Zone 1: Top Area (0-30% from content top)**
- **Purpose**: Space for actors aligned with use cases
- **Elements**: Actors (if aligned with use cases)

### **Zone 2: Center Area (40% from content top)**
- **Purpose**: Primary use case area
- **Elements**: Use Cases (rounded rectangles)
- **Layout**: Horizontal row, centered
- **Spacing**: 40pt between use cases (adjustable)

### **Zone 3: Bottom Area (85% from content top)**
- **Purpose**: System components
- **Elements**: Parts (rectangles)
- **Layout**: Horizontal row, centered
- **Spacing**: 25pt between parts (adjustable)

### **Zone 4: Side Areas (Left & Right)**
- **Purpose**: External actors
- **Elements**: Actors (circles)
- **Layout**: Vertical stacks
- **Positioning**: 
  - Left: 15% from left edge
  - Right: 15% from right edge

---

## 🔄 Element Drawing Order

The elements are drawn in this specific order to ensure proper layering:

```
1. System Boundary (background)
   ↓
2. Parts (rectangles)
   ↓
3. Use Cases (rounded rectangles)
   ↓
4. Actors (circles)
   ↓
5. Connections (arrows) - LAST, so they appear on top
```

---

## 📊 Example: Complete Slide Content

Based on `OpsCon.sysml`, a typical slide contains:

### **System Boundary**
- Name: "OpsCon_UAV_basedAircraftInspection"

### **Parts (4 elements)**
- Human
- Environment
- Drone
- Aircraft

### **Use Cases (1 element)**
- InspectAircraftAutomatically

### **Actors (3 elements)**
- DroneOperator (left side)
- CandidateAircraft (right side)
- InspectionEnvironment (right side)

### **Subject (1 element)**
- SoI (Subject of Interest)

### **Connections (9 arrows)**
- Human → DroneOperator
- Environment → InspectionEnvironment
- Aircraft → CandidateAircraft
- Drone → SoI
- DroneOperator → InspectAircraftAutomatically
- CandidateAircraft → InspectAircraftAutomatically
- InspectionEnvironment → InspectAircraftAutomatically
- SoI → InspectAircraftAutomatically (dashed)

---

## 🎯 Alternative: Multi-Slide Approach

There's also a `visualize_sysml.py` script that creates **multiple slides**:

- **Slide 1**: Complete diagram (all relationships)
- **Slide 2+**: One slide per relationship (individual diagrams)

This approach splits the model by relationships for better focus on individual connections.

---

## 📝 Summary

**Current Flow:**
```
SysML File → Parse → Layout → Generate → Single Slide (All Elements)
```

**What's on the Slide:**
- 1 System Boundary (container)
- Multiple Parts (rectangles, bottom)
- Multiple Use Cases (rounded rectangles, center)
- Multiple Actors (circles, sides)
- Multiple Connections (arrows between elements)

**Layout Strategy:**
- Fixed zones for different element types
- Collision detection to prevent overlaps
- Professional SysML-style arrangement
- All elements fit within system boundary

