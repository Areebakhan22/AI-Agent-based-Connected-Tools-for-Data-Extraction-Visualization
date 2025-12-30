# Fixes Applied Summary

## ✅ Implemented Fixes

### 1. **Dynamic Use Case Discovery** (`find_relationship_context`)

**Location**: `RelationshipSplitter.find_relationship_context()`

**What it does**:
- Takes a connection (e.g., `{"from": "Aircraft", "to": "CandidateAircraft"}`)
- Searches for which Use Case contains the target Actor
- Verifies types by checking actual lists (parts, actors, use_cases)
- Returns context with validated elements

**Logic**:
```python
1. Extract source_name (from) and target_name (to)
2. Verify target is in actors list → Actor ✅
3. Verify source is in parts list → Part ✅
4. Find Use Case that connects to the Actor:
   - Check connections: UseCase → Actor
   - If found: Use that Use Case
   - If not: Use first Use Case as fallback
5. Return: {container_oval, port_circle, source_rect, is_valid}
```

### 2. **Explicit Type Validation**

**Location**: `RelationshipSplitter.find_relationship_context()` and `calculate_layout()`

**What it does**:
- **Before**: Assumed `from` = Part, `to` = Actor
- **After**: Explicitly checks:
  ```python
  # Check if source is in parts list
  source_part = next((p for p in sysml_data.get('parts', []) if p['name'] == source_name), None)
  
  # Check if target is in actors list
  target_actor = next((a for a in sysml_data.get('actors', []) if a['name'] == target_name), None)
  ```

**Result**: No more guessing - types are verified from actual data

### 3. **Fixed Dimensions (EMU-based)**

**Location**: `_individual_relationship_layout()`

**Dimensions**:
- **Use Case Oval**: 
  - Width: 3,000,000 EMU (~236 points)
  - Height: 1,500,000 EMU (~118 points)
  - Position: X: 3,072,000 EMU (centered), Y: 1,000,000 EMU

- **Part Rectangle**: 
  - Width: 2,000,000 EMU (~157 points)
  - Height: 1,000,000 EMU (~79 points)
  - Position: X: 3,572,000 EMU (centered), Y: 3,500,000 EMU

- **Actor Circle**: 
  - Diameter: 500,000 EMU (~39 points)
  - Position: Calculated to sit on right edge of Use Case Oval

### 4. **Connection Anchoring**

**Location**: `_draw_arrow_with_connection_sites()`

**Connection Sites**:
- **Start**: Part Rectangle at `connectionSiteIndex: 0` (Top-middle)
- **End**: Actor Circle at `connectionSiteIndex: 0` (Center)

**Note**: Google Slides API doesn't support true "glued" connections, but we calculate connection points based on these indices for accurate positioning.

### 5. **One Slide Per Connection**

**Location**: `split_by_relationships()`

**Process**:
1. Creates Slide 1: Full combined diagram
2. For each connection in `connections` array:
   - Creates individual slide
   - Extracts only relevant elements (Part, Actor, Use Case)
   - Uses `find_relationship_context()` for accurate mapping

## 📊 Current Flow

### For Connection: `{"from": "Aircraft", "to": "CandidateAircraft"}`

1. **Extract Context**:
   ```python
   context = find_relationship_context(connection, sysml_data)
   # Returns:
   {
     "container_oval": "InspectAircraftAutomatically",
     "port_circle": "CandidateAircraft",
     "source_rect": "Aircraft",
     "is_valid": True
   }
   ```

2. **Verify Types**:
   - ✅ "Aircraft" is in `parts` list → Part (Rectangle)
   - ✅ "CandidateAircraft" is in `actors` list → Actor (Circle)
   - ✅ "InspectAircraftAutomatically" is in `use_cases` list → Use Case (Oval)

3. **Layout**:
   - Use Case Oval: Center-top (fixed EMU position)
   - Actor Circle: Right edge of Use Case Oval
   - Part Rectangle: Bottom-center (fixed EMU position)

4. **Connection**:
   - Arrow from Part Rectangle top-middle → Actor Circle center
   - Uses connection site indices for positioning

## ⚠️ Known Limitations

1. **Google Slides API**: Doesn't support true "glued" connection sites. We calculate connection points based on indices, but arrows won't automatically re-route if shapes are moved manually.

2. **Use Case Discovery**: Currently uses first Use Case as fallback if no direct connection found. In real SysML, actors are scoped within use cases, so this should work for most cases.

3. **EMU Conversion**: Dimensions are converted from EMU to points for layout calculations, then back to points for API calls.

## ✅ What's Working

- ✅ Dynamic Use Case discovery
- ✅ Explicit type validation
- ✅ Fixed dimensions (EMU-based)
- ✅ Connection site-based arrow positioning
- ✅ One slide per connection
- ✅ Only relevant elements per slide (Part, Actor, Use Case)

## 🔄 Next Steps (If Needed)

1. **True Connection Sites**: If Google Slides API adds support for glued connections, update `_draw_arrow_with_connection_sites()` to use actual connection site API.

2. **Better Use Case Discovery**: If SysML structure includes actor scoping within use cases, enhance `find_relationship_context()` to parse that structure.

3. **Validation**: Add more validation to ensure relationships make sense (e.g., Part → Actor, not Actor → Part).









