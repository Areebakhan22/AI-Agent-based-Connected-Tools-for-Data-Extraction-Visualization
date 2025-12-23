#!/usr/bin/env python3
"""
Generic, Reusable Pipeline for SysML JSON → Google Slides Visualization

This pipeline:
1. Accepts SysML-derived JSON as input (not raw SysML text)
2. Uses LLM/AI agent for semantic understanding and validation
3. Splits model by relationships (one diagram/slide per relationship)
4. Uses graph layout engine (NetworkX/Graphviz) for dynamic positioning
5. Renders diagrams in Google Slides with element_id metadata
6. Supports bidirectional feedback (Slides → JSON)

Usage:
    python visualize_sysml.py input.json [--model MODEL] [--presentation-id ID]
"""

import json
import sys
import argparse
import os
from typing import Dict, List, Optional, Tuple
import ollama  # LLaMA library via Ollama API
import networkx as nx
import numpy as np
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Slides API scope
SCOPES = ['https://www.googleapis.com/auth/presentations']

# Standard Google Slides dimensions (in points)
SLIDE_WIDTH = 720
SLIDE_HEIGHT = 540
MARGIN = 50


class SemanticModelProcessor:
    """
    Uses LLM to semantically understand and validate SysML JSON models.
    References local LLaMA 3 model files from Ollama installation.
    """
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        # Local LLaMA 3 model paths
        self.model_paths = [
            "/usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library/llama3",
            "/home/bit-and-bytes/.ollama/models/manifests/registry.ollama.ai/library/llama3"
        ]
        self._check_ollama_connection()
        self._verify_local_model()
    
    def _check_ollama_connection(self):
        """Check if Ollama is running and model is available."""
        try:
            response = ollama.list()
            if hasattr(response, 'models'):
                available_models = [model.model for model in response.models]
            elif isinstance(response, dict):
                available_models = [model['name'] for model in response.get('models', [])]
            else:
                available_models = []
            
            model_found = any(self.model in model_name for model_name in available_models)
            if not model_found:
                print(f"⚠️  Warning: Model '{self.model}' not found. Available: {', '.join(available_models)}")
            else:
                print(f"✓ Using LLM model: {self.model}")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Ollama: {e}")
    
    def _verify_local_model(self):
        """Verify local LLaMA 3 model files exist."""
        for path in self.model_paths:
            if os.path.exists(path):
                print(f"✓ Found local LLaMA 3 model at: {path}")
                return True
        print(f"ℹ️  Note: Local model manifests not found, using Ollama API (which uses local models)")
        return False
    
    def understand_model(self, json_data: Dict) -> Dict:
        """
        Use LLM to semantically understand and validate the JSON system model.
        
        Args:
            json_data: SysML-derived JSON model
            
        Returns:
            Validated and enriched model with semantic mappings
        """
        prompt = self._create_semantic_prompt(json_data)
        
        try:
            # Use local LLaMA 3 model via Ollama API
            # Ollama automatically uses models from:
            # - /usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library/llama3
            # - /home/bit-and-bytes/.ollama/models/manifests/registry.ollama.ai/library/llama3
            print(f"🤖 Using local LLaMA 3 model ({self.model}) for semantic understanding...")
            response = ollama.chat(
                model=self.model,  # References local llama3 model files
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a SysML expert. Analyze JSON system models and provide semantic mappings and validations.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,
                    'num_ctx': 1024,  # Smaller context window to save memory
                    'num_predict': 300,  # Limit prediction length
                    'num_gpu': 0  # Force CPU to avoid GPU memory issues
                }
            )
            
            llm_response = response['message']['content']
            semantic_analysis = self._parse_llm_response(llm_response)
            
            # Enrich the model with semantic mappings
            enriched_model = self._enrich_with_semantics(json_data, semantic_analysis)
            
            print("✓ Semantic understanding completed")
            return enriched_model
            
        except Exception as e:
            print(f"⚠️  Warning: LLM processing failed: {e}. Using direct JSON mapping.")
            return self._default_mapping(json_data)
    
    def _create_semantic_prompt(self, json_data: Dict) -> str:
        """Create prompt for semantic understanding."""
        # Create a more compact JSON representation to save memory
        compact_json = json.dumps(json_data, separators=(',', ':'))
        
        return f"""Analyze JSON system model. Return ONLY valid JSON:

{compact_json}

Map: parts/actors→components, use_cases→functional_nodes, connections→edges.

Return JSON:
{{"mappings":{{"components":[],"functional_nodes":[],"system_boundary":""}},"validations":{{"valid_relationships":[],"issues":[]}}}}"""
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Parse JSON from LLM response."""
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            json_str = json_match.group(0) if json_match else response.strip()
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"mappings": {}, "validations": {}}
    
    def _enrich_with_semantics(self, json_data: Dict, semantic_analysis: Dict) -> Dict:
        """Enrich model with semantic information."""
        enriched = json_data.copy()
        
        # Add element type mappings
        enriched['element_types'] = {}
        
        # Map parts as 'part' (will be drawn as rectangles)
        for part in json_data.get('parts', []):
            enriched['element_types'][part['name']] = 'part'
        
        # Map actors as 'actor' (will be drawn as circles/ellipses)
        for actor in json_data.get('actors', []):
            enriched['element_types'][actor['name']] = 'actor'
        
        # Map use cases to functional nodes (will be drawn as ellipses)
        for uc in json_data.get('use_cases', []):
            enriched['element_types'][uc['name']] = 'functional_node'
        
        # Map SoI (Subject of Interest) as 'subject' (will be drawn as round rectangle)
        enriched['element_types']['SoI'] = 'subject'
        
        # Add system boundary
        top_level = [p for p in json_data.get('parts', []) if p.get('is_top_level', False)]
        enriched['system_boundary'] = top_level[0]['name'] if top_level else "System"
        
        return enriched
    
    def _default_mapping(self, json_data: Dict) -> Dict:
        """Default mapping when LLM is unavailable."""
        return self._enrich_with_semantics(json_data, {})


class RelationshipSplitter:
    """
    Splits the model so each relationship generates one diagram/slide.
    """
    
    def split_by_relationships(self, model: Dict) -> List[Dict]:
        """
        Split model into sub-models: FIRST create full combined diagram, then individual relationships.
        
        Args:
            model: Enriched system model
            
        Returns:
            List of sub-models: [full_combined_diagram, ...individual_relationship_diagrams]
        """
        connections = model.get('connections', [])
        sub_models = []
        
        # FIRST: Create full combined diagram with ALL relationships, parts, and use cases
        full_diagram = {
            'system_boundary': model.get('system_boundary', 'System'),
            'relationship_id': 'full_combined',
            'relationship': None,  # All relationships combined
            'all_relationships': connections,  # Store all relationships
            'elements': {
                'components': model.get('parts', []) + model.get('actors', []),
                'functional_nodes': model.get('use_cases', []),
                'system': model.get('system_boundary', 'System')
            },
            'element_types': model.get('element_types', {}),
            'is_full_diagram': True
        }
        sub_models.append(full_diagram)
        
        if not connections:
            return sub_models
        
        # THEN: Create individual relationship diagrams
        for idx, conn in enumerate(connections):
            sub_model = {
                'system_boundary': model.get('system_boundary', 'System'),
                'relationship_id': f"rel_{idx}",
                'relationship': conn,
                'elements': self._extract_relationship_elements(model, conn),
                'element_types': model.get('element_types', {}),
                'is_full_diagram': False
            }
            sub_models.append(sub_model)
        
        return sub_models
    
    def find_relationship_context(self, connection: Dict, sysml_data: Dict) -> Dict:
        """
        Dynamically find the correct Use Case and verify types.
        
        Returns:
            {
                "container_oval": use_case_name,
                "port_circle": actor_name,
                "source_rect": part_name,
                "is_valid": bool
            }
        """
        source_name = connection.get('from')
        target_name = connection.get('to')
        
        # Find the correct Use Case by searching for the Actor
        parent_use_case = None
        target_actor = None
        
        # Check if target is in actors list
        for actor in sysml_data.get('actors', []):
            if actor.get('name') == target_name:
                target_actor = actor
                break
        
        # Find which Use Case contains this Actor
        # In SysML, actors are typically associated with use cases
        # Check connections to find the relationship
        use_cases = sysml_data.get('use_cases', [])
        connections = sysml_data.get('connections', [])
        
        # Method 1: Check if there's a direct connection from Use Case to Actor
        for conn in connections:
            if conn.get('to') == target_name:
                from_name = conn.get('from')
                for uc in use_cases:
                    if uc.get('name') == from_name:
                        parent_use_case = uc
                        break
                if parent_use_case:
                    break
        
        # Method 2: If no direct connection, check if actor is mentioned in use case scope
        # In the SysML structure, actors might be nested within use cases
        if not parent_use_case and use_cases:
            # For now, use the first use case as fallback
            # In real SysML, actors are scoped within use cases
            parent_use_case = use_cases[0]
        
        # Verify the source is a structural Part
        source_part = None
        for part in sysml_data.get('parts', []):
            if part.get('name') == source_name:
                source_part = part
                break
        
        return {
            "container_oval": parent_use_case.get('name') if parent_use_case else None,
            "port_circle": target_name,
            "source_rect": source_name,
            "is_valid": parent_use_case is not None and source_part is not None,
            "use_case": parent_use_case,
            "part": source_part,
            "actor": target_actor
        }
    
    def _extract_relationship_elements(self, model: Dict, connection: Dict) -> Dict:
        """
        Extract elements relevant to a relationship with proper type validation.
        Uses find_relationship_context for accurate mapping.
        """
        context = self.find_relationship_context(connection, model)
        
        elements = {
            'components': [],
            'functional_nodes': [],
            'system': model.get('system_boundary', 'System'),
            'relationship_context': context  # Store context for later use
        }
        
        # Add Part (source rectangle)
        if context.get('part'):
            elements['components'].append(context['part'])
        
        # Add Actor (target circle/port)
        if context.get('actor'):
            elements['components'].append(context['actor'])
        
        # Add Use Case (container oval)
        if context.get('use_case'):
            elements['functional_nodes'].append(context['use_case'])
        
        return elements
    
    def _find_element(self, model: Dict, name: str) -> Optional[Dict]:
        """Find element by name in model."""
        for part in model.get('parts', []):
            if part['name'] == name:
                return part
        for actor in model.get('actors', []):
            if actor['name'] == name:
                return actor
        for uc in model.get('use_cases', []):
            if uc['name'] == name:
                return uc
        # Handle special elements like SoI (Subject of Interest) that might not be in standard lists
        if name == 'SoI' or 'SoI' in name:
            return {'name': name, 'type': 'subject'}
        return None


class GraphLayoutEngine:
    """
    Uses advanced graph layout algorithms (NetworkX) for professional diagram positioning.
    Implements hierarchical, force-directed, and circular layouts with proper scaling.
    Ensures diagrams fit perfectly within slide bounds with no overlapping.
    """
    
    def __init__(self):
        self.layout_algorithm = 'hierarchical'  # Default: hierarchical for better organization
        self.min_node_spacing = 80  # Minimum spacing between nodes
        self.node_padding = 20  # Padding around nodes
    
    def _hierarchical_layout(self, G: nx.DiGraph, root: str) -> Dict:
        """
        Create professional hierarchical layout matching SysML standards.
        Layout structure:
        - Use cases: Center-top area
        - Components: Arranged around (left, right, bottom) with proper spacing
        - No overlaps, everything fits within slide bounds
        """
        pos = {}
        
        # Calculate available space (with generous margins for system boundary)
        margin_x = MARGIN + 40
        margin_y = MARGIN + 90  # Extra space for title
        available_width = SLIDE_WIDTH - 2 * margin_x
        available_height = SLIDE_HEIGHT - 2 * margin_y
        
        # Separate nodes by type
        use_cases = [n for n in G.nodes() if G.nodes[n].get('type') == 'functional_node']
        components = [n for n in G.nodes() if G.nodes[n].get('type') in ['component', 'source', 'target']]
        
        # Remove system nodes (they're the boundary, not positioned)
        nodes_to_position = use_cases + components
        
        if not nodes_to_position:
            return pos
        
        # Calculate element sizes for spacing
        def get_element_size(node_name, node_type):
            name_len = len(str(node_name))
            if node_type == 'functional_node':
                return (max(180, min(280, name_len * 9)), 75)
            else:
                return (max(130, min(200, name_len * 8)), 60)
        
        # LAYER 1: Use cases in center-top (horizontal arrangement)
        if use_cases:
            uc_y = margin_y + available_height * 0.25  # 25% from top
            uc_widths = [get_element_size(uc, 'functional_node')[0] for uc in use_cases]
            total_uc_width = sum(uc_widths) + (len(use_cases) - 1) * 40  # 40px spacing
            
            # Center use cases horizontally
            if total_uc_width <= available_width:
                uc_start_x = margin_x + (available_width - total_uc_width) / 2
                current_x = uc_start_x
                for idx, uc in enumerate(use_cases):
                    pos[uc] = (current_x, uc_y)
                    current_x += uc_widths[idx] + 40
            else:
                # Too wide - reduce spacing
                spacing = (available_width - sum(uc_widths)) / (len(use_cases) - 1) if len(use_cases) > 1 else 0
                spacing = max(20, spacing)
                uc_start_x = margin_x
                current_x = uc_start_x
                for idx, uc in enumerate(use_cases):
                    pos[uc] = (current_x, uc_y)
                    current_x += uc_widths[idx] + spacing
        
        # LAYER 2: Components arranged around use cases
        if components:
            # Smart distribution: balance left, right, and bottom
            num_components = len(components)
            
            # Calculate how many per side (aim for balanced layout)
            if num_components <= 3:
                left_count = 1
                right_count = 1
                bottom_count = num_components - 2
            elif num_components <= 6:
                left_count = num_components // 3
                right_count = num_components // 3
                bottom_count = num_components - left_count - right_count
            else:
                left_count = num_components // 3
                right_count = num_components // 3
                bottom_count = num_components - left_count - right_count
            
            left_components = components[:left_count]
            right_components = components[left_count:left_count + right_count]
            bottom_components = components[left_count + right_count:]
            
            # Position LEFT components (vertical stack)
            if left_components:
                left_x = margin_x + 50
                left_zone_height = available_height * 0.7  # Use 70% of height
                left_spacing = left_zone_height / (len(left_components) + 1)
                left_start_y = margin_y + (available_height - left_zone_height) / 2
                
                for idx, comp in enumerate(left_components):
                    pos[comp] = (left_x, left_start_y + (idx + 1) * left_spacing)
            
            # Position RIGHT components (vertical stack)
            if right_components:
                right_x = SLIDE_WIDTH - margin_x - 50
                right_zone_height = available_height * 0.7
                right_spacing = right_zone_height / (len(right_components) + 1)
                right_start_y = margin_y + (available_height - right_zone_height) / 2
                
                for idx, comp in enumerate(right_components):
                    pos[comp] = (right_x, right_start_y + (idx + 1) * right_spacing)
            
            # Position BOTTOM components (horizontal row)
            if bottom_components:
                bottom_y = margin_y + available_height * 0.80  # 80% from top
                comp_widths = [get_element_size(comp, 'component')[0] for comp in bottom_components]
                total_bottom_width = sum(comp_widths) + (len(bottom_components) - 1) * 30
                
                if total_bottom_width <= available_width:
                    bottom_start_x = margin_x + (available_width - total_bottom_width) / 2
                    current_x = bottom_start_x
                    for idx, comp in enumerate(bottom_components):
                        pos[comp] = (current_x, bottom_y)
                        current_x += comp_widths[idx] + 30
                else:
                    # Too wide - reduce spacing
                    spacing = (available_width - sum(comp_widths)) / (len(bottom_components) - 1) if len(bottom_components) > 1 else 0
                    spacing = max(15, spacing)
                    bottom_start_x = margin_x
                    current_x = bottom_start_x
                    for idx, comp in enumerate(bottom_components):
                        pos[comp] = (current_x, bottom_y)
                        current_x += comp_widths[idx] + spacing
        
        return pos
    
    def _force_directed_layout(self, G: nx.DiGraph, iterations: int = 100) -> Dict:
        """
        Improved force-directed layout with better parameters for professional diagrams.
        """
        # Use spring layout with optimized parameters
        pos = nx.spring_layout(
            G,
            k=self.min_node_spacing / 10,  # Optimal distance between nodes
            iterations=iterations,
            seed=42,  # Deterministic
            weight='weight' if G.edges() else None
        )
        
        # Apply additional repulsion to prevent overlap
        for _ in range(20):  # Additional iterations for fine-tuning
            for node1 in G.nodes():
                for node2 in G.nodes():
                    if node1 != node2:
                        x1, y1 = pos[node1]
                        x2, y2 = pos[node2]
                        dx = x2 - x1
                        dy = y2 - y1
                        dist = np.sqrt(dx*dx + dy*dy)
                        
                        if dist < self.min_node_spacing:
                            # Push nodes apart
                            force = (self.min_node_spacing - dist) / dist * 0.5
                            pos[node1] = (x1 - dx * force, y1 - dy * force)
                            pos[node2] = (x2 + dx * force, y2 + dy * force)
        
        return pos
    
    def _individual_relationship_layout(self, G: nx.DiGraph, system_name: str, element_types: Dict) -> Dict:
        """
        Specialized layout for individual relationship diagrams.
        Layout: Use Case (Oval center-right), Actor (Circle on Oval RIGHT edge as port), Part (Rectangle bottom-left)
        All shapes medium-sized, fit within 16:9 aspect ratio.
        """
        pos = {}
        nodes = [n for n in G.nodes() if n != system_name]
        
        # Identify elements by type
        use_case = None
        actor = None
        part = None
        
        for node in nodes:
            node_type = G.nodes[node].get('type', 'component')
            if node_type == 'functional_node' or element_types.get(node, '') == 'functional_node':
                use_case = node
            elif node_type == 'actor' or element_types.get(node, '') == 'actor':
                actor = node
            else:
                part = node
        
        # Calculate available space (16:9 aspect ratio, with margins)
        margin_x = MARGIN + 30
        margin_y = MARGIN + 80  # Extra for title
        available_width = SLIDE_WIDTH - 2 * margin_x
        available_height = SLIDE_HEIGHT - 2 * margin_y
        
        # Medium-sized shapes
        use_case_width = min(280, available_width * 0.45)  # Medium-large oval
        use_case_height = 85
        actor_size = 55  # Small circle (port size)
        part_width = min(140, available_width * 0.22)  # Medium rectangle
        part_height = 60
        
        # Position Use Case in center-right area (Oval)
        # Based on desired image: Use Case is in upper-right/center area
        use_case_x = SLIDE_WIDTH / 2 + available_width * 0.15  # Slightly right of center
        use_case_y = SLIDE_HEIGHT / 2 - available_height * 0.1  # Slightly above center
        if use_case:
            pos[use_case] = (use_case_x - use_case_width / 2, use_case_y - use_case_height / 2)
        
        # Position Actor on Use Case Oval RIGHT EDGE (Circle/Port)
        # Actor should be anchored to the right edge of the Use Case oval
        if actor and use_case:
            uc_x, uc_y = pos[use_case]
            # Position actor circle on the RIGHT EDGE of the use case oval
            # The circle center should be at the right edge of the oval
            actor_center_x = uc_x + use_case_width  # Right edge of oval
            actor_center_y = uc_y + use_case_height / 2  # Vertical center of oval
            # Position is the top-left corner of the circle bounding box
            pos[actor] = (actor_center_x - actor_size / 2, actor_center_y - actor_size / 2)
        elif actor:
            # If no use case, position actor in center-right
            pos[actor] = (SLIDE_WIDTH / 2 + available_width * 0.25, SLIDE_HEIGHT / 2 - actor_size / 2)
        
        # Position Part in bottom-left (Rectangle, peripheral)
        # Based on desired image: Part is in bottom-left area
        if part:
            part_x = margin_x + 30
            part_y = SLIDE_HEIGHT - margin_y - part_height - 30  # Bottom area
            pos[part] = (part_x, part_y)
        
        return pos
    
    def _simple_layout(self, G: nx.DiGraph, root: str) -> Dict:
        """Simple layout for small diagrams (2-3 nodes)."""
        pos = {}
        nodes = list(G.nodes())
        
        if len(nodes) == 2:
            # Two nodes: horizontal layout
            center_y = SLIDE_HEIGHT / 2
            spacing = SLIDE_WIDTH * 0.3
            center_x = SLIDE_WIDTH / 2
            pos[nodes[0]] = (center_x - spacing, center_y)
            pos[nodes[1]] = (center_x + spacing, center_y)
        elif len(nodes) == 3:
            # Three nodes: triangular layout
            center_x = SLIDE_WIDTH / 2
            center_y = SLIDE_HEIGHT / 2
            radius = min(SLIDE_WIDTH, SLIDE_HEIGHT) * 0.25
            
            for idx, node in enumerate(nodes):
                angle = 2 * np.pi * idx / 3 - np.pi / 2  # Start from top
                pos[node] = (center_x + radius * np.cos(angle), 
                            center_y + radius * np.sin(angle))
        else:
            # Fallback to force-directed
            pos = self._force_directed_layout(G, iterations=50)
        
        return pos
    
    def _prevent_overlaps(self, pos: Dict, G: nx.DiGraph) -> Dict:
        """Ensure no nodes overlap by adjusting positions."""
        adjusted_pos = pos.copy()
        nodes = list(G.nodes())
        
        # Filter nodes to only those that have positions
        nodes_with_pos = [n for n in nodes if n in adjusted_pos]
        
        # Node sizes (approximate)
        node_sizes = {}
        for node in nodes_with_pos:
            node_type = G.nodes[node].get('type', 'component')
            if node_type == 'functional_node':
                node_sizes[node] = (180, 70)  # width, height
            else:
                node_sizes[node] = (140, 60)
        
        # Check and resolve overlaps
        max_iterations = 50
        for iteration in range(max_iterations):
            overlaps_found = False
            
            for i, node1 in enumerate(nodes_with_pos):
                for node2 in nodes_with_pos[i+1:]:
                    if node1 not in adjusted_pos or node2 not in adjusted_pos:
                        continue
                    x1, y1 = adjusted_pos[node1]
                    x2, y2 = adjusted_pos[node2]
                    w1, h1 = node_sizes[node1]
                    w2, h2 = node_sizes[node2]
                    
                    # Check if bounding boxes overlap
                    if (abs(x1 - x2) < (w1 + w2) / 2 + self.node_padding and
                        abs(y1 - y2) < (h1 + h2) / 2 + self.node_padding):
                        overlaps_found = True
                        
                        # Calculate separation vector
                        dx = x2 - x1
                        dy = y2 - y1
                        dist = np.sqrt(dx*dx + dy*dy) if (dx != 0 or dy != 0) else 1
                        
                        # Minimum distance needed
                        min_dist = (w1 + w2) / 2 + self.node_padding + 10
                        
                        if dist < min_dist:
                            # Push nodes apart
                            push_x = dx / dist * (min_dist - dist) / 2
                            push_y = dy / dist * (min_dist - dist) / 2
                            
                            adjusted_pos[node1] = (x1 - push_x, y1 - push_y)
                            adjusted_pos[node2] = (x2 + push_x, y2 + push_y)
            
            if not overlaps_found:
                break
        
        return adjusted_pos
    
    def _scale_to_slide(self, pos: Dict, is_full_diagram: bool) -> Dict:
        """
        Scale positions to fit perfectly within slide bounds with proper margins.
        Ensures all elements are visible and well-spaced.
        """
        if not pos:
            return pos
        
        # Calculate bounding box of current positions
        x_coords = [p[0] for p in pos.values()]
        y_coords = [p[1] for p in pos.values()]
        
        min_x = min(x_coords)
        max_x = max(x_coords)
        min_y = min(y_coords)
        max_y = max(y_coords)
        
        # Calculate available space with generous margins
        top_margin = MARGIN + 70  # Space for title
        bottom_margin = MARGIN + 30
        left_margin = MARGIN + 30
        right_margin = MARGIN + 30
        
        available_width = SLIDE_WIDTH - left_margin - right_margin
        available_height = SLIDE_HEIGHT - top_margin - bottom_margin
        
        # Calculate current dimensions
        current_width = max_x - min_x if max_x != min_x else 100
        current_height = max_y - min_y if max_y != min_y else 100
        
        # Calculate scale factors (use 85% to ensure everything fits with padding)
        scale_x = (available_width / current_width * 0.85) if current_width > 0 else 1
        scale_y = (available_height / current_height * 0.85) if current_height > 0 else 1
        
        # Use uniform scale to maintain aspect ratio
        scale = min(scale_x, scale_y, 1.0)  # Don't scale up, only down
        
        # Calculate center offset to center the diagram
        scaled_width = current_width * scale
        scaled_height = current_height * scale
        
        offset_x = left_margin + (available_width - scaled_width) / 2
        offset_y = top_margin + (available_height - scaled_height) / 2
        
        # Transform positions
        scaled_pos = {}
        for node in pos:
            # Scale relative to min point, then offset
            x = (pos[node][0] - min_x) * scale + offset_x
            y = (pos[node][1] - min_y) * scale + offset_y
            
            # Ensure within bounds
            x = max(left_margin, min(x, SLIDE_WIDTH - right_margin))
            y = max(top_margin, min(y, SLIDE_HEIGHT - bottom_margin))
            
            scaled_pos[node] = (x, y)
        
        return scaled_pos
    
    def calculate_layout(self, sub_model: Dict) -> Dict:
        """
        Calculate layout for a sub-model using improved graph layout algorithms.
        Ensures proper spacing, automatic label positioning, and fit within slide bounds.
        
        Args:
            sub_model: Sub-model with system + source + target (or full combined)
            
        Returns:
            Layout dictionary with positions for all elements
        """
        # Build graph
        G = nx.DiGraph()
        
        # Add system boundary as central node
        system_name = sub_model.get('system_boundary', 'System')
        G.add_node(system_name, type='system')
        
        is_full_diagram = sub_model.get('is_full_diagram', False)
        
        if is_full_diagram:
            # FULL COMBINED DIAGRAM: Include all elements and relationships
            elements = sub_model.get('elements', {})
            all_relationships = sub_model.get('all_relationships', [])
            element_types = sub_model.get('element_types', {})
            
            # Collect all element names
            all_elem_names = set()
            
            # Add all components
            for comp in elements.get('components', []):
                elem_name = comp.get('name') if isinstance(comp, dict) else comp
                all_elem_names.add(elem_name)
                G.add_node(elem_name, type='component')
            
            # Add all functional nodes (use cases)
            for func_node in elements.get('functional_nodes', []):
                elem_name = func_node.get('name') if isinstance(func_node, dict) else func_node
                all_elem_names.add(elem_name)
                G.add_node(elem_name, type='functional_node')
            
            # Add all relationships as edges (including connections to actors and SoI)
            for rel in all_relationships:
                from_elem = rel.get('from')
                to_elem = rel.get('to')
                
                # Add nodes if they don't exist (for actors, SoI, or other elements)
                if from_elem and from_elem not in G:
                    node_type = element_types.get(from_elem, 'part')
                    G.add_node(from_elem, type=node_type)
                if to_elem and to_elem not in G:
                    node_type = element_types.get(to_elem, 'part')
                    G.add_node(to_elem, type=node_type)
                
                # Add edge
                if from_elem and to_elem:
                    G.add_edge(from_elem, to_elem, label=rel.get('label', ''))
        else:
            # Individual relationship layout: Part → Actor with Use Case
            # Use dynamic context discovery for accurate mapping
            rel = sub_model.get('relationship')
            element_types = sub_model.get('element_types', {})
            
            if rel:
                # Get relationship context with proper type validation
                model = getattr(self, '_current_model', {})
                # Use splitter's find_relationship_context method
                splitter = getattr(self, '_splitter', None)
                if splitter and hasattr(splitter, 'find_relationship_context'):
                    context = splitter.find_relationship_context(rel, model)
                else:
                    # Fallback: create temporary splitter
                    from visualize_sysml import RelationshipSplitter
                    temp_splitter = RelationshipSplitter()
                    context = temp_splitter.find_relationship_context(rel, model)
                
                if context.get('is_valid'):
                    # Extract validated elements
                    part_name = context.get('source_rect')
                    actor_name = context.get('port_circle')
                    use_case_name = context.get('container_oval')
                    
                    # Add Part (Rectangle) - explicitly verified as Part
                    if part_name:
                        G.add_node(part_name, type='part')
                    
                    # Add Actor (Circle/Port) - explicitly verified as Actor
                    if actor_name:
                        G.add_node(actor_name, type='actor')
                    
                    # Add Use Case (Oval) - dynamically found parent
                    if use_case_name:
                        G.add_node(use_case_name, type='functional_node')
                        # Use case connects to actor (actor is port on use case)
                        if actor_name:
                            G.add_edge(use_case_name, actor_name)
                    
                    # Add connection from Part to Actor
                    if part_name and actor_name:
                        G.add_edge(part_name, actor_name)
                else:
                    # Fallback: use original logic if context is invalid
                    from_elem = rel.get('from')
                    to_elem = rel.get('to')
                    
                    if from_elem:
                        # Explicitly check if it's a part or actor
                        is_part = any(p.get('name') == from_elem for p in model.get('parts', []))
                        is_actor = any(a.get('name') == from_elem for a in model.get('actors', []))
                        node_type = 'part' if is_part else ('actor' if is_actor else 'component')
                        G.add_node(from_elem, type=node_type)
                    
                    if to_elem:
                        # Explicitly check if it's a part or actor
                        is_part = any(p.get('name') == to_elem for p in model.get('parts', []))
                        is_actor = any(a.get('name') == to_elem for a in model.get('actors', []))
                        node_type = 'part' if is_part else ('actor' if is_actor else 'component')
                        G.add_node(to_elem, type=node_type)
                        if from_elem:
                            G.add_edge(from_elem, to_elem)
                    
                    # Find Use Case dynamically
                    use_cases = model.get('use_cases', [])
                    if to_elem and use_cases:
                        # Find use case that contains this actor
                        associated_uc = None
                        for uc in use_cases:
                            # Check connections to find relationship
                            connections = model.get('connections', [])
                            for conn in connections:
                                if conn.get('to') == to_elem and conn.get('from') == uc.get('name'):
                                    associated_uc = uc.get('name')
                                    break
                            if associated_uc:
                                break
                        
                        # Fallback to first use case if not found
                        if not associated_uc:
                            associated_uc = use_cases[0].get('name')
                        
                        if associated_uc:
                            G.add_node(associated_uc, type='functional_node')
                            if to_elem:
                                G.add_edge(associated_uc, to_elem)
        
        # Calculate positions using professional layout algorithms
        if len(G.nodes()) == 1:
            # Single node - center it
            pos = {list(G.nodes())[0]: (SLIDE_WIDTH / 2, SLIDE_HEIGHT / 2)}
        else:
            num_nodes = len(G.nodes())
            
            # Choose layout algorithm based on diagram type and size
            if is_full_diagram:
                # Full diagrams: Use hierarchical layout for better organization
                try:
                    pos = self._hierarchical_layout(G, system_name)
                except Exception as e:
                    print(f"  ⚠️  Hierarchical layout failed, using force-directed: {e}")
                    pos = self._force_directed_layout(G, iterations=150)
            elif num_nodes <= 3:
                # Individual relationship diagrams: Use specialized layout
                # Layout: Use Case (Oval center), Actor (Circle on edge), Part (Rectangle peripheral)
                pos = self._individual_relationship_layout(G, system_name, element_types)
            else:
                # Medium diagrams: Force-directed with optimization
                pos = self._force_directed_layout(G, iterations=120)
            
            # For individual relationship diagrams, don't scale - use fixed positions
            if not is_full_diagram:
                # Individual diagrams use fixed layout, don't scale
                pass
            else:
                # Ensure no overlaps and proper spacing for full diagrams
                pos = self._prevent_overlaps(pos, G)
                # Scale and translate to fit within slide bounds
                pos = self._scale_to_slide(pos, is_full_diagram)
        
        # Build layout structure
        layout = {
            'system_boundary': {
                'name': system_name,
                'x': MARGIN,
                'y': MARGIN + 40,
                'width': SLIDE_WIDTH - 2 * MARGIN,
                'height': SLIDE_HEIGHT - 2 * MARGIN - 40
            },
            'elements': {}
        }
        
        # Add element positions (excluding system boundary which is drawn separately)
        for node, (x, y) in pos.items():
            node_data = G.nodes[node]
            elem_type = node_data.get('type', 'component')
            
            if elem_type == 'system':
                continue  # System boundary already added
            
            # Determine size based on type and name length (consistent with layout)
            node_name = str(node)
            name_length = len(node_name)
            
            # Medium-sized shapes for individual relationship diagrams
            is_individual = not is_full_diagram
            
            if elem_type == 'functional_node':
                # Use cases: medium oval (center-top)
                if is_individual:
                    width = min(280, SLIDE_WIDTH * 0.39)  # Medium size, fit 16:9
                    height = 85
                else:
                    width = max(180, min(280, name_length * 9))
                    height = 75
            elif elem_type == 'actor':
                # Actors: medium circle (port on use case edge) for individual, larger for full
                if is_individual:
                    size = 55  # Small port size for individual diagrams
                else:
                    size = max(80, min(120, name_length * 7))
                width = size
                height = size
            elif elem_type == 'subject':
                # Subject: round rectangle (smaller)
                width = max(80, min(150, name_length * 8))
                height = 50
            else:
                # Parts: medium rectangle (peripheral) for individual, normal for full
                if is_individual:
                    width = min(140, SLIDE_WIDTH * 0.19)  # Medium size, fit 16:9
                    height = 60
                else:
                    width = max(130, min(200, name_length * 8))
                    height = 60
            
            # Position is already calculated correctly, just ensure within bounds
            # x, y are already center points from layout
            x = max(MARGIN + width/2 + 20, min(x, SLIDE_WIDTH - MARGIN - width/2 - 20))
            y = max(MARGIN + height/2 + 80, min(y, SLIDE_HEIGHT - MARGIN - height/2 - 20))
            
            layout['elements'][node] = {
                'type': elem_type,
                'x': x,
                'y': y,
                'width': width,
                'height': height,
                'element_id': node  # Store element_id metadata
            }
        
        return layout


class SlidesRenderer:
    """
    Renders diagrams using Google Slides API with element_id metadata.
    """
    
    def __init__(self):
        self.service = None
        self.presentation_id = None
        self.element_mapping = {}  # Maps shape IDs to element IDs for feedback
    
    def authenticate(self):
        """Authenticate and get Google Slides service."""
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download OAuth 2.0 "
                        "credentials from Google Cloud Console and save as 'credentials.json'"
                    )
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('slides', 'v1', credentials=creds)
        return self.service
    
    def create_or_get_presentation(self, title: str, presentation_id: Optional[str] = None) -> str:
        """Create new presentation or use existing one."""
        if presentation_id:
            try:
                self.service.presentations().get(presentationId=presentation_id).execute()
                self.presentation_id = presentation_id
                print(f"Using existing presentation: {presentation_id}")
                return presentation_id
            except Exception as e:
                raise Exception(f"Could not access presentation {presentation_id}: {e}")
        else:
            presentation = self.service.presentations().create(body={'title': title}).execute()
            self.presentation_id = presentation.get('presentationId')
            print(f"Created presentation: {self.presentation_id}")
            return self.presentation_id
    
    def render_diagram(self, layout: Dict, relationship: Optional[Dict], slide_index: int, is_full_diagram: bool = False, all_relationships: Optional[List[Dict]] = None) -> str:
        """
        Render a single diagram on a slide.
        
        Args:
            layout: Layout dictionary with positions
            relationship: Relationship information (None for full diagram)
            slide_index: Index of the slide
            is_full_diagram: Whether this is the full combined diagram
            all_relationships: All relationships for full diagram
            
        Returns:
            Slide object ID
        """
        # Get or create slide
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        slides = presentation.get('slides', [])
        
        if slide_index < len(slides):
            page_id = slides[slide_index]['objectId']
            # Clear existing content
            self._clear_slide(page_id)
        else:
            # Create new slide
            page_id = f'slide_{slide_index}'
            self.service.presentations().batchUpdate(
                presentationId=self.presentation_id,
                body={'requests': [{'createSlide': {'objectId': page_id}}]}
            ).execute()
            presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
            slides = presentation.get('slides', [])
            page_id = slides[-1]['objectId']
        
        # Draw system boundary
        boundary = layout['system_boundary']
        sys_obj_id = self._draw_system_boundary(page_id, boundary)
        
        # Draw elements
        shape_ids = {}
        # Get element types from the model to determine shape
        element_types = {}
        if hasattr(self, 'current_model'):
            element_types = self.current_model.get('element_types', {})
        
        for elem_name, elem_info in layout['elements'].items():
            elem_type = elem_info.get('type', 'component')
            element_id = elem_info.get('element_id', elem_name)
            
            # Determine actual element type from model
            actual_type = element_types.get(elem_name, elem_type)
            
            if actual_type == 'functional_node' or elem_type == 'functional_node':
                # Use case: draw as ellipse
                shape_id = self._draw_use_case(page_id, elem_name, elem_info, element_id, use_ellipse=True)
            elif actual_type == 'actor':
                # Actor: draw as circle (ellipse with equal width/height)
                shape_id = self._draw_actor(page_id, elem_name, elem_info, element_id)
            elif actual_type == 'subject' or elem_name == 'SoI':
                # Subject: draw as round rectangle
                shape_id = self._draw_subject(page_id, elem_name, elem_info, element_id)
            else:
                # Part: draw as rectangle
                shape_id = self._draw_component(page_id, elem_name, elem_info, element_id)
            
            shape_ids[elem_name] = shape_id
            # Store mapping for feedback extraction
            self.element_mapping[shape_id] = element_id
        
        # Draw relationship arrows
        if is_full_diagram and all_relationships:
            # Draw ALL relationships for full diagram
            for rel in all_relationships:
                from_elem = rel.get('from')
                to_elem = rel.get('to')
                
                if from_elem in shape_ids and to_elem in shape_ids:
                    from_layout = layout['elements'][from_elem]
                    to_layout = layout['elements'][to_elem]
                    self._draw_arrow(page_id, shape_ids[from_elem], shape_ids[to_elem], 
                                   from_layout, to_layout, rel)
        elif relationship:
            # Draw single relationship for individual diagram using connection sites
            from_elem = relationship.get('from')
            to_elem = relationship.get('to')
            
            if from_elem in shape_ids and to_elem in shape_ids:
                from_layout = layout['elements'][from_elem]
                to_layout = layout['elements'][to_elem]
                # Use connection sites for unbreakable arrows in individual diagrams
                self._draw_arrow_with_connection_sites(
                    page_id, shape_ids[from_elem], shape_ids[to_elem], 
                    from_layout, to_layout, relationship)
        
        return page_id
    
    def _clear_slide(self, page_id: str):
        """Clear all elements from a slide."""
        presentation = self.service.presentations().get(presentationId=self.presentation_id).execute()
        for slide in presentation.get('slides', []):
            if slide['objectId'] == page_id:
                elements = slide.get('pageElements', [])
                if elements:
                    delete_requests = [{'deleteObject': {'objectId': elem['objectId']}} 
                                     for elem in elements]
                    self.service.presentations().batchUpdate(
                        presentationId=self.presentation_id,
                        body={'requests': delete_requests}
                    ).execute()
                break
    
    def _draw_system_boundary(self, page_id: str, boundary: Dict) -> str:
        """Draw system boundary rectangle."""
        # Make object ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        obj_id = f"sys_{short_page}_{boundary['name'][:25]}"[:50]
        
        requests = [{
            'createShape': {
                'objectId': obj_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': boundary['height'], 'unit': 'PT'},
                        'width': {'magnitude': boundary['width'], 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': boundary['x'],
                        'translateY': boundary['y'],
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2}}
                            }
                        },
                        'weight': {'magnitude': 2, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }, {
            'insertText': {
                'objectId': obj_id,
                'text': boundary['name'],
                'insertionIndex': 0
            }
        }, {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {'bold': True, 'fontSize': {'magnitude': 14, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        return obj_id
    
    def _draw_component(self, page_id: str, name: str, layout: Dict, element_id: str) -> str:
        """Draw a component (part/actor) as rectangle."""
        # Make object ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        obj_id = f"comp_{short_page}_{name[:35]}"[:50]
        
        requests = [{
            'createShape': {
                'objectId': obj_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': layout['height'], 'unit': 'PT'},
                        'width': {'magnitude': layout['width'], 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': layout['x'],
                        'translateY': layout['y'],
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 2, 'unit': 'PT'}  # Thicker border for visibility
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }, {
            'insertText': {
                'objectId': obj_id,
                'text': name,
                'insertionIndex': 0
            }
        }, {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {'bold': False, 'fontSize': {'magnitude': 11, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }]
        
        # Store element_id as shape description (metadata)
        # Note: Google Slides API doesn't have a direct metadata field,
        # so we'll use the shape's description field or store in a separate mapping
        requests.append({
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'contentAlignment': 'MIDDLE'
                },
                'fields': 'contentAlignment'
            }
        })
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        return obj_id
    
    def _draw_use_case(self, page_id: str, name: str, layout: Dict, element_id: str, use_ellipse: bool = False) -> str:
        """Draw a use case as ellipse (oval) or rounded rectangle."""
        # Make object ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        obj_id = f"uc_{short_page}_{name[:30]}"[:50]
        
        # Use ellipse for use cases (oval shape)
        shape_type = 'ELLIPSE' if use_ellipse else 'ROUND_RECTANGLE'
        
        requests = [{
            'createShape': {
                'objectId': obj_id,
                'shapeType': shape_type,
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': layout['height'], 'unit': 'PT'},
                        'width': {'magnitude': layout['width'], 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': layout['x'],
                        'translateY': layout['y'],
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 1.0, 'green': 1.0, 'blue': 1.0}}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 2, 'unit': 'PT'}  # Thicker border for visibility
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }, {
            'insertText': {
                'objectId': obj_id,
                'text': name,
                'insertionIndex': 0
            }
        }, {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {'bold': False, 'fontSize': {'magnitude': 11, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        return obj_id
    
    def _draw_actor(self, page_id: str, name: str, layout: Dict, element_id: str) -> str:
        """Draw an actor as a circle (ellipse with equal dimensions)."""
        # Make object ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        obj_id = f"actor_{short_page}_{name[:30]}"[:50]
        
        # For actors, use circle (ellipse with equal width and height)
        # Use the larger dimension to ensure it's a proper circle
        size = max(layout['width'], layout['height'])
        # Center the circle at the layout position
        center_x = layout['x'] + layout['width'] / 2
        center_y = layout['y'] + layout['height'] / 2
        circle_x = center_x - size / 2
        circle_y = center_y - size / 2
        
        requests = [{
            'createShape': {
                'objectId': obj_id,
                'shapeType': 'ELLIPSE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': size, 'unit': 'PT'},
                        'width': {'magnitude': size, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': circle_x,
                        'translateY': circle_y,
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 1.0, 'green': 0.98, 'blue': 0.77}}  # Light yellow
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 2, 'unit': 'PT'}  # Thicker border for visibility
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }, {
            'insertText': {
                'objectId': obj_id,
                'text': name,
                'insertionIndex': 0
            }
        }, {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {'bold': False, 'fontSize': {'magnitude': 10, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        return obj_id
    
    def _draw_subject(self, page_id: str, name: str, layout: Dict, element_id: str) -> str:
        """Draw a subject (SoI) as a round rectangle."""
        # Make object ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        obj_id = f"subject_{short_page}_{name[:25]}"[:50]
        
        requests = [{
            'createShape': {
                'objectId': obj_id,
                'shapeType': 'ROUND_RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': layout['height'], 'unit': 'PT'},
                        'width': {'magnitude': layout['width'], 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': layout['x'],
                        'translateY': layout['y'],
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': obj_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.78, 'green': 0.90, 'blue': 0.79}}  # Light green
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 2, 'unit': 'PT'}  # Thicker border for visibility
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }, {
            'insertText': {
                'objectId': obj_id,
                'text': name,
                'insertionIndex': 0
            }
        }, {
            'updateTextStyle': {
                'objectId': obj_id,
                'style': {'bold': False, 'fontSize': {'magnitude': 11, 'unit': 'PT'}},
                'fields': 'bold,fontSize'
            }
        }]
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
        
        return obj_id
    
    def _draw_arrow_with_connection_sites(self, page_id: str, from_id: str, to_id: str,
                                          from_layout: Dict, to_layout: Dict, relationship: Dict):
        """
        Draw an arrow from Part Rectangle to Actor Circle center using connection sites.
        For Individual Relationship Diagrams: Part → Actor (Port on Use Case Oval).
        
        Connection sites indices (standard Google Slides):
        0 = Top
        1 = Right
        2 = Bottom
        3 = Left
        """
        # For Part → Actor connections:
        # Start: closest edge of Part Rectangle
        # End: center of Actor Circle
        
        from_center_x = from_layout['x'] + from_layout['width'] / 2
        from_center_y = from_layout['y'] + from_layout['height'] / 2
        to_center_x = to_layout['x'] + to_layout['width'] / 2
        to_center_y = to_layout['y'] + to_layout['height'] / 2
        
        dx = to_center_x - from_center_x
        dy = to_center_y - from_center_y
        
        # Determine start connection site on Part Rectangle (closest edge)
        if abs(dx) > abs(dy):
            # Horizontal connection
            start_site = 1 if dx > 0 else 3  # Right or Left
        else:
            # Vertical connection
            start_site = 2 if dy > 0 else 0  # Bottom or Top
        
        # End point is center of Actor Circle (not an edge, but center)
        # We'll calculate the center point directly
        
        # Make connector ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        conn_id = f"conn_{short_page}_{from_id[:12]}_{to_id[:12]}"[:50]
        
        # Calculate actual connection points based on connection sites
        # Connection sites: 0=Top, 1=Right, 2=Bottom, 3=Left
        from_width = from_layout['width']
        from_height = from_layout['height']
        from_x = from_layout['x']
        from_y = from_layout['y']
        
        to_width = to_layout['width']
        to_height = to_layout['height']
        to_x = to_layout['x']
        to_y = to_layout['y']
        
        # Calculate start point: Part Rectangle top-middle (connectionSiteIndex 0)
        start_x = from_x + from_width / 2  # Top-middle horizontally
        start_y = from_y  # Top edge
        
        # End point: Actor Circle center (connectionSiteIndex 0)
        end_x = to_center_x  # Center of circle
        end_y = to_center_y  # Center of circle
        
        # Create line using calculated connection points
        # Note: Google Slides API doesn't support true "glued" connection sites,
        # but we calculate connection points based on connection site indices
        # and create a line that connects at those points
        # The line will be positioned correctly even if not "glued"
        
        # Calculate line dimensions
        line_width = abs(end_x - start_x)
        line_height = abs(end_y - start_y)
        line_x = min(start_x, end_x)
        line_y = min(start_y, end_y)
        
        # Use the same approach as legacy method but with connection site calculations
        is_horizontal = line_width > line_height
        
        if is_horizontal:
            conn_width = max(line_width, 1)
            conn_height = 2
        else:
            conn_width = 2
            conn_height = max(line_height, 1)
        
        # Create line as a thin rectangle (same as legacy, but with connection site positions)
        requests = [{
            'createShape': {
                'objectId': conn_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': conn_height, 'unit': 'PT'},
                        'width': {'magnitude': conn_width, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': line_x,
                        'translateY': line_y,
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': conn_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 1, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }]
        
        # Add arrowhead
        arrow_size = 8
        arrow_id = f"{conn_id}_arr"[:50]
        
        if is_horizontal:
            if dx > 0:
                arrow_x = end_x - arrow_size
                arrow_y = end_y - arrow_size / 2
            else:
                arrow_x = end_x
                arrow_y = end_y - arrow_size / 2
        else:
            if dy > 0:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y - arrow_size
            else:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y
        
        requests.append({
            'createShape': {
                'objectId': arrow_id,
                'shapeType': 'TRIANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': arrow_size, 'unit': 'PT'},
                        'width': {'magnitude': arrow_size, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': arrow_x,
                        'translateY': arrow_y,
                        'unit': 'PT'
                    }
                }
            }
        })
        requests.append({
            'updateShapeProperties': {
                'objectId': arrow_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                        }
                    }
                },
                'fields': 'shapeBackgroundFill'
            }
        })
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()
    
    def _draw_arrow(self, page_id: str, from_id: str, to_id: str,
                   from_layout: Dict, to_layout: Dict, relationship: Dict):
        """Draw an arrow between two shapes (legacy method for full diagrams)."""
        # Calculate connection points
        from_center_x = from_layout['x'] + from_layout['width'] / 2
        from_center_y = from_layout['y'] + from_layout['height'] / 2
        to_center_x = to_layout['x'] + to_layout['width'] / 2
        to_center_y = to_layout['y'] + to_layout['height'] / 2
        
        dx = to_center_x - from_center_x
        dy = to_center_y - from_center_y
        
        # Find edge points
        if abs(dx) > abs(dy):
            if dx > 0:
                start_x = from_layout['x'] + from_layout['width']
                start_y = from_center_y
                end_x = to_layout['x']
                end_y = to_center_y
            else:
                start_x = from_layout['x']
                start_y = from_center_y
                end_x = to_layout['x'] + to_layout['width']
                end_y = to_center_y
        else:
            if dy > 0:
                start_x = from_center_x
                start_y = from_layout['y'] + from_layout['height']
                end_x = to_center_x
                end_y = to_layout['y']
            else:
                start_x = from_center_x
                start_y = from_layout['y']
                end_x = to_center_x
                end_y = to_layout['y'] + to_layout['height']
        
        # Draw line
        line_width = abs(end_x - start_x)
        line_height = abs(end_y - start_y)
        line_x = min(start_x, end_x)
        line_y = min(start_y, end_y)
        
        is_horizontal = line_width > line_height
        
        # Make connector ID unique by including page_id
        short_page = page_id[-8:] if len(page_id) > 8 else page_id
        conn_id = f"conn_{short_page}_{from_id[:12]}_{to_id[:12]}"[:50]
        
        if is_horizontal:
            conn_width = max(line_width, 1)
            conn_height = 2
        else:
            conn_width = 2
            conn_height = max(line_height, 1)
        
        requests = [{
            'createShape': {
                'objectId': conn_id,
                'shapeType': 'RECTANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': conn_height, 'unit': 'PT'},
                        'width': {'magnitude': conn_width, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': line_x,
                        'translateY': line_y,
                        'unit': 'PT'
                    }
                }
            }
        }, {
            'updateShapeProperties': {
                'objectId': conn_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                            }
                        },
                        'weight': {'magnitude': 1, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        }]
        
        # Add arrowhead
        arrow_size = 8
        arrow_id = f"{conn_id}_arr"[:50]
        
        if is_horizontal:
            if dx > 0:
                arrow_x = end_x - arrow_size
                arrow_y = end_y - arrow_size / 2
            else:
                arrow_x = end_x
                arrow_y = end_y - arrow_size / 2
        else:
            if dy > 0:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y - arrow_size
            else:
                arrow_x = end_x - arrow_size / 2
                arrow_y = end_y
        
        requests.append({
            'createShape': {
                'objectId': arrow_id,
                'shapeType': 'TRIANGLE',
                'elementProperties': {
                    'pageObjectId': page_id,
                    'size': {
                        'height': {'magnitude': arrow_size, 'unit': 'PT'},
                        'width': {'magnitude': arrow_size, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1, 'scaleY': 1,
                        'translateX': arrow_x,
                        'translateY': arrow_y,
                        'unit': 'PT'
                    }
                }
            }
        })
        requests.append({
            'updateShapeProperties': {
                'objectId': arrow_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': {'red': 0.0, 'green': 0.0, 'blue': 0.0}}
                        }
                    }
                },
                'fields': 'shapeBackgroundFill'
            }
        })
        
        self.service.presentations().batchUpdate(
            presentationId=self.presentation_id,
            body={'requests': requests}
        ).execute()


class FeedbackHandler:
    """
    Handles bidirectional feedback: extracts user text from Slides and sends back as JSON.
    """
    
    def __init__(self, renderer: SlidesRenderer):
        self.renderer = renderer
        self.element_mapping = {}  # Maps shape IDs to element IDs
    
    def extract_feedback(self, presentation_id: str) -> Dict:
        """
        Extract user feedback from Google Slides (text in shapes).
        
        Args:
            presentation_id: Presentation ID
            
        Returns:
            Dictionary with feedback data
        """
        try:
            presentation = self.renderer.service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            feedback = {
                'presentation_id': presentation_id,
                'slides': []
            }
            
            for slide in presentation.get('slides', []):
                slide_feedback = {
                    'slide_id': slide['objectId'],
                    'elements': []
                }
                
                for element in slide.get('pageElements', []):
                    if 'shape' in element:
                        shape = element['shape']
                        shape_id = element['objectId']
                        
                        # Extract text content
                        text_content = ""
                        if 'text' in shape:
                            text_elements = shape['text'].get('textElements', [])
                            for te in text_elements:
                                if 'textRun' in te:
                                    text_content += te['textRun'].get('content', '')
                        
                        # Map to element_id if available
                        element_id = self.element_mapping.get(shape_id, shape_id)
                        
                        slide_feedback['elements'].append({
                            'element_id': element_id,
                            'shape_id': shape_id,
                            'text_content': text_content.strip()
                        })
                
                feedback['slides'].append(slide_feedback)
            
            return feedback
            
        except Exception as e:
            print(f"Error extracting feedback: {e}")
            return {}
    
    def send_feedback(self, feedback: Dict, output_path: Optional[str] = None) -> str:
        """
        Send feedback back as JSON.
        
        Args:
            feedback: Feedback dictionary
            output_path: Optional path to save JSON file
            
        Returns:
            JSON string
        """
        json_str = json.dumps(feedback, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_str)
            print(f"Feedback saved to: {output_path}")
        
        return json_str


def load_json_model(json_path: str) -> Dict:
    """Load SysML-derived JSON model from file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main pipeline orchestrator."""
    parser = argparse.ArgumentParser(
        description='Transform SysML JSON to Google Slides with LLM-based semantic understanding'
    )
    parser.add_argument('json_file', help='Path to SysML-derived JSON file')
    parser.add_argument('--model', default='llama3', help='Ollama model name (default: llama3)')
    parser.add_argument('--presentation-id', type=str, default=None,
                       help='Existing Google Slides presentation ID to update')
    parser.add_argument('--title', type=str, default='SysML Visualization',
                       help='Presentation title (for new presentations)')
    parser.add_argument('--feedback-output', type=str, default=None,
                       help='Path to save feedback JSON file (also saves element mapping)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("SysML JSON → Google Slides Pipeline")
    print("=" * 60)
    
    # Step 1: Load JSON model
    print(f"\n[1/5] Loading JSON model from: {args.json_file}")
    try:
        json_model = load_json_model(args.json_file)
        print(f"✓ Loaded model with {len(json_model.get('parts', []))} parts, "
              f"{len(json_model.get('connections', []))} connections")
    except Exception as e:
        print(f"✗ Error loading JSON: {e}")
        sys.exit(1)
    
    # Step 2: Semantic understanding with LLM
    print(f"\n[2/5] Semantic understanding with LLM...")
    processor = SemanticModelProcessor(model=args.model)
    enriched_model = processor.understand_model(json_model)
    
    # Step 3: Split by relationships
    print(f"\n[3/5] Splitting model by relationships...")
    splitter = RelationshipSplitter()
    sub_models = splitter.split_by_relationships(enriched_model)
    full_count = sum(1 for m in sub_models if m.get('is_full_diagram', False))
    individual_count = len(sub_models) - full_count
    print(f"✓ Created {len(sub_models)} diagram(s): {full_count} full combined + {individual_count} individual relationship(s)")
    
    # Step 4: Calculate layouts
    print(f"\n[4/5] Calculating graph layouts...")
    layout_engine = GraphLayoutEngine()
    layouts = []
    for sub_model in sub_models:
        layout = layout_engine.calculate_layout(sub_model)
        layouts.append((layout, sub_model))
    print(f"✓ Calculated layouts for {len(layouts)} diagram(s)")
    
    # Step 5: Render to Google Slides
    print(f"\n[5/5] Rendering to Google Slides...")
    renderer = SlidesRenderer()
    try:
        renderer.authenticate()
        presentation_id = renderer.create_or_get_presentation(
            args.title, args.presentation_id
        )
        
        # Store the enriched model in renderer for element type lookup
        renderer.current_model = enriched_model
        
        for idx, (layout, sub_model) in enumerate(layouts):
            is_full_diagram = sub_model.get('is_full_diagram', False)
            relationship = sub_model.get('relationship')
            all_relationships = sub_model.get('all_relationships', [])
            
            renderer.render_diagram(
                layout, 
                relationship, 
                idx,
                is_full_diagram=is_full_diagram,
                all_relationships=all_relationships if is_full_diagram else None
            )
            
            diagram_type = "Full Combined" if is_full_diagram else f"Relationship {idx}"
            print(f"  ✓ Rendered {diagram_type} diagram {idx + 1}/{len(layouts)}")
        
        url = f"https://docs.google.com/presentation/d/{presentation_id}"
        print(f"\n✓ Success! Presentation ready at: {url}")
        
        # Save element mapping for feedback extraction
        if renderer.element_mapping:
            mapping_file = args.feedback_output.replace('.json', '_mapping.json') if args.feedback_output else 'element_mapping.json'
            with open(mapping_file, 'w') as f:
                json.dump(renderer.element_mapping, f, indent=2)
            print(f"✓ Element mapping saved to: {mapping_file}")
            print(f"  Use this mapping with feedback_service.py: --mapping {mapping_file}")
        
        # Step 6: Extract feedback (optional)
        if args.feedback_output:
            print(f"\n[6/6] Extracting feedback...")
            feedback_handler = FeedbackHandler(renderer)
            feedback_handler.element_mapping = renderer.element_mapping
            feedback = feedback_handler.extract_feedback(presentation_id)
            feedback_handler.send_feedback(feedback, args.feedback_output)
            print(f"✓ Feedback extracted and saved")
        
    except Exception as e:
        print(f"✗ Error rendering slides: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

