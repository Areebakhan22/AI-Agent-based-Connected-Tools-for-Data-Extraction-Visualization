# Deep Dive: LLM (Ollama 3) Role in SysML Visualization Pipeline

## Complete Flow with LLM Deep Integration

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        PHASE 1: INPUT - SysML FILE                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────┐
    │   OpsCon.sysml                  │
    │   (Raw Text File)                │
    │                                  │
    │   Contains:                      │
    │   • part def Human {...}         │
    │   • actor DroneOperator          │
    │   • use case InspectAircraft... │
    │   • connect Human to DroneOp... │
    │   • Nested structures            │
    │   • Documentation comments       │
    └────────────┬────────────────────┘
                 │
                 │ Raw SysML Text Content
                 │ (Complex, unstructured)
                 ▼

╔══════════════════════════════════════════════════════════════════════════════╗
║              PHASE 2: LLM-BASED PARSING (OLLAMA 3) - CORE PHASE             ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    llm_service.py                                   │
    │                    (LLM Orchestrator)                              │
    └────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  │ Step 1: Initialize LLM Connection
                                  ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  _check_ollama_connection()                                         │
    │  • Connects to Ollama server (localhost:11434)                     │
    │  • Verifies LLaMA 3 model availability                             │
    │  • Checks model files at:                                          │
    │    - /usr/share/ollama/.ollama/models/.../llama3                  │
    │    - /home/user/.ollama/models/.../llama3                          │
    │  • Returns: ✓ Model ready / ✗ Model not found                       │
    └────────────────────────────┬──────────────────────────────────────┘
                                  │
                                  │ Step 2: Prepare SysML Content
                                  ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  extract_sysml(sysml_content)                                       │
    │                                                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  _create_extraction_prompt()                                   │ │
    │  │                                                                │ │
    │  │  Creates comprehensive prompt with:                             │ │
    │  │  • Full SysML file content                                     │ │
    │  │  • Extraction instructions (structured)                         │ │
    │  │  • JSON schema requirements                                     │ │
    │  │  • Mapping rules (parts→components, actors→ports)              │ │
    │  │  • Relationship identification rules                           │ │
    │  │  • Hierarchy extraction rules                                   │ │
    │  │  • Documentation extraction rules                              │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    │                               │ Prepared Prompt                      │
    │                               ▼                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  SYSTEM PROMPT (Role Definition)                                │ │
    │  │  "You are a SysML v2 expert. Extract structured information   │ │
    │  │   from SysML files and return valid JSON only."              │ │
    │  └──────────────────────────────────────────────────────────────┘ │
    │                                                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  USER PROMPT (Task Definition)                                 │ │
    │  │  "Analyze this SysML v2 file and extract all structured info. │ │
    │  │                                                                │ │
    │  │  SysML Content:                                                │ │
    │  │  ```                                                           │ │
    │  │  [Full SysML file content here]                                │ │
    │  │  ```                                                           │ │
    │  │                                                                │ │
    │  │  Extract and return ONLY valid JSON with structure:            │ │
    │  │  {                                                             │ │
    │  │    "parts": [...],                                            │ │
    │  │    "actors": [...],                                           │ │
    │  │    "use_cases": [...],                                         │ │
    │  │    "connections": [...],                                       │ │
    │  │    "hierarchy": {...}                                         │ │
    │  │  }                                                             │ │
    │  │                                                                │ │
    │  │  Rules:                                                        │ │
    │  │  1. Extract ALL parts (both "part def" and nested "part")     │ │
    │  │  2. Mark top-level parts with "is_top_level": true             │ │
    │  │  3. Mark nested parts with parent relationships                │ │
    │  │  4. Extract ALL actors                                         │ │
    │  │  5. Extract ALL use cases with objectives                      │ │
    │  │  6. Extract ALL "connect X to Y" as connections                │ │
    │  │  7. Build hierarchy mapping                                   │ │
    │  │  8. Extract documentation from "doc" comments                 │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    │                               │ Complete Prompt Package             │
    │                               ▼                                      │
    └───────────────────────────────┼──────────────────────────────────────┘
                                    │
                                    │ Step 3: Send to Ollama API
                                    ▼
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                    OLLAMA API CALL (LLM Processing)                    ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                                                                        ║
    ║  ollama.chat(                                                          ║
    ║    model="llama3",  ← Local LLaMA 3 model files                      ║
    ║    messages=[                                                          ║
    ║      {role: "system", content: "SysML expert..."},                    ║
    ║      {role: "user", content: "[Full prompt]"}                         ║
    ║    ],                                                                  ║
    ║    options={                                                           ║
    ║      temperature: 0.1,  ← Low temp for structured output             ║
    ║      num_ctx: 1024,     ← Context window                             ║
    ║      num_predict: 300,  ← Max tokens to generate                     ║
    ║      num_gpu: 0          ← CPU mode (avoids GPU issues)                ║
    ║    }                                                                   ║
    ║  )                                                                     ║
    ║                                                                        ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                    LLM INTERNAL PROCESSING                            ║
    ╠═══════════════════════════════════════════════════════════════════════╣
    ║                                                                        ║
    ║  ┌────────────────────────────────────────────────────────────────┐  ║
    ║  │  STEP 1: Tokenization                                           │  ║
    ║  │  • Converts SysML text → tokens                                 │  ║
    ║  │  • Understands SysML keywords (part, actor, use case, etc.)   │  ║
    ║  └────────────────────────────────────────────────────────────────┘  ║
    ║                                                                        ║
    ║  ┌────────────────────────────────────────────────────────────────┐  ║
    ║  │  STEP 2: Semantic Understanding                                 │  ║
    ║  │  • Recognizes SysML v2 syntax patterns                          │  ║
    ║  │  • Understands structural relationships                          │  ║
    ║  │  • Identifies parent-child hierarchies                           │  ║
    ║  │  • Maps connections between elements                              │  ║
    ║  │  • Extracts implicit relationships                                │  ║
    ║  └────────────────────────────────────────────────────────────────┘  ║
    ║                                                                        ║
    ║  ┌────────────────────────────────────────────────────────────────┐  ║
    ║  │  STEP 3: Context Analysis                                        │  ║
    ║  │  • Analyzes nested structures                                    │  ║
    ║  │  • Determines which parts belong to which parents                │  ║
    ║  │  • Associates actors with use cases                                │  ║
    ║  │  • Links connections to their source/target elements              │  ║
    ║  │  • Extracts documentation from comments                           │  ║
    ║  └────────────────────────────────────────────────────────────────┘  ║
    ║                                                                        ║
    ║  ┌────────────────────────────────────────────────────────────────┐  ║
    ║  │  STEP 4: Structured Extraction                                 │  ║
    ║  │  • Identifies all parts (top-level and nested)                  │  ║
    ║  │  • Extracts actor definitions                                    │  ║
    ║  │  • Extracts use case definitions with objectives                 │  ║
    ║  │  • Maps all connections (from → to)                              │  ║
    ║  │  • Builds hierarchy tree structure                               │  ║
    ║  │  • Extracts documentation strings                                │  ║
    ║  └────────────────────────────────────────────────────────────────┘  ║
    ║                                                                        ║
    ║  ┌────────────────────────────────────────────────────────────────┐  ║
    ║  │  STEP 5: JSON Generation                                        │  ║
    ║  │  • Formats extracted data as JSON                                │  ║
    ║  │  • Validates JSON structure                                      │  ║
    ║  │  • Ensures all required fields present                           │  ║
    ║  │  • Returns structured output                                     │  ║
    ║  └────────────────────────────────────────────────────────────────┘  ║
    ║                                                                        ║
    ╚═══════════════════════════════════════════════════════════════════════╝
                                    │
                                    │ LLM Response (JSON)
                                    ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  LLM Response Format:                                                │
    │  ```json                                                             │
    │  {                                                                   │
    │    "parts": [                                                       │
    │      {                                                               │
    │        "name": "Human",                                             │
    │        "doc": "Human operator...",                                   │
    │        "parent": null,                                               │
    │        "is_top_level": false                                         │
    │      },                                                              │
    │      ...                                                             │
    │    ],                                                                │
    │    "actors": [...],                                                  │
    │    "use_cases": [...],                                               │
    │    "connections": [{"from": "Human", "to": "DroneOperator"}],        │
    │    "hierarchy": {"Parent": ["Child1", "Child2"]}                    │
    │  }                                                                   │
    │  ```                                                                 │
    └────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ Step 4: Parse LLM Response
                                 ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  _parse_llm_response(response)                                       │
    │  • Removes markdown code blocks (```json ... ```)                   │
    │  • Extracts JSON object from text                                   │
    │  • Handles edge cases (extra text, formatting)                      │
    │  • Returns: Parsed dictionary                                       │
    └────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ Step 5: Normalize Structure
                                 ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  _normalize_structure(data)                                          │
    │  • Validates all required fields                                    │
    │  • Ensures correct data types                                        │
    │  • Fills in missing relationships                                    │
    │  • Infers actors from connections if not explicitly defined         │
    │  • Builds complete element_types mapping                            │
    │  • Returns: Normalized, validated JSON                               │
    └────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ Final Structured JSON
                                 ▼

╔══════════════════════════════════════════════════════════════════════════════╗
║              PHASE 3: SEMANTIC ENRICHMENT (LLM CONTINUES)                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │  visualize_sysml.py → SemanticModelProcessor                        │
    │                                                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  understand_model(json_data)                                   │ │
    │  │                                                                │ │
    │  │  SECOND LLM CALL for semantic understanding:                   │ │
    │  │  • Analyzes extracted JSON structure                            │ │
    │  │  • Validates relationships                                      │ │
    │  │  • Maps elements to diagram types                              │ │
    │  │  • Identifies system boundary                                   │ │
    │  │  • Enriches with semantic metadata                              │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    │                               │ Semantic Analysis Prompt             │
    │                               ▼                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  LLM Prompt:                                                  │ │
    │  │  "Analyze JSON system model. Map:                             │ │
    │  │   • parts/actors → components                                  │ │
    │  │   • use_cases → functional_nodes                               │ │
    │  │   • connections → edges                                        │ │
    │  │                                                                │ │
    │  │  Return mappings and validations."                             │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    │                               │ LLM Response                        │
    │                               ▼                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  _enrich_with_semantics()                                    │ │
    │  │  • Adds element_types mapping:                                │ │
    │  │    - parts → 'part' (rectangles)                              │ │
    │  │    - actors → 'actor' (circles)                               │ │
    │  │    - use_cases → 'functional_node' (ovals)                     │ │
    │  │    - SoI → 'subject' (round rectangles)                      │ │
    │  │  • Identifies system boundary                                 │ │
    │  │  • Validates relationships                                    │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    └───────────────────────────────┼──────────────────────────────────────┘
                                    │
                                    │ Enriched JSON with Semantic Metadata
                                    ▼

╔══════════════════════════════════════════════════════════════════════════════╗
║              PHASE 4: RELATIONSHIP SPLITTING (LLM-ASSISTED)                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │  RelationshipSplitter → split_by_relationships()                      │
    │                                                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  find_relationship_context(connection, sysml_data)             │ │
    │  │                                                                │ │
    │  │  LLM-ASSISTED CONTEXT DISCOVERY:                               │ │
    │  │  • Analyzes connection: "Human → DroneOperator"               │ │
    │  │  • Identifies source type: Part (Human)                       │ │
    │  │  • Identifies target type: Actor (DroneOperator)              │ │
    │  │  • Finds associated Use Case dynamically                       │ │
    │  │  • Validates relationship structure                             │ │
    │  │  • Returns:                                                    │ │
    │  │    {                                                           │ │
    │  │      "container_oval": "InspectAircraftAutomatically",       │ │
    │  │      "port_circle": "DroneOperator",                          │ │
    │  │      "source_rect": "Human",                                  │ │
    │  │      "is_valid": true                                         │ │
    │  │    }                                                           │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    │                               │ Context-Aware Relationship Data     │
    │                               ▼                                      │
    │  ┌──────────────────────────────────────────────────────────────┐ │
    │  │  Creates sub-models:                                          │ │
    │  │  • Full combined diagram (all relationships)                 │ │
    │  │  • Individual relationship diagrams (one per connection)      │ │
    │  │  • Each with proper element context                           │ │
    │  └────────────────────────────┬───────────────────────────────────┘ │
    │                               │                                      │
    └───────────────────────────────┼──────────────────────────────────────┘
                                    │
                                    │ Split Sub-Models
                                    ▼

╔══════════════════════════════════════════════════════════════════════════════╗
║              PHASE 5: LAYOUT CALCULATION (LLM-ENHANCED)                      ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │  GraphLayoutEngine → calculate_layout()                              │
    │                                                                      │
    │  Uses LLM-enriched data:                                            │
    │  • element_types (from LLM semantic mapping)                        │
    │  • Validated relationships (from LLM validation)                     │
    │  • Context-aware element grouping                                    │
    │                                                                      │
    │  Creates NetworkX graph with:                                       │
    │  • Nodes: Parts, Actors, Use Cases (typed by LLM)                   │
    │  • Edges: Connections (validated by LLM)                            │
    │                                                                      │
    │  Applies hierarchical layout:                                       │
    │  • Use cases: Center (functional nodes from LLM)                   │
    │  • Actors: Sides (ports from LLM context)                           │
    │  • Parts: Bottom (components from LLM)                               │
    └────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 │ Calculated Layout Positions
                                 ▼

╔══════════════════════════════════════════════════════════════════════════════╗
║              PHASE 6: VISUALIZATION GENERATION                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │  SlidesRenderer → render()                                          │
    │                                                                      │
    │  Uses LLM-enriched metadata:                                        │
    │  • element_types → Determines shape type (rectangle/circle/oval)    │
    │  • Validated connections → Draws correct arrows                      │
    │  • Context-aware positioning → Proper layout                        │
    │                                                                      │
    │  Draws elements:                                                     │
    │  • Parts → Rectangles (from LLM type mapping)                      │
    │  • Actors → Circles (from LLM type mapping)                        │
    │  • Use Cases → Ovals (from LLM type mapping)                       │
    │  • Connections → Arrows (from LLM-validated relationships)         │
    └────────────────────────────┬─────────────────────────────────────────┘
                                 │
                                 │ Final Visualization
                                 ▼
    ┌─────────────────────────────────────────────────────────────────────┐
    │  Google Slides Presentation                                          │
    │  OR                                                                  │
    │  HTML Visualization                                                  │
    └─────────────────────────────────────────────────────────────────────┘

```

## KEY LLM CAPABILITIES UTILIZED

### 1. **Semantic Understanding**
   - **What LLM does**: Understands SysML syntax beyond simple pattern matching
   - **Why it matters**: Handles complex nested structures, implicit relationships
   - **Example**: Recognizes that "Human" in a connection refers to a part, not just text

### 2. **Context Awareness**
   - **What LLM does**: Analyzes relationships between elements
   - **Why it matters**: Correctly maps actors to use cases, parts to parents
   - **Example**: Knows "DroneOperator" is an actor associated with "InspectAircraftAutomatically" use case

### 3. **Relationship Extraction**
   - **What LLM does**: Identifies all connections, even implicit ones
   - **Why it matters**: Captures complete system model
   - **Example**: Extracts "connect Human to DroneOperator" and understands it's a Part→Actor relationship

### 4. **Hierarchy Building**
   - **What LLM does**: Constructs parent-child relationships from nested structures
   - **Why it matters**: Maintains system organization
   - **Example**: Recognizes that nested "part" declarations belong to parent "part def"

### 5. **Documentation Extraction**
   - **What LLM does**: Extracts doc comments and descriptions
   - **Why it matters**: Preserves system documentation
   - **Example**: Captures "doc /* Human operator... */" comments

### 6. **Type Inference**
   - **What LLM does**: Determines element types (part, actor, use case)
   - **Why it matters**: Enables correct visualization (rectangles vs circles vs ovals)
   - **Example**: Identifies "DroneOperator" as actor (circle) vs "Human" as part (rectangle)

### 7. **Validation**
   - **What LLM does**: Validates extracted data structure
   - **Why it matters**: Ensures correctness before visualization
   - **Example**: Checks that all connections reference existing elements

### 8. **Error Recovery**
   - **What LLM does**: Handles malformed or incomplete SysML
   - **Why it matters**: Robust parsing even with syntax variations
   - **Example**: Infers missing relationships from context

## LLM PROCESSING FLOW SUMMARY

```
SysML Text
    ↓
[LLM Tokenization] → Understands SysML keywords
    ↓
[LLM Semantic Analysis] → Recognizes structures, relationships
    ↓
[LLM Context Building] → Maps elements to types, hierarchies
    ↓
[LLM Extraction] → Extracts structured JSON
    ↓
[LLM Validation] → Validates and enriches data
    ↓
[LLM Context Discovery] → Finds relationship contexts
    ↓
Structured, Validated, Enriched JSON
    ↓
Visualization Generation
```

## WHY LLM IS CRITICAL

1. **Beyond Regex**: LLM understands SysML semantics, not just patterns
2. **Context Understanding**: Knows how elements relate to each other
3. **Robustness**: Handles variations in SysML syntax
4. **Completeness**: Extracts implicit relationships
5. **Accuracy**: Validates and corrects extracted data
6. **Enrichment**: Adds semantic metadata for visualization

## LLM CONTRIBUTION AT EACH STAGE

| Stage | LLM Role | Impact |
|-------|----------|--------|
| **Parsing** | Extracts structured data from raw SysML | Converts unstructured text → structured JSON |
| **Enrichment** | Adds semantic metadata | Enables correct visualization types |
| **Validation** | Validates relationships | Ensures data correctness |
| **Context Discovery** | Finds element associations | Enables proper diagram layout |
| **Type Mapping** | Maps elements to visual types | Determines shapes (rect/circle/oval) |
| **Error Handling** | Recovers from parsing errors | Provides fallback strategies |

---

**The LLM is the BRAIN of the system - it provides the intelligence to understand, extract, validate, and enrich the SysML model before visualization.**

