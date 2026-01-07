#!/usr/bin/env python3
"""
Extract comments from SysML file and add them to metadata JSON.
This script extracts doc comments from SysML files and adds them to the relationship_images_metadata.json
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

def extract_sysml_comments(sysml_file_path: str) -> List[Dict]:
    """
    Extract comments from SysML file preserving raw format.
    Returns a list of comment dictionaries with raw comment text as-is.
    """
    with open(sysml_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    comments = []
    
    # Extract doc comments from objective blocks - preserve raw format
    # Pattern: objective 'Name' { doc /* ... */ }
    objective_pattern = r"objective\s+['\"]?(\w+)['\"]?\s*\{[^}]*doc\s+(/\*.*?\*/)"
    for match in re.finditer(objective_pattern, content, re.DOTALL):
        obj_name = match.group(1)
        raw_comment = match.group(2).strip()  # Preserve /* ... */ format
        
        comments.append({
            'title': f"Objective: {obj_name}",
            'raw_comment': raw_comment,
            'content': raw_comment
        })
    
    # Extract doc comments from use cases - preserve raw format
    use_case_pattern = r"use\s+case\s+['\"]?(\w+)['\"]?\s*\{[^}]*doc\s+(/\*.*?\*/)"
    for match in re.finditer(use_case_pattern, content, re.DOTALL):
        uc_name = match.group(1)
        raw_comment = match.group(2).strip()  # Preserve /* ... */ format
        
        comments.append({
            'title': f"Use Case: {uc_name}",
            'raw_comment': raw_comment,
            'content': raw_comment
        })
    
    # Extract doc comments from part definitions - preserve raw format
    part_doc_pattern = r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{[^}]*doc\s+(/\*.*?\*/)"
    for match in re.finditer(part_doc_pattern, content, re.DOTALL):
        part_name = match.group(1)
        raw_comment = match.group(2).strip()  # Preserve /* ... */ format
        
        comments.append({
            'title': f"Part: {part_name}",
            'raw_comment': raw_comment,
            'content': raw_comment
        })
    
    # Extract top-level file comments (at the beginning of file, before any action/part/etc)
    # Pattern: /* ... */ at the start of file
    top_level_comment_pattern = r"^/\*.*?\*/"
    top_match = re.search(top_level_comment_pattern, content, re.DOTALL | re.MULTILINE)
    if top_match:
        raw_comment = top_match.group(0).strip()
        # Check if this comment is not already captured
        if not any(c.get('raw_comment') == raw_comment for c in comments):
            comments.insert(0, {  # Insert at beginning
                'title': 'System Overview',
                'raw_comment': raw_comment,
                'content': raw_comment
            })
    
    # If no structured comments found, try to extract any doc blocks - preserve raw format
    if not comments:
        doc_pattern = r"doc\s+(/\*.*?\*/)"
        for match in re.finditer(doc_pattern, content, re.DOTALL):
            raw_comment = match.group(1).strip()  # Preserve /* ... */ format
            
            if raw_comment:
                comments.append({
                    'title': 'System Documentation',
                    'raw_comment': raw_comment,
                    'content': raw_comment
                })
    
    return comments

def update_metadata_with_comments(metadata_path: str, comments: List[Dict]):
    """Update metadata JSON file with extracted comments."""
    if Path(metadata_path).exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'relationships': []}
    
    data['sysml_comments'] = comments
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Updated {metadata_path} with {len(comments)} comment(s)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_sysml_comments.py <sysml_file> [metadata_json]")
        print("Example: python extract_sysml_comments.py OpsCon.sysml frontend/public/relationship_images_metadata.json")
        sys.exit(1)
    
    sysml_file = sys.argv[1]
    metadata_file = sys.argv[2] if len(sys.argv) > 2 else 'frontend/public/relationship_images_metadata.json'
    
    if not Path(sysml_file).exists():
        print(f"Error: SysML file not found: {sysml_file}")
        sys.exit(1)
    
    print(f"Extracting comments from {sysml_file}...")
    comments = extract_sysml_comments(sysml_file)
    
    if comments:
        print(f"Found {len(comments)} comment(s):")
        for comment in comments:
            print(f"  - {comment['title']}")
        update_metadata_with_comments(metadata_file, comments)
    else:
        print("No comments found in SysML file")
        # Still update metadata with empty comments array
        update_metadata_with_comments(metadata_file, [])

if __name__ == "__main__":
    main()

