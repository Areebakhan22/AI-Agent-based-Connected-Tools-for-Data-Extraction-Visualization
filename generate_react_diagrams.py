#!/usr/bin/env python3
"""
Generate React + D3.js Diagrams from SysML JSON

This script integrates with the existing LLM pipeline (visualize_sysml.py)
and generates React-compatible JSON output without modifying the pipeline.
"""

import json
import sys
import argparse
from pathlib import Path
from visualize_sysml import (
    SemanticModelProcessor,
    RelationshipSplitter,
    GraphLayoutEngine
)
from react_renderer import ReactRenderer


def main():
    parser = argparse.ArgumentParser(
        description='Generate React + D3.js diagrams from SysML JSON'
    )
    parser.add_argument('input_json', help='Path to SysML JSON file (e.g., OpsCon.json)')
    parser.add_argument('--model', default='llama3', help='Ollama model name (default: llama3)')
    parser.add_argument('--output', default='react_diagrams.json', 
                       help='Output filename (default: react_diagrams.json)')
    parser.add_argument('--no-llm', action='store_true', 
                       help='Skip LLM processing (use default mappings)')
    
    args = parser.parse_args()
    
    # Load input JSON
    input_path = Path(args.input_json)
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)
    
    with open(input_path, 'r') as f:
        json_data = json.load(f)
    
    print(f"✓ Loaded JSON from: {input_path}")
    print(f"  Parts: {len(json_data.get('parts', []))}")
    print(f"  Actors: {len(json_data.get('actors', []))}")
    print(f"  Use Cases: {len(json_data.get('use_cases', []))}")
    print(f"  Connections: {len(json_data.get('connections', []))}")
    
    # Step 1: Semantic processing (existing LLM pipeline)
    print("\n[Step 1] Processing with LLM...")
    if args.no_llm:
        print("⚠️  Skipping LLM processing (using default mappings)")
        # Use default mapping without LLM
        enriched_model = json_data.copy()
        enriched_model['element_types'] = {}
        enriched_model['system_boundary'] = 'System'
    else:
        processor = SemanticModelProcessor(model=args.model)
        enriched_model = processor.understand_model(json_data)
    print("✓ Semantic processing complete")
    
    # Step 2: Split by relationships (existing pipeline)
    print("\n[Step 2] Splitting by relationships...")
    splitter = RelationshipSplitter()
    sub_models = splitter.split_by_relationships(enriched_model)
    print(f"✓ Created {len(sub_models)} sub-models")
    
    # Step 3: Calculate layouts (existing pipeline)
    print("\n[Step 3] Calculating layouts...")
    layout_engine = GraphLayoutEngine()
    for sub_model in sub_models:
        layout = layout_engine.calculate_layout(sub_model)
        sub_model['layout'] = layout
    print("✓ Layout calculation complete")
    
    # Step 4: Render for React (NEW)
    print("\n[Step 4] Rendering for React + D3.js...")
    react_renderer = ReactRenderer()
    system_name = enriched_model.get('system_boundary', 'SysML System')
    react_data = react_renderer.render(sub_models, system_name)
    
    # Save output
    output_path = react_renderer.save(react_data, args.output)
    print(f"✓ React diagram data saved to: {output_path}")
    
    print(f"\n✓ Success! Generated {len(react_data['diagrams'])} diagrams")
    print(f"  - Full diagram: 1")
    print(f"  - Individual relationships: {len(react_data['diagrams']) - 1}")
    print(f"\nNext steps:")
    print(f"  1. Start backend server: python backend/api_server.py")
    print(f"  2. Start frontend: cd frontend && npm install && npm run dev")
    print(f"  3. Open browser: http://localhost:3000")


if __name__ == '__main__':
    main()

