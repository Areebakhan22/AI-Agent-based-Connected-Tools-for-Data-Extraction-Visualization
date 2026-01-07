#!/usr/bin/env python3
"""
Complete Pipeline: SysML → LLM → JSON → Gemini Images → React Frontend

This script runs the complete workflow:
1. Parse SysML file with LLM to create JSON
2. Convert JSON to relationship format
3. Generate images with Gemini for each relationship
4. Copy files to React frontend
5. Start React dev server
"""

import sys
import json
import os
import subprocess
import shutil
from pathlib import Path
from llm_parser import parse_sysml_file
from gemini_image_generator import GeminiImageGenerator


def convert_to_relationship_json(llm_json: dict, sysml_file: str) -> dict:
    """
    Convert LLM parser output to the format needed for gemini_image_generator.
    Creates a format similar to complete_slide.json with elements and connections_summary.
    """
    # Extract parts, actors, use cases from LLM output
    parts = llm_json.get('parts', [])
    actors = llm_json.get('actors', [])
    use_cases = llm_json.get('use_cases', [])
    connections = llm_json.get('connections', [])
    
    # Build elements list
    elements = []
    element_map = {}
    
    # Add system container (use first top-level part or filename)
    system_name = None
    for part in parts:
        if part.get('is_top_level', False):
            system_name = part.get('name', Path(sysml_file).stem)
            break
    if not system_name:
        system_name = Path(sysml_file).stem.replace('_', ' ')
    
    elements.append({
        "element_id": "sys_container",
        "shape_id": "sys_container",
        "shape_type": "RECTANGLE",
        "text_content": system_name,
        "has_text_changes": False,
        "element_type": "SYSTEM"
    })
    
    # Process parts (exclude top-level system)
    for part in parts:
        part_name = part.get('name', '')
        if part.get('is_top_level', False):
            continue  # Skip top-level system container
        shape_id = f"comp_{part_name}"
        elements.append({
            "element_id": part_name,
            "shape_id": shape_id,
            "shape_type": "RECTANGLE",
            "text_content": part_name,
            "has_text_changes": False,
            "element_type": "PART"
        })
        element_map[part_name] = {'type': 'PART', 'shape_id': shape_id}
    
    # Process actors (if provided in JSON)
    for actor in actors:
        actor_name = actor.get('name', '')
        if actor_name:
            shape_id = f"actor_{actor_name}"
            elements.append({
                "element_id": actor_name,
                "shape_id": shape_id,
                "shape_type": "CIRCLE",
                "text_content": actor_name,
                "has_text_changes": False,
                "element_type": "ACTOR"
            })
            element_map[actor_name] = {'type': 'ACTOR', 'shape_id': shape_id}
    
    # Process use cases (if provided in JSON)
    for use_case in use_cases:
        uc_name = use_case.get('name', '')
        if uc_name:
            shape_id = f"uc_{uc_name}"
            elements.append({
                "element_id": uc_name,
                "shape_id": shape_id,
                "shape_type": "ELLIPSE",
                "text_content": uc_name,
                "has_text_changes": False,
                "element_type": "USE_CASE"
            })
            element_map[uc_name] = {'type': 'USE_CASE', 'shape_id': shape_id}
    
    # If actors/use_cases not in JSON, try to infer from connections
    part_names = {p.get('name') for p in parts if not p.get('is_top_level', False)}
    actors_seen = {a.get('name') for a in actors}
    use_cases_seen = {uc.get('name') for uc in use_cases}
    
    for conn in connections:
        from_elem = conn.get('from', '')
        to_elem = conn.get('to', '')
        
        # Try to identify actors (often end with Actor or are external)
        if to_elem not in part_names and to_elem not in actors_seen and to_elem not in use_cases_seen:
            if 'Actor' in to_elem or to_elem.endswith('Actor') or to_elem.endswith('Environment'):
                actors_seen.add(to_elem)
                shape_id = f"actor_{to_elem}"
                elements.append({
                    "element_id": to_elem,
                    "shape_id": shape_id,
                    "shape_type": "CIRCLE",
                    "text_content": to_elem,
                    "has_text_changes": False,
                    "element_type": "ACTOR"
                })
                element_map[to_elem] = {'type': 'ACTOR', 'shape_id': shape_id}
        
        # Identify use cases
        if 'UseCase' in to_elem or 'Use' in to_elem or 'use case' in to_elem.lower() or to_elem not in part_names:
            if to_elem not in use_cases_seen and to_elem not in actors_seen:
                # Check if it looks like a use case (action verbs, etc.)
                action_verbs = ['Inspect', 'Operate', 'Monitor', 'Control', 'Manage', 'Process']
                if any(verb in to_elem for verb in action_verbs) or 'Automatically' in to_elem:
                    use_cases_seen.add(to_elem)
                    shape_id = f"uc_{to_elem}"
                    elements.append({
                        "element_id": to_elem,
                        "shape_id": shape_id,
                        "shape_type": "ELLIPSE",
                        "text_content": to_elem,
                        "has_text_changes": False,
                        "element_type": "USE_CASE"
                    })
                    element_map[to_elem] = {'type': 'USE_CASE', 'shape_id': shape_id}
    
    # Add connection elements
    connection_elements = []
    connections_summary = {
        "part_to_actor": [],
        "part_to_part": [],
        "part_to_subject": [],
        "actor_to_use_case": [],
        "subject_to_use_case": []
    }
    
    for conn in connections:
        from_elem = conn.get('from', '')
        to_elem = conn.get('to', '')
        from_type = element_map.get(from_elem, {}).get('type', 'PART')
        to_type = element_map.get(to_elem, {}).get('type', 'PART')  # Default to PART instead of ACTOR
        
        # Categorize connection
        if from_type == 'PART' and to_type == 'ACTOR':
            connections_summary["part_to_actor"].append(f"{from_elem} → {to_elem}")
        elif from_type == 'PART' and to_type == 'PART':
            connections_summary["part_to_part"].append(f"{from_elem} → {to_elem}")
        elif from_type == 'ACTOR' and to_type == 'USE_CASE':
            connections_summary["actor_to_use_case"].append(f"{from_elem} → {to_elem}")
        elif from_type == 'PART' and to_type == 'SUBJECT':
            connections_summary["part_to_subject"].append(f"{from_elem} → {to_elem}")
        elif from_type == 'SUBJECT' and to_type == 'USE_CASE':
            connections_summary["subject_to_use_case"].append(f"{from_elem} → {to_elem}")
        
        # Add connection line element
        conn_shape_id = f"conn_{from_elem}_{to_elem}"
        connection_elements.append({
            "element_id": conn_shape_id,
            "shape_id": conn_shape_id,
            "shape_type": "LINE",
            "text_content": "",
            "has_text_changes": False,
            "from": element_map.get(from_elem, {}).get('shape_id', from_elem),
            "to": element_map.get(to_elem, {}).get('shape_id', to_elem),
            "connection_type": "ASSOCIATION"
        })
    
    elements.extend(connection_elements)
    
    # Build final JSON structure
    result = {
        "slide_index": 0,
        "slide_id": f"complete_approach_1",
        "slide_title": f"Complete {system_name} Diagram",
        "elements": elements,
        "shape_legend": {
            "SYSTEM": "RECTANGLE - Large container box",
            "PART": "RECTANGLE - System components",
            "ACTOR": "CIRCLE - External actors",
            "USE_CASE": "ELLIPSE - Use case functionality",
            "SUBJECT": "ROUND_RECTANGLE - Subject of interest"
        },
        "connections_summary": connections_summary
    }
    
    return result


def run_pipeline(sysml_file: str, model: str = "llama3", use_llm: bool = True, start_frontend: bool = True):
    """
    Run the complete pipeline.
    
    Args:
        sysml_file: Path to SysML file
        model: Ollama model name
        use_llm: Whether to use LLM parsing
        start_frontend: Whether to start React dev server
    """
    print("=" * 70)
    print("🚀 Complete Pipeline: SysML → LLM → JSON → Gemini Images → React")
    print("=" * 70)
    print()
    print("📋 Pipeline Flow:")
    print("   1. Read SysML file (OpsCon.sysml)")
    print("   2. Parse with LLM → Create/REWRITE JSON file")
    print("   3. Extract comments from SysML file")
    print("   4. Generate individual relationship images")
    print("   5. Generate complete diagram image")
    print("   6. Copy all files to frontend")
    print("   7. Start React frontend (if enabled)")
    print()
    
    # Step 1: Parse SysML with LLM
    print("[1/6] Parsing SysML file with LLM...")
    print(f"     File: {sysml_file}")
    print(f"     Model: {model}")
    print(f"     Use LLM: {use_llm}")
    print()
    
    try:
        llm_data = parse_sysml_file(sysml_file, use_llm=use_llm, model=model)
        print("✓ SysML parsed successfully")
        print(f"  Parts: {len(llm_data.get('parts', []))}")
        print(f"  Connections: {len(llm_data.get('connections', []))}")
        print()
    except Exception as e:
        print(f"❌ Error parsing SysML: {e}")
        return 1
    
    # Step 2: Convert to relationship JSON format and REWRITE JSON file
    print("[2/6] Converting to relationship JSON format...")
    print("     📝 Rewriting JSON file with updated SysML data...")
    try:
        relationship_json = convert_to_relationship_json(llm_data, sysml_file)
        json_output = "pipeline_output.json"
        
        # Always rewrite the JSON file (overwrite if exists)
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(relationship_json, f, indent=2)
        
        print(f"✓ JSON file REWRITTEN: {json_output}")
        print(f"  📊 Elements: {len(relationship_json.get('elements', []))}")
        print(f"  🔗 Connections: {len(relationship_json.get('connections_summary', {}).get('part_to_actor', [])) + len(relationship_json.get('connections_summary', {}).get('actor_to_use_case', []))}")
        print(f"  📄 File location: {os.path.abspath(json_output)}")
        print()
    except Exception as e:
        print(f"❌ Error converting JSON: {e}")
        return 1
    
    # Step 3: Extract comments from SysML file
    print("[3/6] Extracting comments from SysML file...")
    sysml_comments = []
    try:
        from extract_sysml_comments import extract_sysml_comments
        sysml_comments = extract_sysml_comments(sysml_file)
        print(f"✓ Extracted {len(sysml_comments)} comment(s) from SysML file")
        print()
    except Exception as e:
        print(f"⚠️  Warning: Could not extract comments: {e}")
        print("   Continuing without comments...")
        print()
    
    # Step 4: Generate images with Gemini (individual relationships + complete diagram)
    print("[4/6] Generating images with Gemini API...")
    print("     🎨 Creating images based on updated JSON...")
    try:
        generator = GeminiImageGenerator()
        # Pass the original SysML file path so complete diagram can use it
        generator.original_sysml_file = sysml_file
        relationships = generator.generate_all_images(json_output)
        generator.save_metadata(relationships, 'relationship_images_metadata.json', sysml_comments=sysml_comments)
        
        # Count generated images
        generated_images = [r for r in relationships if r.get('image_path')]
        individual_count = len(generated_images)
        
        # Check for complete diagram
        complete_diagram_path = generator.output_dir / "complete_sysml_diagram_gemini.png"
        has_complete = complete_diagram_path.exists()
        
        print(f"✓ Image generation complete!")
        print(f"  📸 Individual relationship images: {individual_count}")
        if has_complete:
            print(f"  🎯 Complete diagram: {complete_diagram_path.name}")
        print(f"  📁 Output directory: {generator.output_dir}")
        print()
        
        # List all created image files
        if generated_images:
            print("  📋 Created individual relationship images:")
            for rel in generated_images:
                img_name = os.path.basename(rel.get('image_path', ''))
                print(f"     • {img_name}")
        if has_complete:
            print(f"  📋 Complete diagram:")
            print(f"     • {complete_diagram_path.name}")
        print()
    except Exception as e:
        print(f"❌ Error generating images: {e}")
        print("   Continuing anyway...")
        print()
    
    # Step 5: Copy files to React frontend
    print("[5/6] Copying files to React frontend...")
    print("     📦 Copying JSON, metadata, and images to frontend...")
    try:
        frontend_public = Path("frontend/public")
        frontend_public.mkdir(parents=True, exist_ok=True)
        (frontend_public / "generated_images").mkdir(exist_ok=True)
        
        files_copied = []
        
        # Copy JSON file (for reference)
        if os.path.exists(json_output):
            shutil.copy(json_output, frontend_public / json_output)
            files_copied.append(f"  ✓ {json_output} → frontend/public/")
        
        # Copy metadata
        if os.path.exists("relationship_images_metadata.json"):
            shutil.copy("relationship_images_metadata.json", frontend_public / "relationship_images_metadata.json")
            files_copied.append("  ✓ relationship_images_metadata.json → frontend/public/")
        
        # Copy images (including complete diagram)
        if os.path.exists("generated_images"):
            image_count = 0
            for img_file in Path("generated_images").glob("*.png"):
                shutil.copy(img_file, frontend_public / "generated_images" / img_file.name)
                image_count += 1
                if img_file.name == "complete_sysml_diagram_gemini.png":
                    files_copied.append(f"  ✓ {img_file.name} (complete diagram) → frontend/public/generated_images/")
            
            if image_count > 0:
                files_copied.append(f"  ✓ {image_count} total images → frontend/public/generated_images/")
        
        print("✓ Files copied to frontend/public")
        for msg in files_copied:
            print(msg)
        print()
    except Exception as e:
        print(f"⚠️  Warning: Error copying files: {e}")
        print()
    
    # Step 6: Start React frontend
    if start_frontend:
        print("[6/6] Starting React frontend...")
        print("     Opening http://localhost:3000")
        print()
        print("=" * 70)
        print("✅ Pipeline complete! React app is starting...")
        print("=" * 70)
        print()
        print("Press Ctrl+C to stop the server")
        print()
        
        try:
            # Change to frontend directory and start dev server
            frontend_dir = Path("frontend")
            if not (frontend_dir / "node_modules").exists():
                print("Installing npm dependencies first...")
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            
            subprocess.run(["npm", "run", "dev"], cwd=frontend_dir)
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
        except Exception as e:
            print(f"❌ Error starting React server: {e}")
            print("\nYou can start it manually:")
            print("  cd frontend")
            print("  npm install  # if needed")
            print("  npm run dev")
            return 1
    else:
        print("[5/5] Skipping React frontend (use --start-frontend to enable)")
        print()
        print("=" * 70)
        print("✅ Pipeline complete!")
        print("=" * 70)
        print()
        print("To start the React app manually:")
        print("  cd frontend")
        print("  npm run dev")
    
    return 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete pipeline: SysML → LLM → JSON → Gemini Images → React'
    )
    parser.add_argument('sysml_file', help='Path to SysML file (e.g., OpsCon.sysml)')
    parser.add_argument('--model', default='llama3', help='Ollama model name (default: llama3)')
    parser.add_argument('--no-llm', action='store_true', help='Use regex parser instead of LLM')
    parser.add_argument('--no-frontend', action='store_true', help='Skip starting React frontend')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.sysml_file):
        print(f"❌ Error: File not found: {args.sysml_file}")
        return 1
    
    return run_pipeline(
        args.sysml_file,
        model=args.model,
        use_llm=not args.no_llm,
        start_frontend=not args.no_frontend
    )


if __name__ == '__main__':
    sys.exit(main())

