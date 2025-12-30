# How Individual Relationship Mappings Are Found

## Current Process Flow

### Step 1: Split by Relationships (`split_by_relationships`)

```python
# From OpsCon.json, we have 4 connections:
connections = [
    {"from": "Human", "to": "DroneOperator"},
    {"from": "Environment", "to": "InspectionEnvironment"},
    {"from": "Drone", "to": "SoI"},
    {"from": "Aircraft", "to": "CandidateAircraft"}
]
```

**What happens:**
- Creates **Slide 1**: Full combined diagram (all 4 connections)
- Creates **Slide 2**: Individual diagram for connection 1 (`Human → DroneOperator`)
- Creates **Slide 3**: Individual diagram for connection 2 (`Environment → InspectionEnvironment`)
- Creates **Slide 4**: Individual diagram for connection 3 (`Drone → SoI`)
- Creates **Slide 5**: Individual diagram for connection 4 (`Aircraft → CandidateAircraft`)

### Step 2: Extract Elements for Each Relationship (`_extract_relationship_elements`)

**Current Logic:**
```python
def _extract_relationship_elements(model, connection):
    from_elem = connection.get('from')  # e.g., "Aircraft"
    to_elem = connection.get('to')      # e.g., "CandidateAircraft"
    
    # Only extracts the TWO elements directly in the connection
    # Does NOT identify which is Part vs Actor
    # Does NOT include Use Case automatically
```

**For connection `{"from": "Aircraft", "to": "CandidateAircraft"}`:**
- Extracts: `Aircraft` (from) and `CandidateAircraft` (to)
- **Problem**: Doesn't know `Aircraft` is a Part and `CandidateAircraft` is an Actor
- **Problem**: Doesn't include the Use Case (`InspectAircraftAutomatically`)

### Step 3: Identify Element Types (in `calculate_layout`)

**Current Logic:**
```python
# In calculate_layout, for individual diagrams:
from_type = element_types.get(from_elem, 'part')  # Defaults to 'part'
to_type = element_types.get(to_elem, 'actor')     # Defaults to 'actor'
```

**Issues:**
1. **Type identification is guesswork**: 
   - Assumes `from` is always a Part
   - Assumes `to` is always an Actor
   - This might be wrong!

2. **Use Case is added manually**:
   ```python
   # Always adds the FIRST use case, not necessarily the correct one
   associated_uc = use_cases[0].get('name')  # Always "InspectAircraftAutomatically"
   ```

## Problems with Current Approach

### Problem 1: Type Identification
- **Current**: Assumes `from` = Part, `to` = Actor
- **Reality**: Could be `Part → Part`, `Actor → Actor`, `Part → UseCase`, etc.
- **Example**: `{"from": "Drone", "to": "SoI"}` - `SoI` is not an Actor!

### Problem 2: Use Case Selection
- **Current**: Always uses the first use case (`InspectAircraftAutomatically`)
- **Reality**: Should find the Use Case that's actually related to the Actor
- **Example**: For `Aircraft → CandidateAircraft`, we need to find which Use Case uses `CandidateAircraft`

### Problem 3: Missing Context
- **Current**: Only extracts the two connected elements
- **Reality**: Should understand the relationship context:
  - Which Use Case does the Actor belong to?
  - Is the connection Part → Actor, or something else?

## What Should Happen

### Correct Mapping Logic:

For each `connect X to Y` statement:

1. **Identify Source and Target Types**:
   - Check if `X` is in `parts` list → It's a Part
   - Check if `X` is in `actors` list → It's an Actor
   - Check if `X` is in `use_cases` list → It's a Use Case
   - Same for `Y`

2. **Find Associated Use Case**:
   - If target is an Actor, find which Use Case uses that Actor
   - Look for connections like `UseCase → Actor` or `Actor → UseCase`
   - If no direct connection, use the Use Case that's in the same scope

3. **Extract All Three Elements**:
   - Part (source)
   - Actor (target)
   - Use Case (context)

## Example: `Aircraft → CandidateAircraft`

**Current Process:**
1. Extract: `Aircraft` and `CandidateAircraft`
2. Assume: `Aircraft` = Part, `CandidateAircraft` = Actor
3. Add: First Use Case (`InspectAircraftAutomatically`)
4. Result: ✅ Works by accident, but not systematic

**Correct Process Should Be:**
1. Identify: `Aircraft` is in `parts` → Part ✅
2. Identify: `CandidateAircraft` is in `actors` → Actor ✅
3. Find Use Case: Look for connections involving `CandidateAircraft`
   - Check: Is there `InspectAircraftAutomatically → CandidateAircraft`?
   - Or: Is `CandidateAircraft` defined within `InspectAircraftAutomatically` scope?
4. Extract: Part (`Aircraft`), Actor (`CandidateAircraft`), Use Case (`InspectAircraftAutomatically`)

## Summary

**Current Method:**
- ✅ Splits connections correctly (one slide per connection)
- ⚠️ Type identification is guesswork (assumes from=Part, to=Actor)
- ⚠️ Use Case selection is arbitrary (always first use case)
- ⚠️ Doesn't verify the relationship makes sense

**What We Need:**
- ✅ Proper type identification (check actual lists)
- ✅ Smart Use Case selection (find related use case)
- ✅ Context-aware extraction (understand relationship semantics)









