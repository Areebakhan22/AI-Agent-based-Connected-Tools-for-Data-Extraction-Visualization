# Slide Content Breakdown: What Goes on Each Slide

## 📊 Overview

The project creates **multiple slides** with different content:

- **Slide 1 (First Slide)**: Complete overview with ALL elements and relationships
- **Slide 2+ (Other Slides)**: Individual relationship diagrams (one per relationship)

---

## 🎯 **SLIDE 1: Full Combined Diagram**

### **What It Contains:**

```
┌─────────────────────────────────────────────────────────┐
│  System Boundary: "OpsCon_UAV_basedAircraftInspection"  │
│  ┌───────────────────────────────────────────────────┐ │
│  │                                                   │ │
│  │  [Actor]         [Use Case]         [Actor]      │ │
│  │  (Left)          (Center)           (Right)     │ │
│  │                                                   │ │
│  │         [Part]  [Part]  [Part]  [Part]          │ │
│  │         (Bottom Row)                              │ │
│  │                                                   │ │
│  │  ALL CONNECTIONS (All Arrows)                     │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### **Elements on Slide 1:**

✅ **System Boundary**
- Large rectangle container
- Title: System name (e.g., "OpsCon_UAV_basedAircraftInspection")
- Light gray background

✅ **ALL Parts** (All components)
- Human
- Environment  
- Drone
- Aircraft
- Any other parts from the model

✅ **ALL Actors** (All external entities)
- DroneOperator
- CandidateAircraft
- InspectionEnvironment
- Any other actors from the model

✅ **ALL Use Cases** (All system behaviors)
- InspectAircraftAutomatically
- Any other use cases from the model

✅ **ALL Connections** (All relationship arrows)
- Human → DroneOperator
- Environment → InspectionEnvironment
- Aircraft → CandidateAircraft
- Drone → SoI
- DroneOperator → InspectAircraftAutomatically
- CandidateAircraft → InspectAircraftAutomatically
- InspectionEnvironment → InspectAircraftAutomatically
- SoI → InspectAircraftAutomatically
- **Every single connection** from the model

### **Purpose:**
- **Complete system overview**
- See all relationships at once
- Understand the big picture
- Best for high-level understanding

### **Layout Algorithm:**
- Uses **hierarchical layout**
- Elements arranged in zones:
  - Use cases: Center (25% from top)
  - Actors: Left and Right sides
  - Parts: Bottom (80% from top)
- All connections drawn between all related elements

---

## 📋 **SLIDE 2+: Individual Relationship Diagrams**

### **What Each Slide Contains:**

Each slide (2, 3, 4, etc.) shows **ONE specific relationship**:

```
┌─────────────────────────────────────────────────────────┐
│  System Boundary: "OpsCon_UAV_basedAircraftInspection" │
│  ┌───────────────────────────────────────────────────┐ │
│  │                                                   │ │
│  │              [Source Element]                     │ │
│  │                      │                            │ │
│  │                      ▼                            │ │
│  │              [Target Element]                     │ │
│  │                                                   │ │
│  │              ONE CONNECTION (One Arrow)           │ │
│  │                                                   │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### **Elements on Each Individual Slide:**

✅ **System Boundary**
- Same large rectangle container
- Same system name

✅ **Source Element** (The "from" element)
- Only the element that the relationship starts from
- Could be a Part, Actor, or Use Case
- Example: "DroneOperator"

✅ **Target Element** (The "to" element)
- Only the element that the relationship goes to
- Could be a Part, Actor, or Use Case
- Example: "InspectAircraftAutomatically"

✅ **ONE Connection** (One arrow)
- Only the arrow for this specific relationship
- Example: "DroneOperator → InspectAircraftAutomatically"

### **Purpose:**
- **Focus on one relationship**
- Easier to understand individual connections
- Less cluttered view
- Better for detailed analysis
- Good for presentations focusing on specific relationships

### **Layout Algorithm:**
- Uses **simple layout** (for 2-3 elements) or **force-directed layout** (for more)
- Only shows elements relevant to that relationship
- Cleaner, more focused view

---

## 📊 **Example: Complete Slide Breakdown**

### **If Your Model Has 5 Relationships:**

**Slide 1 (Index 0): Full Combined**
- Contains: ALL parts, ALL actors, ALL use cases, ALL 5 connections
- Purpose: Complete overview

**Slide 2 (Index 1): Relationship 1**
- Contains: System boundary + Source element + Target element + 1 connection
- Example: "Human → DroneOperator"

**Slide 3 (Index 2): Relationship 2**
- Contains: System boundary + Source element + Target element + 1 connection
- Example: "Environment → InspectionEnvironment"

**Slide 4 (Index 3): Relationship 3**
- Contains: System boundary + Source element + Target element + 1 connection
- Example: "Aircraft → CandidateAircraft"

**Slide 5 (Index 4): Relationship 4**
- Contains: System boundary + Source element + Target element + 1 connection
- Example: "DroneOperator → InspectAircraftAutomatically"

**Slide 6 (Index 5): Relationship 5**
- Contains: System boundary + Source element + Target element + 1 connection
- Example: "SoI → InspectAircraftAutomatically"

---

## 🔄 **How It Works (Code Flow)**

### **Step 1: Split Model**
```python
# RelationshipSplitter.split_by_relationships()
1. Create FULL diagram (all relationships) → Slide 1
2. For each relationship:
   - Create individual diagram → Slide 2, 3, 4, etc.
```

### **Step 2: Calculate Layouts**
```python
# GraphLayoutEngine.calculate_layout()
- Full diagram: Uses hierarchical layout
- Individual diagrams: Uses simple/force-directed layout
```

### **Step 3: Render to Slides**
```python
# SlidesRenderer.render_diagram()
- Slide 1: is_full_diagram=True → Draws ALL relationships
- Slide 2+: is_full_diagram=False → Draws ONE relationship
```

---

## 📝 **Summary Table**

| Slide | Index | Content | Elements | Connections | Purpose |
|-------|-------|---------|----------|--------------|---------|
| **Slide 1** | 0 | Full Combined | ALL | ALL | Complete overview |
| **Slide 2** | 1 | Relationship 1 | 2-3 | 1 | Focus on relationship 1 |
| **Slide 3** | 2 | Relationship 2 | 2-3 | 1 | Focus on relationship 2 |
| **Slide 4** | 3 | Relationship 3 | 2-3 | 1 | Focus on relationship 3 |
| ... | ... | ... | ... | ... | ... |

---

## 🎨 **Visual Comparison**

### **Slide 1 (Full Combined):**
```
Complex diagram with:
- 4+ Parts
- 3+ Actors  
- 1+ Use Cases
- 8+ Connections (arrows everywhere)
```

### **Slide 2+ (Individual):**
```
Simple diagram with:
- 1 Source element
- 1 Target element
- 1 Connection (one arrow)
```

---

## 💡 **When to Use Which Slide**

### **Use Slide 1 (Full Combined) When:**
- Presenting the complete system architecture
- Need to see all relationships at once
- High-level overview for stakeholders
- Understanding system complexity

### **Use Individual Slides (2+) When:**
- Explaining a specific relationship in detail
- Step-by-step presentation
- Training or documentation
- Focused analysis of one connection

---

## 🔧 **Implementation Details**

### **Which Script Creates Multiple Slides?**

- **`visualize_sysml.py`**: Creates multiple slides (Slide 1 = full, Slide 2+ = individual)
- **`slides_generator.py`** (used by `main.py`): Creates single slide (all elements)

### **How to Generate Multiple Slides:**

```bash
# Use visualize_sysml.py for multiple slides
python visualize_sysml.py OpsCon.json

# This creates:
# - Slide 1: Full combined diagram
# - Slide 2+: Individual relationship diagrams
```

### **How to Generate Single Slide:**

```bash
# Use main.py for single slide
python main.py OpsCon.sysml --format google

# This creates:
# - Slide 1: All elements (single slide only)
```

---

## ✅ **Key Takeaways**

1. **First Slide (Slide 1)**: Complete system with ALL elements and ALL relationships
2. **Other Slides (Slide 2+)**: One relationship per slide, showing only relevant elements
3. **Purpose**: Slide 1 = overview, Slide 2+ = detailed focus
4. **Layout**: Slide 1 uses hierarchical layout, Slide 2+ uses simpler layouts
5. **Use Case**: Slide 1 for big picture, Slide 2+ for detailed explanations









