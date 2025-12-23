#!/usr/bin/env python3
"""
Main Script for SysML to Slides Converter

This script orchestrates the workflow:
1. Parse SysML file (using LLM for semantic understanding)
2. Extract parts and connections
3. Generate Google Slides or PowerPoint visualization

Usage:
    python main.py OpsCon.sysml [--no-llm] [--model MODEL_NAME] [--format FORMAT]
    
Options:
    --no-llm    Use regex parser instead of LLM (fallback)
    --model     Specify Ollama model name (default: llama3)
    --format    Output format: 'google' (default) or 'pptx' (PowerPoint)
"""

import sys
import json
import argparse
from llm_parser import parse_sysml_file, validate_connections
from slides_generator import generate_slides
from pptx_generator import generate_pptx


def main():
    """
    Main entry point for the SysML to Slides converter.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Convert SysML files to Google Slides or PowerPoint using LLM-based parsing'
    )
    parser.add_argument('sysml_file', help='Path to SysML file')
    parser.add_argument('--no-llm', action='store_true', 
                       help='Use regex parser instead of LLM (fallback mode)')
    parser.add_argument('--model', default='llama3',
                       help='Ollama model name (default: llama3)')
    parser.add_argument('--format', choices=['google', 'pptx'], default='google',
                       help='Output format: google (Google Slides) or pptx (PowerPoint)')
    parser.add_argument('--google-slides-url', type=str, default=None,
                       help='Google Slides URL to update existing presentation (e.g., https://docs.google.com/presentation/d/ID/edit)')
    
    args = parser.parse_args()
    sysml_file = args.sysml_file
    use_llm = not args.no_llm
    model = args.model
    output_format = args.format
    
    # Step 1: Parse the SysML file
    print(f"Reading SysML file: {sysml_file}")
    if use_llm:
        print(f"Using LLM-based parsing (model: {model})")
    else:
        print("Using regex-based parsing (fallback mode)")
    
    try:
        data = parse_sysml_file(sysml_file, use_llm=use_llm, model=model)
    except FileNotFoundError:
        print(f"Error: File '{sysml_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing SysML file: {e}")
        sys.exit(1)
    
    # Display extracted data
    print(f"\nExtracted {len(data['parts'])} parts:")
    for part in data['parts']:
        print(f"  - {part['name']}: {part['doc']}")
    
    print(f"\nExtracted {len(data['connections'])} connections:")
    for conn in data['connections']:
        print(f"  - {conn['from']} -> {conn['to']}")
    
    # Step 2: Validate connections
    print("\nValidating connections...")
    data['connections'] = validate_connections(data['parts'], data['connections'])
    
    if len(data['connections']) == 0:
        print("Warning: No valid connections found. Only parts will be visualized.")
    
    # Step 3: Convert to JSON format (for debugging/inspection)
    json_output = json.dumps(data, indent=2)
    print("\nStructured data (JSON format):")
    print(json_output)
    
    # Step 4: Generate presentation
    if output_format == 'pptx':
        print("\nGenerating PowerPoint presentation...")
        try:
            output_path = generate_pptx(data, title=f"SysML: {sysml_file}")
            print(f"\n✓ Success! PowerPoint presentation created.")
            print(f"  File: {output_path}")
        except Exception as e:
            print(f"\n✗ Error generating PowerPoint: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:  # Google Slides
        print("\nGenerating Google Slides visualization...")
        try:
            # Extract presentation ID from URL if provided
            existing_presentation_id = None
            if args.google_slides_url:
                # Extract ID from URL pattern: /d/PRESENTATION_ID/
                if '/d/' in args.google_slides_url:
                    parts = args.google_slides_url.split('/d/')
                    if len(parts) > 1:
                        existing_presentation_id = parts[1].split('/')[0].split('?')[0].split('#')[0].strip()
                        print(f"Updating existing presentation: {existing_presentation_id}")
                elif '/' not in args.google_slides_url:
                    # Direct ID provided
                    existing_presentation_id = args.google_slides_url
                    print(f"Updating existing presentation: {existing_presentation_id}")
            
            if existing_presentation_id:
                presentation_id, url = generate_slides(
                    data, 
                    f"SysML: {sysml_file}",
                    presentation_id=existing_presentation_id
                )
                print(f"\n✓ Success! Presentation updated.")
                print(f"  Presentation ID: {presentation_id}")
                print(f"  View at: {url}")
            else:
                presentation_id, url = generate_slides(data, f"SysML: {sysml_file}")
                print(f"\n✓ Success! Presentation created.")
                print(f"  Presentation ID: {presentation_id}")
                print(f"  View at: {url}")
        except FileNotFoundError as e:
            print(f"\n✗ Error: {e}")
            print("\nTo use Google Slides API, you need to:")
            print("1. Create a project in Google Cloud Console")
            print("2. Enable Google Slides API")
            print("3. Create OAuth 2.0 credentials (Desktop app)")
            print("4. Download and save as 'credentials.json' in this directory")
            print("\nAlternatively, use --format pptx for PowerPoint output (no setup required)")
            sys.exit(1)
        except Exception as e:
            print(f"\n✗ Error generating slides: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

