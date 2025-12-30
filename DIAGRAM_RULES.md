# Predefined Rules for Diagram Generation

This document lists ALL predefined rules and requirements for diagram visualization in this project.

---

## 📐 **SHAPE TYPE MAPPING RULES**

### **Element Type → Shape Mapping:**
1. **Parts** → **Rectangles**
   - Shape Type: `RECTANGLE`
   - Background: White (RGB: 1.0, 1.0, 1.0)
   - Border: Black (RGB: 0.0, 0.0, 0.0)
   - Border Weight: 2 PT
   - Text: Element name (11pt font, not bold)

2. **Actors** → **Circles**
   - Shape Type: `ELLIPSE` (with equal width/height to make circle)
   - Background: Light Yellow (RGB: 1.0, 0.98, 0.77)
   - Border: Black (RGB: 0.0, 0.0, 0.0)
   - Border Weight: 2 PT
   - Text: Actor name (10pt font, not bold)
   - Size: Equal width and height (circular)

3. **Use Cases** → **Ovals/Ellipses**
   - Shape Type: `ELLIPSE` (oval shape, width > height)
   - Background: White (RGB: 1.0, 1.0, 1.0)
   - Border: Black (RGB: 0.0, 0.0, 0.0)
   - Border Weight: 2 PT
   - Text: Use case name (11pt font, not bold)

4. **Subject (SoI)** → **Round Rectangles**
   - Shape Type: `ROUND_RECTANGLE`
   - Background: Light Green (RGB: 0.78, 0.90, 0.79)
   - Border: Black (RGB: 0.0, 0.0, 0.0)
   - Border Weight: 2 PT
   - Text: Subject name (11pt font, not bold)

5. **System Boundary** → **Large Rectangle**
   - Shape Type: `RECTANGLE`
   - Background: Light Gray (RGB: 0.95, 0.95, 0.95)
   - Border: Dark Gray (RGB: 0.2, 0.2, 0.2)
   - Border Weight: 2 PT
   - Text: System name (14pt font, **bold**)
   - Position: Outer container for all elements

---

## 📏 **SIZE RULES**

### **Individual Relationship Diagrams (Medium-Sized):**
- **Use Case Oval:**
  - Width: Maximum 280 PT (or 45% of available width)
  - Height: 85 PT
  - Medium-large size

- **Actor Circle:**
  - Size: 55 PT (diameter)
  - Small circle (port size)

- **Part Rectangle:**
  - Width: Maximum 140 PT (or 22% of available width)
  - Height: 60 PT
  - Medium size

### **Full Combined Diagrams:**
- **Use Cases:**
  - Minimum Width: 160 PT
  - Maximum Width: 220 PT (or 40% of content width)
  - Height: Minimum 65 PT (calculated based on text)

- **Parts:**
  - Minimum Width: 90 PT
  - Maximum Width: 120 PT (or calculated based on available space)
  - Height: Minimum 50 PT (calculated based on text)

- **Actors:**
  - Size: 45-55 PT (diameter)
  - Calculated as 7.5% of content width (minimum 45 PT)

### **Text-Based Sizing:**
- Font Size: 11 PT (default)
- Text width estimation: ~6-7 pixels per character at 11pt font
- Element width = text width + 20-30 PT padding
- Element height = text height + 15-20 PT padding

---

## 📍 **POSITIONING RULES**

### **Full Combined Diagram Layout:**

#### **Layout Zones:**
1. **Use Cases Zone:**
   - Position: **Center area** (40% from top of content area)
   - Arrangement: **Horizontal row**
   - Alignment: **Centered horizontally**
   - Spacing: 40 PT between use cases (reduced if too wide)

2. **Actors Zone:**
   - **Left Side Actors:**
     - Position: Left side (15% from left edge)
     - Arrangement: **Vertical stack**
     - Alignment: Aligned with connected use cases (if applicable)
   - **Right Side Actors:**
     - Position: Right side (15% from right edge)
     - Arrangement: **Vertical stack**
     - Alignment: Aligned with connected use cases (if applicable)
   - Spacing: 70 PT between actors vertically

3. **Parts Zone:**
   - Position: **Bottom area** (85% from top of content area)
   - Arrangement: **Horizontal row**
   - Alignment: **Centered horizontally**
   - Spacing: 25 PT between parts (reduced if too wide)

4. **System Boundary:**
   - Position: Outer container
   - Margin: 8% from slide edges
   - Extra space: 40 PT at top for title
   - Contains all elements

### **Individual Relationship Diagram Layout:**

1. **Use Case Position:**
   - Location: **Center-right area**
   - X: Slightly right of center (SLIDE_WIDTH/2 + 15% of available width)
   - Y: Slightly above center (SLIDE_HEIGHT/2 - 10% of available height)
   - Shape: Large Oval

2. **Actor Position:**
   - Location: **On Use Case Oval's RIGHT EDGE** (as a port)
   - X: Right edge of Use Case oval
   - Y: Vertical center of Use Case oval
   - Shape: Small Circle (port)
   - Anchored to Use Case edge

3. **Part Position:**
   - Location: **Bottom-left area** (peripheral position)
   - X: Left margin + 30 PT
   - Y: Bottom area (SLIDE_HEIGHT - margin - height - 30 PT)
   - Shape: Rectangle

4. **Connection Arrow:**
   - From: Closest edge of Part Rectangle
   - To: Center of Actor Circle
   - Style: Arrow with arrowhead

### **Aspect Ratio:**
- **Individual Relationship Diagrams:** Must fit within **16:9 aspect ratio**
- Slide dimensions: 720 PT width × 540 PT height (standard 4:3, but content fits 16:9)

---

## 🎨 **COLOR RULES**

### **Background Colors:**
- **Parts (Rectangles):** White (RGB: 1.0, 1.0, 1.0)
- **Actors (Circles):** Light Yellow (RGB: 1.0, 0.98, 0.77)
- **Use Cases (Ovals):** White (RGB: 1.0, 1.0, 1.0)
- **Subject (Round Rectangles):** Light Green (RGB: 0.78, 0.90, 0.79)
- **System Boundary:** Light Gray (RGB: 0.95, 0.95, 0.95)

### **Border Colors:**
- **All Elements:** Black (RGB: 0.0, 0.0, 0.0)
- **System Boundary:** Dark Gray (RGB: 0.2, 0.2, 0.2)

### **Border Weight:**
- **All Elements:** 2 PT (thicker border for visibility)
- **System Boundary:** 2 PT

### **Text Colors:**
- **All Elements:** Black (default)
- **System Boundary:** Black (bold)

---

## 🔗 **CONNECTION/ARROW RULES**

### **Arrow Style:**
- **Color:** Black (RGB: 0.0, 0.0, 0.0)
- **Stroke Width:** 2 PT
- **Arrowhead:** Filled arrow at target end
- **Line Type:** Straight line

### **Connection Points:**
- **Individual Relationship Diagrams:**
  - Uses **connection sites** (0-7) for unbreakable arrows
  - Connection sites: 0=Top, 1=Right, 2=Bottom, 3=Left, etc.
  - Arrow from: Closest edge of Part Rectangle
  - Arrow to: Center of Actor Circle (on Use Case edge)

- **Full Combined Diagrams:**
  - Calculates edge points dynamically
  - From: Closest edge of source element
  - To: Closest edge of target element

### **Connection Representation:**
- Each `connect X to Y` statement = One arrow
- Part (Rectangle) → Actor (Circle/Port on Use Case Oval)
- Arrow shows relationship direction

---

## 📐 **SPACING RULES**

### **Minimum Spacing:**
- **Between Nodes:** 80 PT minimum (in graph layout)
- **Node Padding:** 20 PT around nodes
- **Use Case Spacing:** 40 PT (horizontal)
- **Part Spacing:** 25 PT (horizontal)
- **Actor Spacing:** 70 PT (vertical)

### **Margins:**
- **Slide Margins:** 50 PT from edges
- **System Boundary Margin:** 8% of slide width
- **Content Padding:** 40 PT inside system boundary
- **Title Space:** 70-90 PT at top for system boundary title

### **Collision Detection:**
- **Overlap Prevention:** Elements must not overlap
- **Minimum Distance:** (width1 + width2)/2 + padding
- **Adjustment:** If overlap detected, elements pushed apart
- **Iterations:** Up to 50 iterations to resolve overlaps

---

## 📝 **TEXT RULES**

### **Font Sizes:**
- **Parts:** 11 PT (not bold)
- **Actors:** 10 PT (not bold)
- **Use Cases:** 11 PT (not bold)
- **Subject:** 11 PT (not bold)
- **System Boundary:** 14 PT (**bold**)

### **Text Alignment:**
- **All Elements:** Middle/Center alignment
- **Text Position:** Centered within shape

### **Text Content:**
- **Parts:** Part name (from `name` field)
- **Actors:** Actor name (from `name` field)
- **Use Cases:** Use case name (from `name` field)
- **System Boundary:** System name (top-level part name)

---

## 🔄 **LAYOUT ALGORITHM RULES**

### **Layout Algorithm Selection:**
1. **Hierarchical Layout** (Default for full diagrams)
   - Use cases: Center-top (horizontal)
   - Components: Arranged around (left, right, bottom)
   - Professional SysML-style organization

2. **Force-Directed Layout** (Alternative)
   - Uses NetworkX spring layout
   - Iterations: 100+ for refinement
   - Simulates physical forces (attraction/repulsion)

3. **Individual Relationship Layout** (Specialized)
   - Use Case: Center-right (Oval)
   - Actor: Circle on Use Case edge (Port)
   - Part: Bottom-left (Rectangle)

4. **Simple Layout** (For 2-3 nodes)
   - 2 nodes: Horizontal layout
   - 3 nodes: Triangular layout

### **Scaling Rules:**
- All positions scaled to fit within slide bounds
- Maintains aspect ratio
- Ensures all elements are visible
- Generous margins applied

---

## 📊 **DIAGRAM SPLITTING RULES**

### **Relationship Splitting:**
1. **Full Combined Diagram:**
   - Contains ALL elements and ALL relationships
   - One slide with complete system view

2. **Individual Relationship Diagrams:**
   - One diagram per relationship/connection
   - Each shows: Part → Actor → Use Case
   - Focused view of single relationship

### **Element Context Discovery:**
- For each connection, identifies:
  - **Source Part:** Structural component (Rectangle)
  - **Target Actor:** External entity (Circle/Port)
  - **Use Case:** Functional node (Oval)
- Uses relationship context to map correctly

---

## ✅ **VALIDATION RULES**

### **Data Extraction Rules (LLM Prompt):**
1. Extract ALL parts (both "part def" and nested "part" declarations)
2. Mark top-level parts with `"is_top_level": true`
3. Mark nested parts with `"is_top_level": false` and set their `"parent"`
4. Extract ALL actors (declared with "actor" keyword)
5. Extract ALL use cases (declared with "use case" keyword)
6. Extract objectives from use cases
7. Extract ALL "connect X to Y" statements as connections
8. Build hierarchy mapping parent names to arrays of child names
9. Extract documentation from "doc" comments if present
10. Return ONLY JSON object, no additional text

### **Connection Validation:**
- All connections are kept (even if they reference actors)
- Warns if connection references unknown elements
- Connections may reference parts or actors

---

## 🎯 **INDIVIDUAL RELATIONSHIP DIAGRAM SPECIFIC RULES**

### **Element Mapping:**
- **Use Case** → Large Oval (Center position)
- **Part** → Rectangle (Peripheral position)
- **Actor** → Small Circle (Port) anchored to Use Case Oval's edge
- **Connection:** Arrow from closest edge of Part Rectangle to center of Actor Circle

### **Size Requirements:**
- All shapes and connections should be **medium-sized**
- Must fit within **16:9 aspect ratio**

### **Position Requirements:**
- Use Case: Center-right area
- Actor: On Use Case Oval's RIGHT EDGE (as port)
- Part: Bottom-left (peripheral)
- Arrow: From Part edge to Actor center

---

## 🔧 **TECHNICAL RULES**

### **Slide Dimensions:**
- **Width:** 720 PT (standard Google Slides width)
- **Height:** 540 PT (standard Google Slides height)
- **Aspect Ratio:** 4:3 (but content fits 16:9)

### **Object ID Naming:**
- **Parts:** `comp_{page_id}_{name}` (max 50 chars)
- **Actors:** `actor_{page_id}_{name}` (max 50 chars)
- **Use Cases:** `uc_{page_id}_{name}` (max 50 chars)
- **Subject:** `subject_{page_id}_{name}` (max 50 chars)
- **System Boundary:** `sys_{page_id}_{name}` (max 50 chars)

### **Element ID Metadata:**
- Each shape stores `element_id` for feedback extraction
- Mapping: `shape_id → element_id`
- Saved to `element_mapping.json`

---

## 📋 **SUMMARY CHECKLIST**

### **Shape Types:**
- ✅ Parts = Rectangles (white)
- ✅ Actors = Circles (light yellow)
- ✅ Use Cases = Ovals (white)
- ✅ Subject = Round Rectangles (light green)
- ✅ System Boundary = Large Rectangle (light gray)

### **Layout:**
- ✅ Use Cases: Center (horizontal row)
- ✅ Actors: Left/Right sides (vertical stacks)
- ✅ Parts: Bottom (horizontal row)
- ✅ Individual: Use Case center-right, Actor on edge, Part bottom-left

### **Colors:**
- ✅ All borders: Black (2 PT)
- ✅ Backgrounds: Element-specific colors
- ✅ Text: Black (11pt, except system boundary 14pt bold)

### **Connections:**
- ✅ Arrows: Black, 2 PT, filled arrowhead
- ✅ From: Edge of source element
- ✅ To: Edge/center of target element

### **Spacing:**
- ✅ Minimum 80 PT between nodes
- ✅ Margins: 50 PT from slide edges
- ✅ No overlaps allowed

---

These are ALL the predefined rules for diagram generation in this project!

