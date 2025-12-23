#!/usr/bin/env python3
"""
React + D3.js Renderer for SysML Diagrams

This renderer generates JSON output compatible with the React frontend,
while preserving the existing LLM pipeline workflow.
"""

import json
import os
from typing import Dict, List
from pathlib import Path


class ReactRenderer:
    """
    Renders SysML diagrams as JSON for React + D3.js frontend.
    Works alongside existing SlidesRenderer without modifying the LLM pipeline.
    """
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent
        self.output_dir.mkdir(exist_ok=True)
    
    def render(self, sub_models: List[Dict], system_name: str = "SysML System") -> Dict:
        """
        Convert sub_models from visualize_sysml.py to React-friendly JSON format.
        
        Args:
            sub_models: List of sub-models from RelationshipSplitter
            system_name: Name of the system
            
        Returns:
            Dictionary with diagrams ready for React frontend
        """
        diagrams = []
        
        for idx, sub_model in enumerate(sub_models):
            diagram_id = sub_model.get('relationship_id', f'diagram_{idx}')
            
            # Extract nodes and links
            nodes = self._extract_nodes(sub_model)
            links = self._extract_links(sub_model, nodes)
            
            # Get layout if available
            layout = sub_model.get('layout', {})
            
            # Apply layout positions to nodes
            if layout and 'elements' in layout:
                for node in nodes:
                    element_name = node['name']
                    if element_name in layout['elements']:
                        elem_layout = layout['elements'][element_name]
                        node['x'] = elem_layout.get('x', 0)
                        node['y'] = elem_layout.get('y', 0)
                        node['fx'] = elem_layout.get('x')  # Fixed position
                        node['fy'] = elem_layout.get('y')
            
            # Determine title
            if sub_model.get('is_full_diagram'):
                title = f"Complete {system_name} Diagram"
            else:
                rel = sub_model.get('relationship', {})
                from_name = rel.get('from', '')
                to_name = rel.get('to', '')
                title = f"{from_name} → {to_name}" if from_name and to_name else f"Relationship {idx + 1}"
            
            diagrams.append({
                'id': diagram_id,
                'title': title,
                'nodes': nodes,
                'links': links,
                'metadata': {
                    'is_full_diagram': sub_model.get('is_full_diagram', False),
                    'system_boundary': sub_model.get('system_boundary', system_name),
                    'relationship': sub_model.get('relationship')
                }
            })
        
        return {
            'system_name': system_name,
            'diagrams': diagrams,
            'total_diagrams': len(diagrams)
        }
    
    def _extract_nodes(self, sub_model: Dict) -> List[Dict]:
        """Extract nodes from sub_model."""
        nodes = []
        element_types = sub_model.get('element_types', {})
        elements = sub_model.get('elements', {})
        
        # Extract parts
        parts = elements.get('components', [])
        for part in parts:
            if isinstance(part, dict) and part.get('name'):
                part_name = part['name']
                # Check if it's actually a part (not an actor)
                is_actor = any(a.get('name') == part_name 
                             for a in sub_model.get('actors', []))
                if not is_actor:
                    nodes.append({
                        'id': f"part_{part_name}",
                        'name': part_name,
                        'type': 'part',
                        'width': 140,
                        'height': 60,
                        'x': 0,
                        'y': 0,
                        'doc': part.get('doc', '')
                    })
        
        # Extract actors
        actors = sub_model.get('actors', [])
        for actor in actors:
            if isinstance(actor, dict) and actor.get('name'):
                nodes.append({
                    'id': f"actor_{actor['name']}",
                    'name': actor['name'],
                    'type': 'actor',
                    'size': 55,
                    'width': 55,
                    'height': 55,
                    'x': 0,
                    'y': 0,
                    'doc': actor.get('doc', '')
                })
        
        # Extract use cases
        use_cases = elements.get('functional_nodes', [])
        for uc in use_cases:
            if isinstance(uc, dict) and uc.get('name'):
                nodes.append({
                    'id': f"usecase_{uc['name']}",
                    'name': uc['name'],
                    'type': 'use_case',
                    'width': 280,
                    'height': 90,
                    'x': 0,
                    'y': 0,
                    'doc': uc.get('doc', ''),
                    'objectives': uc.get('objectives', [])
                })
        
        # Extract SoI if present
        if 'SoI' in str(sub_model) or any('SoI' in str(v) for v in sub_model.values()):
            nodes.append({
                'id': 'soi',
                'name': 'SoI',
                'type': 'soi',
                'width': 80,
                'height': 50,
                'x': 0,
                'y': 0
            })
        
        return nodes
    
    def _extract_links(self, sub_model: Dict, nodes: List[Dict]) -> List[Dict]:
        """Extract links/connections from sub_model."""
        links = []
        node_map = {node['name']: node['id'] for node in nodes}
        
        # Get connections
        if sub_model.get('is_full_diagram'):
            # Full diagram: use all connections
            connections = sub_model.get('all_relationships', [])
        else:
            # Individual relationship: use single connection
            rel = sub_model.get('relationship', {})
            if rel:
                connections = [rel]
            else:
                connections = []
        
        for conn in connections:
            from_name = conn.get('from', '')
            to_name = conn.get('to', '')
            
            source_id = node_map.get(from_name)
            target_id = node_map.get(to_name)
            
            if source_id and target_id:
                # Check if it's a dashed line (SoI connections)
                is_dashed = to_name == 'SoI' or from_name == 'SoI'
                
                links.append({
                    'source': source_id,
                    'target': target_id,
                    'dashed': is_dashed,
                    'fromName': from_name,
                    'toName': to_name
                })
        
        return links
    
    def save(self, data: Dict, filename: str = "react_diagrams.json"):
        """Save diagram data to JSON file."""
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ React diagram data saved to: {output_path}")
        return str(output_path)

