# Connection Sites Update: Unbreakable Arrows for Individual Relationship Diagrams

## 📋 Overview

Updated the `visualize_sysml.py` script to use **connection sites (glue points)** for arrows in Individual Relationship Diagrams (Slide 2+). This ensures arrows remain attached to shapes when users move them in Google Slides.

## ✅ What Changed

### **1. New Method: `_draw_arrow_with_connection_sites()`**

Added a new method that creates unbreakable connections using Google Slides API's connection sites feature.

**Key Features:**
- Uses `createLine` with `startConnectionSite` and `endConnectionSite`
- Automatically determines optimal connection points based on element positions
- Arrows automatically re-route when shapes are moved
- Only applies to **Individual Relationship Diagrams** (Slide 2+)

### **2. Updated `render_diagram()` Method**

Modified to use the new connection sites method for individual relationship diagrams:
- **Full Combined Diagram (Slide 1)**: Uses legacy `_draw_arrow()` method
- **Individual Relationship Diagrams (Slide 2+)**: Uses `_draw_arrow_with_connection_sites()` method

## 🔧 Technical Details

### **Connection Sites Mapping**

Connection sites are predefined points on shapes:
- **0** = Top
- **1** = Right
- **2** = Bottom
- **3** = Left
- **4** = Top-Left corner
- **5** = Top-Right corner
- **6** = Bottom-Right corner
- **7** = Bottom-Left corner

### **Connection Site Selection Logic**

The code automatically selects connection sites based on the relative positions of source and target elements:

```python
# Horizontal connections
if abs(dx) > abs(dy):
    start_site = 1 if dx > 0 else 3  # Right or Left
    end_site = 3 if dx > 0 else 1    # Left or Right

# Vertical connections
else:
    start_site = 2 if dy > 0 else 0  # Bottom or Top
    end_site = 0 if dy > 0 else 2    # Top or Bottom
```

### **API Structure**

```python
{
    'createLine': {
        'objectId': conn_id,
        'elementProperties': {
            'pageObjectId': page_id,
            'line': {
                'lineCategory': 'STRAIGHT_LINE',
                'lineFill': {...},
                'weight': {'magnitude': 2, 'unit': 'PT'},
                'startArrow': 'NONE',
                'endArrow': 'ARROW'
            }
        },
        'startConnectionSite': {
            'connectedObjectId': from_id,
            'connectionSiteIndex': start_site
        },
        'endConnectionSite': {
            'connectedObjectId': to_id,
            'connectionSiteIndex': end_site
        }
    }
}
```

## 📊 Element Mapping (Maintained)

The mapping remains consistent with the requirements:

- **Use Case** → Large Oval (Ellipse) - Center position
- **Part** → Rectangle - Peripheral position
- **Actor** → Small Circle (Ellipse with equal dimensions) - Port position, anchored to Oval's edge

## 🎯 What This Means

### **Before (Legacy Method):**
- Arrows were drawn as separate shapes (rectangles + triangles)
- Moving shapes would disconnect arrows
- Manual reconnection required

### **After (Connection Sites Method):**
- Arrows are connected using glue points
- Moving shapes automatically re-routes arrows
- Arrows stay attached at all times
- Professional, maintainable diagrams

## 🔄 Bidirectional Flow Maintained

✅ **All existing functionality preserved:**
- Full combined diagram (Slide 1) still works
- Individual relationship diagrams (Slide 2+) now use connection sites
- Feedback extraction still works
- Element mapping still works
- No breaking changes

## 📝 Usage

### **Generate Slides with Connection Sites:**

```bash
python visualize_sysml.py OpsCon.json
```

**Result:**
- **Slide 1**: Full combined diagram (legacy arrows)
- **Slide 2+**: Individual relationship diagrams (unbreakable arrows with connection sites)

### **Example Individual Relationship Diagram:**

For a relationship like `Aircraft → CandidateAircraft`:
- **Aircraft** (Rectangle) connected via connection site
- **CandidateAircraft** (Circle/Actor) connected via connection site
- Arrow automatically stays attached when either shape is moved

## ✅ Requirements Met

- ✅ Use connection sites (glue points) for arrows
- ✅ Unbreakable connections (arrows stay attached)
- ✅ Only applies to Individual Relationship Diagrams
- ✅ Maintains bidirectional flow
- ✅ Normal-sized shapes (no changes to size calculations)
- ✅ Proper element mapping (Use Case → Oval, Part → Rectangle, Actor → Circle)

## 🧪 Testing

To test the connection sites:

1. Generate slides: `python visualize_sysml.py OpsCon.json`
2. Open the Google Slides presentation
3. Navigate to Slide 2+ (individual relationship diagrams)
4. Try moving a shape (e.g., "Aircraft" rectangle)
5. Verify the arrow automatically re-routes and stays attached

## 📚 References

- Google Slides API: [CreateLineRequest](https://developers.google.com/slides/api/reference/rest/v1/presentations/request#CreateLineRequest)
- Connection Sites: Predefined attachment points on shapes (0-7 indices)


