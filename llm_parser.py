"""
LLM-based SysML Parser Module

This module uses LLM (Ollama) to extract structured information from SysML files.
It replaces regex-based parsing with semantic understanding.
"""

from typing import Dict, List
from llm_service import LLMService


def parse_sysml_file(file_path: str, use_llm: bool = True, model: str = "llama3") -> Dict:
    """
    Parse a SysML file using LLM for semantic extraction.
    
    Args:
        file_path: Path to the SysML file
        use_llm: Whether to use LLM (True) or fallback to regex (False)
        model: Ollama model name (default: "llama3")
        
    Returns:
        Dictionary with 'parts', 'hierarchy', and 'connections' keys
        {
            'parts': [{'name': 'PartName', 'doc': 'description', 'parent': 'ParentName' or None, 'is_top_level': True/False}, ...],
            'hierarchy': {'ParentName': ['Child1', 'Child2', ...], ...},
            'connections': [{'from': 'SourcePart', 'to': 'TargetPart'}, ...]
        }
    """
    # Read SysML file
    with open(file_path, 'r', encoding='utf-8') as f:
        sysml_content = f.read()
    
    if use_llm:
        # Use LLM for semantic extraction
        try:
            llm_service = LLMService(model=model)
            data = llm_service.extract_sysml(sysml_content)
            return data
        except Exception as e:
            print(f"⚠️  LLM parsing failed: {e}")
            print("   Falling back to regex-based parser...")
            # Fallback to regex parser
            return _fallback_regex_parse(sysml_content)
    else:
        # Use regex parser directly
        return _fallback_regex_parse(sysml_content)


def _fallback_regex_parse(sysml_content: str) -> Dict:
    """
    Fallback regex-based parser (original implementation).
    Used when LLM is unavailable or fails.
    """
    import re
    
    parts = []
    hierarchy = {}
    
    # Extract top-level part definitions (part def)
    part_def_pattern = r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{"
    top_level_parts = []
    for match in re.finditer(part_def_pattern, sysml_content):
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
    part_def_blocks = list(re.finditer(r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{", sysml_content))
    
    for i, parent_match in enumerate(part_def_blocks):
        parent_name = parent_match.group(1)
        start_pos = parent_match.end()
        
        if i < len(part_def_blocks) - 1:
            end_pos = part_def_blocks[i + 1].start()
        else:
            end_pos = len(sysml_content)
        
        block_content = sysml_content[start_pos:end_pos]
        
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
    
    # Extract doc comments for parts
    part_def_with_doc_pattern = r"part\s+def\s+['\"]?(\w+)['\"]?\s*\{[^}]*doc\s+/\*\s*(.*?)\s*\*/\s*\}"
    for match in re.finditer(part_def_with_doc_pattern, sysml_content, re.DOTALL):
        part_name = match.group(1)
        part_doc = match.group(2).strip() if match.group(2) else ""
        for part in parts:
            if part['name'] == part_name:
                part['doc'] = part_doc
                break
    
    # Extract all connections
    connect_pattern = r'connect\s+(\w+)\s+to\s+(\w+)\s*;?'
    connections = []
    for match in re.finditer(connect_pattern, sysml_content):
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
        valid_connections.append(conn)
        
        # Optional: warn if connection references unknown elements
        if conn['from'] not in part_names:
            print(f"Note: Connection source '{conn['from']}' is not a defined part "
                  f"(may be an actor or other element). Will be visualized anyway.")
        if conn['to'] not in part_names:
            print(f"Note: Connection target '{conn['to']}' is not a defined part "
                  f"(may be an actor or other element). Will be visualized anyway.")
    
    return valid_connections

