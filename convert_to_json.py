#!/usr/bin/env python3
"""
Helper script to convert existing SysML parser output to JSON format
for use with visualize_sysml.py pipeline.

Usage:
    python convert_to_json.py OpsCon.sysml [--output output.json] [--model MODEL]
"""

import json
import sys
import argparse
from llm_parser import parse_sysml_file


def main():
    parser = argparse.ArgumentParser(
        description='Convert SysML file to JSON format for visualize_sysml.py'
    )
    parser.add_argument('sysml_file', help='Path to SysML file')
    parser.add_argument('--output', '-o', default=None,
                       help='Output JSON file path (default: <input>.json)')
    parser.add_argument('--model', default='llama3',
                       help='Ollama model name (default: llama3)')
    parser.add_argument('--no-llm', action='store_true',
                       help='Use regex parser instead of LLM')
    
    args = parser.parse_args()
    
    # Parse SysML file
    print(f"Parsing SysML file: {args.sysml_file}")
    data = parse_sysml_file(args.sysml_file, use_llm=not args.no_llm, model=args.model)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.sysml_file.replace('.sysml', '.json')
        if output_path == args.sysml_file:
            output_path = args.sysml_file + '.json'
    
    # Write JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ JSON saved to: {output_path}")
    print(f"\nYou can now use this JSON with visualize_sysml.py:")
    print(f"  python visualize_sysml.py {output_path}")


if __name__ == "__main__":
    main()



