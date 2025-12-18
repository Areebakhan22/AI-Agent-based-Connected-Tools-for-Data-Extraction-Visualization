"""
SysML Parser Module

This module extracts structured information from SysML v2 style text files.
It identifies 'part' definitions and 'connect' relationships.
"""

import re
from typing import Dict, List, Tuple


def parse_sysml_file(file_path: str) -> Dict:
    """
    Parse a SysML file and extract parts, hierarchy, and connections.
    
    Handles multiple formats:
    - part def 'Name' { ... } (with or without quotes)
    - part 'Name' (nested parts)
    - connect X to Y (may reference parts or actors)
    
    Args:
        file_path: Path to the SysML file
        
    Returns:
        Dictionary with 'parts', 'hierarchy', and 'connections' keys
        {
            'parts': [{'name': 'PartName', 'doc': 'description', 'parent': 'ParentName' or None}, ...],
            'hierarchy': {'ParentName': ['Child1', 'Child2', ...], ...},
            'connections': [{'from': 'SourcePart', 'to': 'TargetPart'}, ...]
        }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parts = []
    hierarchy = {}  # Maps parent name to list of child names
    part_to_parent = {}  # Maps child name to parent name
    
    # Extract top-level part definitions (part def)
    part_def_pattern = r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{"
    top_level_parts = []
    for match in re.finditer(part_def_pattern, content):
        part_name = match.group(1)
        top_level_parts.append(part_name)
        parts.append({
            'name': part_name,
            'doc': '',
            'parent': None,
            'is_top_level': True
        })
        hierarchy[part_name] = []
    
    # Extract nested parts and determine their parent
    # Find all part def blocks and their nested parts
    part_def_blocks = list(re.finditer(r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{", content))
    
    for i, parent_match in enumerate(part_def_blocks):
        parent_name = parent_match.group(1)
        start_pos = parent_match.end()
        
        # Find the end of this block (matching closing brace)
        if i < len(part_def_blocks) - 1:
            end_pos = part_def_blocks[i + 1].start()
        else:
            end_pos = len(content)
        
        block_content = content[start_pos:end_pos]
        
        # Find nested parts within this block
        nested_part_pattern = r"part\s+['\"]?(\w+)['\"]?\s*;"
        for nested_match in re.finditer(nested_part_pattern, block_content):
            child_name = nested_match.group(1)
            if child_name not in [p['name'] for p in parts]:
                parts.append({
                    'name': child_name,
                    'doc': '',
                    'parent': parent_name,
                    'is_top_level': False
                })
                if parent_name not in hierarchy:
                    hierarchy[parent_name] = []
                hierarchy[parent_name].append(child_name)
                part_to_parent[child_name] = parent_name
    
    # Extract doc comments for parts
    part_def_with_doc_pattern = r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{[^}]*doc\s+/\*\s*(.*?)\s*\*/\s*\}"
    for match in re.finditer(part_def_with_doc_pattern, content, re.DOTALL):
        part_name = match.group(1)
        part_doc = match.group(2).strip() if match.group(2) else ""
        # Update existing part with doc
        for part in parts:
            if part['name'] == part_name:
                part['doc'] = part_doc
                break
    
    # Extract all connections
    connect_pattern = r'connect\s+(\w+)\s+to\s+(\w+)\s*;?'
    connections = []
    for match in re.finditer(connect_pattern, content):
        from_part = match.group(1)
        to_part = match.group(2)
        connections.append({
            'from': from_part,
            'to': to_part
        })
    
    return {
        'parts': parts,
        'hierarchy': hierarchy,
        'connections': connections
    }


def validate_connections(parts: List[Dict], connections: List[Dict]) -> List[Dict]:
    """
    Validate that all connections reference existing parts or actors.
    For Milestone 1, we include all connections even if they reference actors,
    as actors may be visualized as well.
    
    Args:
        parts: List of part dictionaries
        connections: List of connection dictionaries
        
    Returns:
        List of valid connections (all connections are kept, even if they
        reference actors or other elements not in the parts list)
    """
    part_names = {part['name'] for part in parts}
    valid_connections = []
    
    for conn in connections:
        # Include all connections - they may reference parts or actors
        # For visualization purposes, we'll create shapes for both
        valid_connections.append(conn)
        
        # Optional: warn if connection references unknown elements
        if conn['from'] not in part_names:
            print(f"Note: Connection source '{conn['from']}' is not a defined part "
                  f"(may be an actor or other element). Will be visualized anyway.")
        if conn['to'] not in part_names:
            print(f"Note: Connection target '{conn['to']}' is not a defined part "
                  f"(may be an actor or other element). Will be visualized anyway.")
    
    return valid_connections

