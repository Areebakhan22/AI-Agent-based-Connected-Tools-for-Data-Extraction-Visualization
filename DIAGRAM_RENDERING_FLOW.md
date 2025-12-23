# Diagram Rendering Flow: From JSON to Visual Diagrams

## Overview
This document explains how diagrams are drawn from JSON data, keeping in mind the universal SysML rules and reference patterns.

---

## Step 1: JSON Data Structure (`react_diagrams.json`)

### Input Format
```json
{
  "system_name": "OpsCon_UAV_basedAircraftInspection",
  "diagrams": [
    {
      "id": "rel_3",
      "title": "Aircraft → CandidateAircraft",
      "nodes": [
        {
          "id": "part_Aircraft",
          "name": "Aircraft",
          "type": "part",        // Will be converted to actor if needed
          "width": 140,
          "height": 60,
          "x": 138.4,           // Initial position (may be recalculated)
          "y": 320
        },
        {
          "id": "part_CandidateAircraft",
          "name": "CandidateAircraft",
          "type": "part",        // Will be converted to "actor"
          ...
        },
        {
          "id": "usecase_InspectAircraftAutomatically",
          "name": "InspectAircraftAutomatically",
          "type": "use_case",
          ...
        },
        {
          "id": "soi",
          "name": "SoI",
          "type": "soi"          // Will be filtered out in individual diagrams
        }
      ],
      "links": [
        {
          "source": "part_Aircraft",
          "target": "part_CandidateAircraft",
          "fromName": "Aircraft",
          "toName": "CandidateAircraft"
        }
      ],
      "metadata": {
        "is_full_diagram": false,
        "system_boundary": "OpsCon_UAV_basedAircraftInspection",
        "relationship": {
          "from": "Aircraft",
          "to": "CandidateAircraft"
        }
      }
    }
  ]
}
```

---

## Step 2: Frontend Data Loading (`InteractiveDiagram.jsx`)

### Process Flow:

1. **API Call**: `apiClient.getDiagram(diagramId)`
   - Fetches diagram data from backend
   - Returns JSON from `react_diagrams.json`

2. **Data Processing** (Lines 48-144):
   
   **a) Node Type Identification:**
   ```javascript
   // Collect actor names from connections
   const actorNames = new Set()
   data.links.forEach(link => {
     if (link.toName && link.toName !== 'SoI') {
       actorNames.add(link.toName)  // "CandidateAircraft"
     }
   })
   ```

   **b) Convert Parts to Actors:**
   ```javascript
   // If node name matches actor name and is currently a part
   if (actorNames.has(node.name) && node.type === 'part') {
     node.type = 'actor'           // Convert to actor
     node.size = 40
     node.isHandle = true          // Mark as handle on use case
   }
   ```

   **c) Filter Individual Diagrams:**
   ```javascript
   if (isIndividualDiagram) {
     // Remove SoI from individual relationship diagrams
     data.nodes = data.nodes.filter(node => node.type !== 'soi')
     
     // Fix connections: Part → Use Case with targetHandle
     if (targetNode.type === 'actor') {
       link.target = useCaseNode.id
       link.targetHandle = targetNode.name  // "CandidateAircraft"
     }
   }
   ```

3. **Result**: Cleaned data structure with:
   - Correct node types (part, actor, use_case)
   - Filtered elements (no SoI in individual diagrams)
   - Updated connections (Part → Use Case with targetHandle)

---

## Step 3: Layout Calculation (`d3Renderer.js` - `calculateSysMLLayout`)

### Box/Area Structure:

```javascript
// Define box areas for proper alignment
const upperRegion = {
  top: margin + 30,
  bottom: centerY * 0.6,
  left: margin,
  right: width - margin
}

const lowerRegion = {
  top: centerY * 0.6,
  bottom: height - margin - 30,
  left: margin,
  right: width - margin
}
```

### Element Positioning Logic:

**1. Use Case (Level 1):**
```javascript
// Individual diagrams: center-right
// Full diagrams: center horizontally
if (isIndividual) {
  uc.x = centerX + 100  // Center-right
  uc.y = centerY        // Vertical center
} else {
  uc.x = centerX        // Centered
  uc.y = (upperRegion.top + upperRegion.bottom) / 2
}
```

**2. Actors (Level 2) - Handles on Use Case Right Edge:**
```javascript
// Calculate position on ellipse perimeter (right edge)
const angle = Math.asin(clampedY)
const edgeX = useCaseX + useCaseRx * Math.cos(angle)
const edgeY = useCaseY + useCaseRy * Math.sin(angle)

// Position handle ON the edge (40% overlap)
actor.x = edgeX + normalX * (handleRadius * 0.4)
actor.y = edgeY + normalY * (handleRadius * 0.4)
```

**3. Parts (Level 3) - Bottom-Left:**
```javascript
// Individual diagrams: single part in bottom-left
if (isIndividual && totalParts === 1) {
  part.x = margin + 120      // Left side
  part.y = height - margin - 100  // Bottom area
}
```

**4. SoI (Level 4) - Top-Right (Full Diagrams Only):**
```javascript
soi.x = rightBox.left + (rightBox.right - rightBox.left) * 0.7
soi.y = rightBox.top + (rightBox.bottom - rightBox.top) * 0.3
```

---

## Step 4: Shape Rendering (`d3Renderer.js` - `render` method)

### Rendering Order:

**1. System Boundary (Level 0):**
```javascript
drawSystemBoundary()
// Draws outer rectangle with gradient fill
// Adds system name in top-left corner
```

**2. Links (Connections):**
```javascript
// Create smoothstep paths (L-shaped)
link.attr('d', d => {
  return createSmoothstepPath(d.source, d.target, d.targetHandle)
})
```

**3. Nodes (Shapes):**
```javascript
node.each(function(d) {
  if (d.type === 'use_case') {
    // Draw ellipse (blue gradient, 4px border)
  } else if (d.type === 'actor') {
    // Draw circle (yellow/orange, 40px, on use case edge)
  } else if (d.type === 'part') {
    // Draw rectangle (white fill, green border, 160x70px)
  } else if (d.type === 'soi') {
    // Draw rectangle (green gradient, purple border)
  }
  
  // Add text label (centered, bold)
})
```

---

## Step 5: Connection Path Creation (`createSmoothstepPath`)

### Path Logic:

**For Individual Diagrams (Part → Use Case):**
```javascript
// Start: Part bottom-right corner
startX = source.x + source.width / 2   // Right edge
startY = source.y + source.height / 2  // Bottom edge

// End: Use Case bottom-left edge
endX = target.x - target.width / 2     // Left edge
endY = target.y + target.height / 2    // Bottom edge

// L-shaped path (horizontal then vertical)
return `M ${startX} ${startY} 
        L ${endX} ${startY} 
        L ${endX} ${endY}`
```

**For Full Diagrams (Part → Actor Handle):**
```javascript
// If targetHandle provided, use actor handle position
if (targetHandle) {
  const actorHandle = nodes.find(n => n.type === 'actor' && n.name === targetHandle)
  endX = actorHandle.x
  endY = actorHandle.y
}
```

---

## Key Rules Applied:

### 1. **Context Identification (Dynamic)**
- **System Boundary**: Identified from `is_top_level` or name pattern
- **Use Case**: From `type === 'use_case'`
- **Actors**: Converted from parts based on connection targets
- **Parts**: Physical entities (exclude system boundary)

### 2. **Hierarchical Drawing Order**
- **Level 0**: System Boundary (outer container)
- **Level 1**: Use Case (oval, upper region)
- **Level 2**: Actor Handles (circles, on use case right edge)
- **Level 3**: Parts (rectangles, lower-left)
- **Level 4**: SoI (rectangles, upper-right, full diagrams only)

### 3. **Connection Logic**
- **Individual Diagrams**: Part → Use Case (L-shaped, bottom-right to bottom-left)
- **Full Diagrams**: Part → Use Case with targetHandle (Actor name)
- **Sticky Integrity**: targetHandle explicitly linked to actor handle position

### 4. **Visual Hierarchy**
- **Use Cases**: Blue gradient oval, 280x90px, 4px border
- **Actors**: Yellow/orange circles, 40px, on use case right edge
- **Parts**: White rectangles, 160x70px, green border
- **SoI**: Green gradient, purple border (full diagrams only)

---

## Complete Flow Diagram:

```
react_diagrams.json
    ↓
[Backend API] → GET /api/diagram/:id
    ↓
[InteractiveDiagram.jsx]
    ├─ Load data from API
    ├─ Identify actors from connections
    ├─ Convert parts to actors
    ├─ Filter SoI (individual diagrams)
    └─ Fix connections (Part → Use Case with targetHandle)
    ↓
[D3DiagramRenderer.render()]
    ├─ calculateSysMLLayout()
    │   ├─ Define box areas (upper/lower regions)
    │   ├─ Position Use Case (center-right for individual)
    │   ├─ Position Actors (on use case right edge)
    │   ├─ Position Parts (bottom-left)
    │   └─ Position SoI (top-right, full diagrams only)
    │
    ├─ drawSystemBoundary()
    │   └─ Draw outer container with system name
    │
    ├─ Draw Links
    │   └─ createSmoothstepPath() → L-shaped connections
    │
    └─ Draw Nodes
        ├─ Use Case: Ellipse (blue gradient)
        ├─ Actors: Circles (yellow/orange, on oval edge)
        ├─ Parts: Rectangles (white, green border)
        └─ SoI: Rectangles (green gradient, purple border)
    ↓
[SVG Output] → High-quality, interactive diagram
```

---

## Important Notes:

1. **Dynamic Identification**: No hardcoded values - all elements identified from JSON structure
2. **Individual vs Full**: Different filtering and positioning logic
3. **Actor Conversion**: Parts are converted to actors based on connection analysis
4. **Box Alignment**: Elements positioned in defined box areas for proper structure
5. **Connection Paths**: L-shaped (smoothstep) paths matching reference
6. **Sticky Integrity**: targetHandle ensures connections stay linked to actor handles

---

## Example: "Aircraft → CandidateAircraft" Individual Diagram

**Input JSON:**
- `part_Aircraft` (type: "part")
- `part_CandidateAircraft` (type: "part") 
- `usecase_InspectAircraftAutomatically` (type: "use_case")
- `soi` (type: "soi") ← **Filtered out**

**Processing:**
1. Identify `CandidateAircraft` as actor (from connection target)
2. Convert `part_CandidateAircraft` → `actor_CandidateAircraft`
3. Filter out `soi` node
4. Update link: `Aircraft` → `InspectAircraftAutomatically` (targetHandle: "CandidateAircraft")

**Layout:**
- Aircraft: (120, 440) - bottom-left
- Use Case: (580, 270) - center-right
- CandidateAircraft: (640, 270) - on use case right edge

**Rendering:**
- Aircraft: White rectangle with green border
- Use Case: Blue gradient oval
- CandidateAircraft: Yellow circle on oval edge
- Connection: L-shaped path from Aircraft bottom-right → Use Case bottom-left

---

This flow ensures diagrams match the reference structure with proper alignment, colors, and connections.

