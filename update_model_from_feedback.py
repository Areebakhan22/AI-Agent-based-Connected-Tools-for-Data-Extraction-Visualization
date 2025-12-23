#!/usr/bin/env python3
"""
Update JSON Model from Feedback

This script processes feedback from Google Slides and updates the original JSON model.
"""

import json
import sys
import argparse
from typing import Dict, List


def load_json(file_path: str) -> Dict:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict, file_path: str):
    """Save JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def update_model_from_feedback(model: Dict, feedback: Dict) -> Dict:
    """
    Update model based on feedback from Google Slides.
    
    Args:
        model: Original JSON model
        feedback: Feedback dictionary from feedback_service.py
        
    Returns:
        Updated model dictionary
    """
    updated_model = json.loads(json.dumps(model))  # Deep copy
    changes_made = []
    
    # Process each slide
    for slide in feedback.get('slides', []):
        for element in slide.get('elements', []):
            if element.get('has_text_changes', False):
                element_id = element.get('element_id')
                new_text = element.get('text_content', '').strip()
                
                if not element_id or not new_text:
                    continue
                
                # Skip if unchanged
                if element_id == new_text:
                    continue
                
                # Update parts
                for part in updated_model.get('parts', []):
                    if part.get('name') == element_id:
                        old_name = part['name']
                        part['name'] = new_text
                        changes_made.append(f"Part: '{old_name}' → '{new_text}'")
                        
                        # Update hierarchy if this part is a parent
                        if old_name in updated_model.get('hierarchy', {}):
                            updated_model['hierarchy'][new_text] = updated_model['hierarchy'].pop(old_name)
                        
                        # Update parent references
                        for p in updated_model.get('parts', []):
                            if p.get('parent') == old_name:
                                p['parent'] = new_text
                
                # Update actors
                for actor in updated_model.get('actors', []):
                    if actor.get('name') == element_id:
                        old_name = actor['name']
                        actor['name'] = new_text
                        changes_made.append(f"Actor: '{old_name}' → '{new_text}'")
                
                # Update use cases
                for uc in updated_model.get('use_cases', []):
                    if uc.get('name') == element_id:
                        old_name = uc['name']
                        uc['name'] = new_text
                        changes_made.append(f"Use Case: '{old_name}' → '{new_text}'")
                
                # Update connections
                for conn in updated_model.get('connections', []):
                    if conn.get('from') == element_id:
                        conn['from'] = new_text
                        changes_made.append(f"Connection source: '{element_id}' → '{new_text}'")
                    if conn.get('to') == element_id:
                        conn['to'] = new_text
                        changes_made.append(f"Connection target: '{element_id}' → '{new_text}'")
    
    return updated_model, changes_made


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Update JSON model from Google Slides feedback'
    )
    parser.add_argument('model_file', help='Original JSON model file (e.g., OpsCon.json)')
    parser.add_argument('feedback_file', help='Feedback JSON file (e.g., feedback.json)')
    parser.add_argument('--output', '-o', default=None,
                       help='Output file (default: <model_file>_updated.json)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show changes without saving')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Update JSON Model from Feedback")
    print("=" * 60)
    
    # Load files
    print(f"\n[1/3] Loading model: {args.model_file}")
    try:
        model = load_json(args.model_file)
        print(f"✓ Loaded model with {len(model.get('parts', []))} parts, "
              f"{len(model.get('connections', []))} connections")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        sys.exit(1)
    
    print(f"\n[2/3] Loading feedback: {args.feedback_file}")
    try:
        feedback = load_json(args.feedback_file)
        num_slides = len(feedback.get('slides', []))
        print(f"✓ Loaded feedback from {num_slides} slide(s)")
    except Exception as e:
        print(f"✗ Error loading feedback: {e}")
        sys.exit(1)
    
    # Process feedback
    print(f"\n[3/3] Processing feedback...")
    updated_model, changes = update_model_from_feedback(model, feedback)
    
    if not changes:
        print("ℹ️  No changes detected in feedback")
        return
    
    print(f"✓ Found {len(changes)} change(s):")
    for change in changes:
        print(f"  - {change}")
    
    # Save or dry-run
    if args.dry_run:
        print("\n[DRY RUN] Changes would be saved to:", args.output or f"{args.model_file}_updated.json")
    else:
        output_file = args.output or args.model_file.replace('.json', '_updated.json')
        save_json(updated_model, output_file)
        print(f"\n✓ Updated model saved to: {output_file}")
        print(f"\nNext step: Regenerate slides with updated model:")
        print(f"  ./venv/bin/python3 visualize_sysml.py {output_file} --title 'Updated Model'")


if __name__ == "__main__":
    main()



