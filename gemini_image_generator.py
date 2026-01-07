"""
Gemini-powered Image Generator for SysML Relationships

This module uses Google Gemini API to generate visually appealing images
for individual relationships from the SysML JSON file.
"""

import json
import os
import re
import math
import base64
from typing import Dict, List, Optional
from pathlib import Path
try:
    from google import genai as new_genai
    from google.genai import types
    USE_NEW_GENAI = True
except ImportError:
    import google.generativeai as genai
    USE_NEW_GENAI = False
from PIL import Image, ImageDraw, ImageFont
import io

# Vertex AI imports for image generation
try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform.gapic.schema import predict
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    print("⚠️  Vertex AI not available. Install: pip install google-cloud-aiplatform")

class GeminiImageGenerator:
    """Generate images for SysML relationships using Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, vertex_ai_key: Optional[str] = None):
        """
        Initialize the Gemini image generator.
        
        Args:
            api_key: Google Gemini API key. If None, reads from GEMINI_API_KEY env var or uses default.
            vertex_ai_key: Vertex AI access token/key for image generation (ONLY for complete diagram).
        """
        # Default API key provided by user
        DEFAULT_API_KEY = "AIzaSyAvqHJIbaV01HbEKgRcV-Nb9AuLLOflezU"
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or DEFAULT_API_KEY
        
        if USE_NEW_GENAI:
            try:
                self.client = new_genai.Client(api_key=self.api_key)
                # Use the correct model name that exists
                self.model = "gemini-2.0-flash-exp-image-generation"
                print(f"✓ Using new google.genai package for image generation")
            except Exception as e:
                print(f"⚠️  Could not initialize new genai client: {e}")
                self.client = None
                self.model = None
        else:
            genai.configure(api_key=self.api_key)
            # Try available models (gemini-2.0-flash, gemini-2.5-flash, etc.)
            model_names = ['models/gemini-2.0-flash', 'models/gemini-2.5-flash', 'models/gemini-2.0-flash-exp']
            self.model = None
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    break
                except:
                    continue
        
        self.output_dir = Path('generated_images')
        self.output_dir.mkdir(exist_ok=True)
        self.original_sysml_file = None  # Store original SysML file path
        
        # Vertex AI configuration for complete diagram ONLY (ONE API CALL)
        # User provided Vertex AI key
        DEFAULT_VERTEX_AI_KEY = "AQ.Ab8RN6JeCVCM0eF4ueL0EVe_P-XWVyrpyNMX_xeY1HMJcnVcxw"
        self.vertex_ai_key = vertex_ai_key or os.getenv('VERTEX_AI_KEY') or DEFAULT_VERTEX_AI_KEY
        self.vertex_ai_project = os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('GCP_PROJECT')
        self.vertex_ai_location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        
        # Use Vertex AI if key is available (for complete diagram only)
        self.use_vertex_ai = bool(self.vertex_ai_key)
        
        # Color scheme for different element types
        self.colors = {
            'PART': {'bg': '#E8F5E9', 'border': '#4CAF50', 'text': '#1B5E20'},
            'ACTOR': {'bg': '#FFF9C4', 'border': '#F57C00', 'text': '#E65100'},
            'USE_CASE': {'bg': '#E3F2FD', 'border': '#2196F3', 'text': '#0D47A1'},
            'SUBJECT': {'bg': '#F3E5F5', 'border': '#9C27B0', 'text': '#4A148C'},
            'SYSTEM': {'bg': '#FAFAFA', 'border': '#424242', 'text': '#212121'},
        }
    
    def load_json(self, json_path: str) -> Dict:
        """Load and parse the JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_relationships(self, data: Dict) -> List[Dict]:
        """
        Extract ALL relationships from the JSON structure (not just ASSOCIATION).
        Includes: part_to_actor, part_to_part, part_to_subject, actor_to_use_case, subject_to_use_case
        
        Returns a list of relationship dictionaries with:
        - relationship_id: unique identifier
        - from_element: source element name and type
        - to_element: target element name and type
        - connection_type: type of connection
        - relationship_category: category (part_to_actor, actor_to_use_case, etc.)
        """
        relationships = []
        
        # Get element mapping
        element_map = {}
        for elem in data.get('elements', []):
            element_map[elem.get('shape_id', '')] = {
                'name': elem.get('text_content', ''),
                'type': elem.get('element_type', ''),
                'shape_type': elem.get('shape_type', '')
            }
        
        # Extract from connections_summary - ALL RELATIONSHIP TYPES
        connections_summary = data.get('connections_summary', {})
        rel_id = 0
        
        # part_to_actor relationships
        for rel in connections_summary.get('part_to_actor', []):
            parts = rel.split(' → ')
            if len(parts) == 2:
                relationships.append({
                    'relationship_id': f'rel_{rel_id}',
                    'from_element': {'name': parts[0], 'type': 'PART'},
                    'to_element': {'name': parts[1], 'type': 'ACTOR'},
                    'connection_type': 'ASSOCIATION',
                    'relationship_category': 'part_to_actor',
                    'description': rel
                })
                rel_id += 1
        
        # part_to_subject relationships
        for rel in connections_summary.get('part_to_subject', []):
            parts = rel.split(' → ')
            if len(parts) == 2:
                relationships.append({
                    'relationship_id': f'rel_{rel_id}',
                    'from_element': {'name': parts[0], 'type': 'PART'},
                    'to_element': {'name': parts[1], 'type': 'SUBJECT'},
                    'connection_type': 'ASSOCIATION',
                    'relationship_category': 'part_to_subject',
                    'description': rel
                })
                rel_id += 1
        
        # part_to_part relationships
        for rel in connections_summary.get('part_to_part', []):
            parts = rel.split(' → ')
            if len(parts) == 2:
                relationships.append({
                    'relationship_id': f'rel_{rel_id}',
                    'from_element': {'name': parts[0], 'type': 'PART'},
                    'to_element': {'name': parts[1], 'type': 'PART'},
                    'connection_type': 'ASSOCIATION',
                    'relationship_category': 'part_to_part',
                    'description': rel
                })
                rel_id += 1
        
        # actor_to_use_case relationships (ADDED - was previously skipped)
        for rel in connections_summary.get('actor_to_use_case', []):
            parts = rel.split(' → ')
            if len(parts) == 2:
                relationships.append({
                    'relationship_id': f'rel_{rel_id}',
                    'from_element': {'name': parts[0], 'type': 'ACTOR'},
                    'to_element': {'name': parts[1], 'type': 'USE_CASE'},
                    'connection_type': 'PARTICIPATES',
                    'relationship_category': 'actor_to_use_case',
                    'description': rel
                })
                rel_id += 1
        
        # subject_to_use_case relationships (ADDED - was previously skipped)
        for rel in connections_summary.get('subject_to_use_case', []):
            parts = rel.split(' → ')
            if len(parts) == 2:
                relationships.append({
                    'relationship_id': f'rel_{rel_id}',
                    'from_element': {'name': parts[0], 'type': 'SUBJECT'},
                    'to_element': {'name': parts[1], 'type': 'USE_CASE'},
                    'connection_type': 'SUBJECT_OF',
                    'relationship_category': 'subject_to_use_case',
                    'description': rel
                })
                rel_id += 1
        
        # Extract from direct connections in elements - ALL CONNECTION TYPES (not just ASSOCIATION)
        for elem in data.get('elements', []):
            conn_type = elem.get('connection_type', '')
            # Process ALL connection types (ASSOCIATION, PARTICIPATES, SUBJECT_OF, etc.)
            if conn_type:  # Changed from: if conn_type == 'ASSOCIATION'
                from_shape = elem.get('from', '')
                to_shape = elem.get('to', '')
                
                from_elem = element_map.get(from_shape, {})
                to_elem = element_map.get(to_shape, {})
                
                if from_elem and to_elem:
                    # Check if already added from connections_summary
                    already_added = False
                    rel_desc = f"{from_elem.get('name', '')} → {to_elem.get('name', '')}"
                    for existing_rel in relationships:
                        if existing_rel.get('description') == rel_desc:
                            already_added = True
                            break
                    
                    if not already_added:
                        # Determine connection type based on element types if not specified
                        if not conn_type or conn_type == 'ASSOCIATION':
                            # Auto-determine connection type based on element types
                            from_type = from_elem.get('type', '')
                            to_type = to_elem.get('type', '')
                            if from_type == 'ACTOR' and to_type == 'USE_CASE':
                                conn_type = 'PARTICIPATES'
                            elif from_type == 'SUBJECT' and to_type == 'USE_CASE':
                                conn_type = 'SUBJECT_OF'
                            else:
                                conn_type = 'ASSOCIATION'
                        
                        relationships.append({
                            'relationship_id': f'rel_{rel_id}',
                            'from_element': {
                                'name': from_elem.get('name', ''),
                                'type': from_elem.get('type', '')
                            },
                            'to_element': {
                                'name': to_elem.get('name', ''),
                                'type': to_elem.get('type', '')
                            },
                            'connection_type': conn_type,
                            'relationship_category': self._categorize_relationship(
                                from_elem.get('type', ''),
                                to_elem.get('type', '')
                            ),
                            'description': rel_desc,
                            'line_style': elem.get('line_style', 'SOLID')
                        })
                        rel_id += 1
        
        return relationships
        
    
    def _categorize_relationship(self, from_type: str, to_type: str) -> str:
        """Categorize relationship based on element types."""
        if from_type == 'PART' and to_type == 'ACTOR':
            return 'part_to_actor'
        elif from_type == 'PART' and to_type == 'SUBJECT':
            return 'part_to_subject'
        elif from_type == 'PART' and to_type == 'PART':
            return 'part_to_part'
        elif from_type == 'ACTOR' and to_type == 'USE_CASE':
            return 'actor_to_use_case'
        elif from_type == 'SUBJECT' and to_type == 'USE_CASE':
            return 'subject_to_use_case'
        else:
            return 'other'
    
    def generate_prompt(self, relationship: Dict) -> str:
        """
        Use Gemini to generate a detailed prompt for image generation.
        """
        from_name = relationship['from_element']['name']
        from_type = relationship['from_element']['type']
        to_name = relationship['to_element']['name']
        to_type = relationship['to_element']['type']
        conn_type = relationship['connection_type']
        
        prompt = f"""Generate a detailed visual description for a professional SysML diagram showing this relationship:
- Source: {from_name} ({from_type})
- Target: {to_name} ({to_type})
- Connection Type: {conn_type}

Provide a concise description (2-3 sentences) of how to visually represent this relationship in a diagram, including:
1. Layout arrangement (positions of elements)
2. Visual styling (colors, shapes, borders)
3. Connection arrow style
4. Background and overall aesthetic

Keep it professional and technical, suitable for system architecture documentation."""
        
        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return response.text
            else:
                return self._default_prompt(relationship)
        except Exception as e:
            # Fallback to default description (silent fallback)
            return self._default_prompt(relationship)
    
    def _default_prompt(self, relationship: Dict) -> str:
        """Generate a default prompt if Gemini fails."""
        return f"Professional SysML diagram showing {relationship['description']} with clear labels and arrow connection."
    
    def generate_individual_relationship_image_via_gemini(self, relationship: Dict, full_data: Dict, width: int = 1920, height: int = 1080) -> str:
        """
        Generate image for an individual relationship using Gemini API ONLY (no fallback).
        Uses the EXACT SAME model and method as complete diagram generation:
        - Model: gemini-2.5-flash-image (primary), gemini-2.5-flash-image-preview, gemini-2.0-flash-exp-image-generation
        - Method: _generate_image_via_vertex_ai() - same API call as complete diagram
        - API: client.models.generate_content() with GenerateContentConfig
        """
        from_name = relationship['from_element']['name']
        from_type = relationship['from_element']['type']
        to_name = relationship['to_element']['name']
        to_type = relationship['to_element']['type']
        system_title = full_data.get('slide_title', 'System')
        
        # Build prompt for individual relationship
        prompt = f"""Generate a high-quality, professional SysML (Systems Modeling Language) relationship diagram image.

SYSTEM CONTEXT:
- System Name: {system_title}
- System Boundary: Large black rectangle with title "{system_title}" at the top

FOCUS RELATIONSHIP:
- Source: {from_name} ({from_type})
- Target: {to_name} ({to_type})
- Connection: Association (solid black arrow from source to target)

VISUAL REQUIREMENTS:
1. System Boundary: Large black rectangle with title "{system_title}" at the top
2. Source Element ({from_name}): Rectangle with light green background (#E8F5E9), green border (#4CAF50), 4px width, placed inside boundary
3. Target Element ({to_name}): Rectangle with light green background (#E8F5E9), green border (#4CAF50), 4px width, placed inside boundary
4. Association Arrow: Solid black arrow (3px width) from {from_name} to {to_name}
5. Layout: Professional arrangement showing the relationship clearly
6. Text: Element names clearly visible
7. Style: Clean, technical diagram highlighting this specific relationship
8. Colors: Light green (#E8F5E9) for parts, black for boundaries and arrows
9. Size: High resolution, 1920x1080 aspect ratio

Generate a professional SysML diagram focusing on the relationship: {from_name} → {to_name}"""

        # Use Vertex AI Gemini API (same as complete diagram)
        safe_name = re.sub(r'[^\w\s-]', '', relationship['description']).replace(' ', '_')
        output_filename = f"{safe_name}_{relationship['relationship_id']}_gemini.png"
        
        print(f"  Using Gemini API (Vertex AI) for individual relationship image...")
        print(f"  Using SAME model as complete diagram: gemini-2.5-flash-image (with fallbacks)")
        print(f"  Output filename: {output_filename}")
        
        # Generate image using Vertex AI - EXACT SAME method as complete diagram
        # This ensures consistency: same model, same API, same behavior
        image_path = self._generate_image_via_vertex_ai(prompt, width, height, output_filename)
        
        if image_path and Path(image_path).exists():
            return str(image_path)
        else:
            raise Exception(f"Gemini API failed to generate image for relationship: {relationship['description']}")
    
    def generate_image(self, relationship: Dict, width: int = 1920, height: int = 1080) -> str:
        """
        Generate a UNIQUE image for a relationship using PIL/drawing libraries.
        Uses Gemini's description to guide the visual design and ensures each image is different.
        """
        # Get Gemini's visual description for unique styling guidance
        visual_description = self.generate_prompt(relationship)
        
        # Create unique layout variation based on relationship ID
        rel_id_hash = hash(relationship['relationship_id']) % 4
        
        # Create image with light thematic background (very light purple/cyan)
        # Start with a very light purple-cyan base color
        base_color = (245, 240, 250)  # Very light purple-cyan
        img = Image.new('RGB', (width, height), color=base_color)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        try:
            font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 40)
            font_medium = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 32)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Get element info
        from_name = relationship['from_element']['name']
        from_type = relationship['from_element']['type']
        to_name = relationship['to_element']['name']
        to_type = relationship['to_element']['type']
        conn_type = relationship['connection_type']
        
        # Draw unique gradient background based on relationship
        self._draw_unique_gradient_background(img, draw, width, height, rel_id_hash)
        
        # Create unique layout variations for different relationships
        layouts = [
            {'from_x': 200, 'to_x': width - 500, 'center_y': height // 2, 'angle': 0},      # Horizontal
            {'from_x': width // 4, 'to_x': 3 * width // 4, 'center_y': height // 2, 'angle': 0},  # Centered
            {'from_x': 250, 'to_x': width - 450, 'center_y': height // 2 + 50, 'angle': 0}, # Slight offset
            {'from_x': 150, 'to_x': width - 550, 'center_y': height // 2 - 50, 'angle': 0}, # Upper
        ]
        layout = layouts[rel_id_hash]
        
        from_x = layout['from_x']
        to_x = layout['to_x']
        center_y = layout['center_y']
        
        # Get colors with unique variations per relationship
        from_colors = self._get_unique_colors(from_type, rel_id_hash)
        to_colors = self._get_unique_colors(to_type, rel_id_hash + 1)
        
        # Draw source element with unique styling
        self._draw_element(draw, from_name, from_x, center_y, from_type, from_colors, font_medium)
        
        # Draw target element
        self._draw_element(draw, to_name, to_x, center_y, to_type, to_colors, font_medium)
        
        # Draw connection arrow with unique styling
        arrow_start_x = from_x + 300
        arrow_end_x = to_x
        line_style = relationship.get('line_style', 'SOLID')
        arrow_color = from_colors['border']
        # Vary arrow thickness for uniqueness
        arrow_width = 4 + (rel_id_hash % 3)
        self._draw_arrow(draw, arrow_start_x, center_y, arrow_end_x, center_y, 
                        line_style == 'DASHED', arrow_color, arrow_width)
        
        # Draw title
        title = relationship.get('description', f"{from_name} → {to_name}")
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 50), title, fill='#2C3E50', font=font_large)
        
        # Draw connection type label
        conn_label = f"Connection: {conn_type}"
        conn_bbox = draw.textbbox((0, 0), conn_label, font=font_small)
        conn_width = conn_bbox[2] - conn_bbox[0]
        conn_x = (width - conn_width) // 2
        draw.text((conn_x, height - 100), conn_label, fill='#7F8C8D', font=font_small)
        
        # Add visual description as watermark (subtle)
        # (Could be used for reference)
        
        # Save image
        safe_name = re.sub(r'[^\w\s-]', '', relationship['description']).replace(' ', '_')
        filename = f"{safe_name}_{relationship['relationship_id']}.png"
        filepath = self.output_dir / filename
        
        img.save(filepath, 'PNG', quality=95)
        return str(filepath)
    
    def _draw_gradient_background(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int):
        """Draw a subtle gradient background."""
        for y in range(height):
            ratio = y / height
            r = int(255 - (ratio * 10))
            g = int(255 - (ratio * 10))
            b = int(255 - (ratio * 5))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _draw_unique_gradient_background(self, img: Image.Image, draw: ImageDraw.Draw, width: int, height: int, variation: int):
        """Draw a unique light thematic gradient background for each relationship (cyberpunk theme)."""
        gradients = [
            # Very light purple to light cyan gradient (cyberpunk theme)
            lambda y, h: (int(245 + (y/h) * 5), int(240 + (y/h) * 10), int(250 + (y/h) * 5)),  # Light purple to very light purple
            # Very light pink to light cyan gradient
            lambda y, h: (int(250 + (y/h) * 5), int(240 + (y/h) * 10), int(245 + (y/h) * 10)),  # Light pink to light cyan
            # Very light indigo to light purple gradient
            lambda y, h: (int(240 + (y/h) * 10), int(235 + (y/h) * 15), int(250 + (y/h) * 5)),  # Light indigo to light purple
            # Very light cyan to light purple gradient
            lambda y, h: (int(235 + (y/h) * 15), int(245 + (y/h) * 8), int(250 + (y/h) * 5)),  # Light cyan to light purple
        ]
        gradient_func = gradients[variation % len(gradients)]
        
        for y in range(height):
            r, g, b = gradient_func(y, height)
            # Ensure colors stay in valid range and are very light
            r = min(255, max(235, r))
            g = min(255, max(235, g))
            b = min(255, max(245, b))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _get_unique_colors(self, elem_type: str, variation: int) -> Dict:
        """Get unique color variations for elements based on type and variation."""
        base_colors = self.colors.get(elem_type, self.colors['PART'])
        
        # Create variations by slightly adjusting hue
        variations = [
            lambda c: c,  # Original
            lambda c: self._shift_color_brightness(c, 0.05),  # Slightly brighter
            lambda c: self._shift_color_brightness(c, -0.05),  # Slightly darker
            lambda c: self._shift_color_saturation(c, 0.1),    # More saturated
        ]
        
        var_func = variations[variation % len(variations)]
        
        return {
            'bg': var_func(base_colors['bg']),
            'border': var_func(base_colors['border']),
            'text': base_colors['text']  # Keep text readable
        }
    
    def _shift_color_brightness(self, hex_color: str, factor: float) -> str:
        """Shift color brightness by factor (-1 to 1)."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        r = max(0, min(255, int(r * (1 + factor))))
        g = max(0, min(255, int(g * (1 + factor))))
        b = max(0, min(255, int(b * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _shift_color_saturation(self, hex_color: str, factor: float) -> str:
        """Shift color saturation by factor."""
        hex_color = hex_color.lstrip('#')
        r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        # Simple saturation shift
        gray = (r + g + b) / 3
        r = max(0, min(255, int(gray + (r - gray) * (1 + factor))))
        g = max(0, min(255, int(gray + (g - gray) * (1 + factor))))
        b = max(0, min(255, int(gray + (b - gray) * (1 + factor))))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _draw_element(self, draw: ImageDraw.Draw, name: str, x: int, y: int, 
                     elem_type: str, colors: Dict, font):
        """Draw a SysML element (rectangle, circle, or ellipse) with no shading, prominent boundaries."""
        width = 280
        height = 120
        
        # Use white fill to remove shading, prominent border
        fill_color = '#FFFFFF'  # White fill - no shading
        border_color = colors['border']
        border_width = 6  # Prominent boundary
        
        # Adjust for different shapes
        if elem_type == 'ACTOR':
            # Circle
            bbox = [x, y - height//2, x + width, y + height//2]
            draw.ellipse(bbox, fill=fill_color, outline=border_color, width=border_width)
        elif elem_type == 'USE_CASE':
            # Ellipse (oval)
            bbox = [x, y - height//2, x + width, y + height//2]
            draw.ellipse(bbox, fill=fill_color, outline=border_color, width=border_width)
        elif elem_type == 'SUBJECT':
            # Rounded rectangle
            bbox = [x, y - height//2, x + width, y + height//2]
            draw.rounded_rectangle(bbox, radius=15, fill=fill_color, outline=border_color, width=border_width)
        else:
            # Rectangle (PART, SYSTEM)
            bbox = [x, y - height//2, x + width, y + height//2]
            draw.rectangle(bbox, fill=fill_color, outline=border_color, width=border_width)
        
        # Draw text (centered)
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x + (width - text_width) // 2
        text_y = y - text_height // 2
        
        # Word wrap if needed
        words = name.split()
        if len(words) > 1 and text_width > width - 20:
            # Multi-line text
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                if test_bbox[2] - test_bbox[0] <= width - 40:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            line_height = text_height + 5
            start_y = y - (len(lines) * line_height) // 2
            for i, line in enumerate(lines):
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = x + (width - line_width) // 2
                draw.text((line_x, start_y + i * line_height), line, 
                         fill=colors['text'], font=font)
        else:
            draw.text((text_x, text_y), name, fill=colors['text'], font=font)
    
    def _lighten_color(self, hex_color: str, factor: float = 0.4) -> str:
        """Lighten a hex color for shine highlights."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _draw_arrow(self, draw: ImageDraw.Draw, x1: int, y1: int, x2: int, y2: int, 
                   dashed: bool = False, color: str = '#000000', width: int = 4, orthogonal: bool = False):
        """Draw an arrow from (x1, y1) to (x2, y2) with specified width.
        If orthogonal=True, draws 90-degree (right-angle) arrow."""
        arrow_size = 20
        
        # Use orthogonal (90-degree) arrow if requested
        if orthogonal:
            # Draw 90-degree corner: horizontal then vertical
            # Horizontal segment goes from x1 to target x position (x2)
            # Vertical segment goes from y1 to target y position (y2)
            mid_x = x2  # Vertical segment starts at target x position
            draw.line([(x1, y1), (mid_x, y1)], fill=color, width=width)  # Horizontal segment
            draw.line([(mid_x, y1), (mid_x, y2)], fill=color, width=width)  # Vertical segment
            # Draw arrowhead at end (pointing in direction of final segment)
            # Calculate angle based on vertical direction
            if y2 > y1:
                angle = math.pi / 2  # Downward (pointing down)
            elif y2 < y1:
                angle = -math.pi / 2  # Upward (pointing up)
            else:
                angle = 0  # Horizontal (shouldn't happen in orthogonal)
            
            # Arrowhead points exactly at (x2, y2)
            arrow_x1 = x2 - arrow_size * math.cos(angle - math.pi / 6)
            arrow_y1 = y2 - arrow_size * math.sin(angle - math.pi / 6)
            arrow_x2 = x2 - arrow_size * math.cos(angle + math.pi / 6)
            arrow_y2 = y2 - arrow_size * math.sin(angle + math.pi / 6)
            draw.polygon([(x2, y2), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)], 
                        fill=color, outline=color)
            return
        
        # Draw line
        if dashed:
            # Draw dashed line
            dash_length = 15
            gap_length = 10
            dx = x2 - x1
            dy = y2 - y1
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                unit_x = dx / distance
                unit_y = dy / distance
                
                current_x, current_y = x1, y1
                while True:
                    next_x = current_x + unit_x * dash_length
                    next_y = current_y + unit_y * dash_length
                    if math.sqrt((next_x - x1)**2 + (next_y - y1)**2) >= distance:
                        next_x, next_y = x2, y2
                    
                    draw.line([(current_x, current_y), (next_x, next_y)], 
                             fill=color, width=width)
                    
                    if next_x == x2 and next_y == y2:
                        break
                    
                    current_x = next_x + unit_x * gap_length
                    current_y = next_y + unit_y * gap_length
                    
                    if math.sqrt((current_x - x1)**2 + (current_y - y1)**2) >= distance:
                        break
        else:
            draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
        
        # Draw arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_x1 = x2 - arrow_size * math.cos(angle - math.pi / 6)
        arrow_y1 = y2 - arrow_size * math.sin(angle - math.pi / 6)
        arrow_x2 = x2 - arrow_size * math.cos(angle + math.pi / 6)
        arrow_y2 = y2 - arrow_size * math.sin(angle + math.pi / 6)
        
        draw.polygon([(x2, y2), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)], 
                    fill=color, outline=color)
    
    def generate_all_images(self, json_path: str) -> List[Dict]:
        """
        Generate images for all relationships in the JSON file.
        Uses enhanced generation with full system context.
        
        Returns list of relationship dictionaries with 'image_path' added.
        """
        data = self.load_json(json_path)
        relationships = self.extract_relationships(data)
        
        results = []
        import time
        import re
        
        # Smart rate limiting: Add delay between API calls to avoid quota issues
        # Free tier typically allows: 15 requests/minute, 1500 requests/day
        # We'll space out calls: 5 seconds between calls = 12 calls/minute (safe margin)
        API_CALL_DELAY = 5  # seconds between API calls
        
        for i, rel in enumerate(relationships):
            print(f"Generating image {i+1}/{len(relationships)}: {rel['description']}")
            
            # Add delay between API calls to respect rate limits (except for first call)
            if i > 0:
                print(f"  ⏳ Waiting {API_CALL_DELAY}s to respect rate limits...")
                time.sleep(API_CALL_DELAY)
            
            # Use Gemini API with smart retry logic
            max_retries = 3
            image_path = None
            
            for retry in range(max_retries):
                try:
                    image_path = self.generate_individual_relationship_image_via_gemini(rel, data)
                    rel['image_path'] = image_path
                    rel['image_filename'] = os.path.basename(image_path)
                    results.append(rel)
                    print(f"  ✓ Saved (Gemini API) to: {image_path}")
                    break  # Success, exit retry loop
                    
                except Exception as gemini_error:
                    error_str = str(gemini_error)
                    
                    # Check if it's a quota/rate limit error
                    if '429' in error_str or 'quota' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                        # Extract wait time from error message
                        wait_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                        
                        if wait_match and retry < max_retries - 1:
                            wait_seconds = float(wait_match.group(1))
                            wait_seconds = max(wait_seconds, 10)  # Minimum 10 seconds
                            print(f"  ⚠️  Quota exceeded. Waiting {wait_seconds:.0f}s before retry {retry+1}/{max_retries}...")
                            time.sleep(wait_seconds)
                            continue
                        elif retry < max_retries - 1:
                            # No wait time specified, use smart backoff
                            wait_seconds = 60 * (retry + 1)  # 60s, 120s
                            print(f"  ⚠️  Quota exceeded. Waiting {wait_seconds}s before retry {retry+1}/{max_retries}...")
                            time.sleep(wait_seconds)
                            continue
                        else:
                            # Max retries reached
                            raise Exception(f"Gemini API quota exhausted after {max_retries} retries: {gemini_error}")
                    else:
                        # Other error (not quota), raise immediately
                        raise Exception(f"Gemini API error: {gemini_error}")
            
            # If we get here without breaking, generation failed
            if not image_path:
                raise Exception(f"Failed to generate image after {max_retries} retries")
        
        # Generate complete diagram from JSON using Gemini (ONE API CALL ONLY - NO FALLBACK)
        print(f"\nGenerating complete SysML diagram with all associations using Gemini (1 API call - NO FALLBACK)...")
        complete_path = None
        try:
            # Try multiple ways to find SysML file
            json_path_obj = Path(json_path)
            sysml_file = None
            
            # Method 1: Same name as JSON file
            potential_sysml = json_path_obj.with_suffix('.sysml')
            if potential_sysml.exists():
                sysml_file = str(potential_sysml)
            
            # Method 2: Look for OpsCon.sysml in same directory
            if not sysml_file:
                parent_dir = json_path_obj.parent
                opscon_sysml = parent_dir / 'OpsCon.sysml'
                if opscon_sysml.exists():
                    sysml_file = str(opscon_sysml)
            
            # Method 3: Use stored original SysML file path
            if not sysml_file and hasattr(self, 'original_sysml_file') and self.original_sysml_file:
                original_path = Path(self.original_sysml_file)
                if original_path.exists():
                    sysml_file = str(original_path)
            
            # Method 4: Look in current directory
            if not sysml_file:
                current_dir_sysml = Path('OpsCon.sysml')
                if current_dir_sysml.exists():
                    sysml_file = str(current_dir_sysml)
            
            if not sysml_file:
                raise Exception("SysML file not found. Cannot generate complete diagram without SysML file.")
            
            if not self.model:
                raise Exception("Gemini model not available. Cannot generate complete diagram.")
            
            print(f"  Found SysML file: {sysml_file}")
            print(f"  Making ONE Gemini API call to generate complete diagram (NO FALLBACK)...")
            complete_path = self.generate_complete_diagram_from_sysml(sysml_file)
            
            if not complete_path:
                raise Exception("Gemini API failed to generate complete diagram. No fallback available.")
            
            print(f"  ✓ Complete diagram saved to: {complete_path}")
            
            # Add complete diagram to results for metadata
            complete_diagram_rel = {
                'relationship_id': 'complete_diagram',
                'description': 'Complete SysML Diagram',
                'image_path': str(complete_path),
                'image_filename': os.path.basename(complete_path),
                'connection_type': 'COMPLETE',
                'relationship_category': 'complete'
            }
            results.append(complete_diagram_rel)
        except Exception as e:
            print(f"  ✗ Error generating complete diagram: {e}")
            import traceback
            traceback.print_exc()
            # NO FALLBACK - raise error instead
            raise Exception(f"Gemini API failed to generate complete diagram: {e}. No fallback available.")
        
        # Save metadata
        self.save_metadata(results, 'relationship_images_metadata.json')
        print(f"\n✓ Generated {len([r for r in results if r.get('image_path')])} images")
        return results
    
    def generate_complete_diagram_from_sysml(self, sysml_file_path: str, width: int = 1920, height: int = 1080) -> str:
        """
        Generate a complete SysML diagram using Gemini's Imagen API (actual image generation).
        Uses Gemini 2.5 Flash Image model - ONE API call that returns the actual image file.
        """
        # Read SysML file
        with open(sysml_file_path, 'r', encoding='utf-8') as f:
            sysml_content = f.read()
        
        # Create detailed prompt for image generation
        prompt = f"""Create a professional SysML (Systems Modeling Language) system diagram image.

SysML Code:
```
{sysml_content}
```

Generate a complete visual diagram showing:
- System boundary: Large black rectangle with system name "OpsCon_UAV_basedAircraftInspection" at the top
- Parts (rectangles, light green): Human, Environment, Drone, Aircraft
- Actors (circles, light yellow): DroneOperator, CandidateAircraft, InspectionEnvironment  
- Use Case (ellipse, light blue): InspectAircraftAutomatically
- Subject (rounded rectangle, light purple): SoI
- All connections: Arrows showing relationships between elements

Style: Clean, professional technical diagram with clear labels, proper spacing, no overlapping elements.
Colors: Light green for parts, light yellow for actors, light blue for use cases, light purple for subjects.
All text should be clearly readable."""

        try:
            if not self.model:
                raise Exception("Gemini model not initialized. Please check your API key.")
            
            print("  Using Gemini Imagen API to generate ACTUAL IMAGE (ONE API call)...")
            print("  Model: Imagen 3.0 (500 free images/day)")
            
            # Use Imagen API directly via REST - this is the correct way to generate images
            # Use Vertex AI Gemini API (NO FALLBACK)
            return self._generate_image_via_vertex_ai(prompt, width, height, "complete_sysml_diagram_gemini.png")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            # NO FALLBACK - raise error instead
            raise Exception(f"Gemini API failed to generate complete diagram from SysML: {e}. No fallback available.")
    
    def _generate_image_via_imagen_api(self, prompt: str, width: int = 1920, height: int = 1080) -> str:
        """
        Generate image using Vertex AI Gemini 2.5 Flash Image model.
        Uses gemini-2.5-flash-image (500 free images/day).
        ONE API CALL ONLY for complete diagram.
        """
        # Use Vertex AI with provided key (ONLY for complete diagram - ONE API CALL)
        if self.use_vertex_ai:
            print("  Using Vertex AI key for image generation (ONE API call)...")
            return self._generate_image_via_vertex_ai(prompt, width, height)
        
        # Fallback to REST API
        import requests
        
        try:
            # CORRECT Imagen API endpoint (as of 2024)
            # Note: Imagen might require Vertex AI setup or different authentication
            # Try the correct Gemini API endpoint for Imagen
            url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            params = {
                "key": self.api_key
            }
            
            # Calculate aspect ratio
            if width/height > 1.5:
                aspect_ratio = "16:9"
            elif width/height < 0.7:
                aspect_ratio = "9:16"
            else:
                aspect_ratio = "1:1"
            
            # Correct payload format for Imagen API
            payload = {
                "prompt": prompt,
                "numberOfImages": 1,
                "aspectRatio": aspect_ratio,
                "safetyFilterLevel": "block_some",
                "personGeneration": "allow_all"
            }
            
            print("  Calling Gemini Imagen API (500 free images/day)...")
            print(f"  Endpoint: {url}")
            print(f"  Prompt length: {len(prompt)} characters")
            
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=120)
            
            print(f"  Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Response keys: {list(result.keys())}")
                
                # Extract image data from response
                if 'generatedImages' in result and len(result['generatedImages']) > 0:
                    image_data = result['generatedImages'][0]
                    # Image data might be in different formats
                    if 'imageBytes' in image_data:
                        image_b64 = image_data['imageBytes']
                    elif 'base64EncodedImage' in image_data:
                        image_b64 = image_data['base64EncodedImage']
                    elif 'bytesBase64Encoded' in image_data:
                        image_b64 = image_data['bytesBase64Encoded']
                    else:
                        # Try to get image URL or data
                        image_b64 = image_data.get('image') or image_data.get('data')
                    
                    if image_b64:
                        image_bytes = base64.b64decode(image_b64)
                        filename = "complete_sysml_diagram_gemini.png"
                        filepath = self.output_dir / filename
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        print(f"  ✓ Saved Gemini Imagen-generated image to: {filepath}")
                        return str(filepath)
                elif 'images' in result:
                    # Alternative response format
                    image_b64 = result['images'][0].get('base64') or result['images'][0].get('data') or result['images'][0].get('bytesBase64Encoded')
                    if image_b64:
                        image_bytes = base64.b64decode(image_b64)
                        filename = "complete_sysml_diagram_gemini.png"
                        filepath = self.output_dir / filename
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        print(f"  ✓ Saved Gemini Imagen-generated image to: {filepath}")
                        return str(filepath)
            
            # If 404, the endpoint or model might not be available
            if response.status_code == 404:
                error_msg = response.json().get('error', {}).get('message', 'Model not found')
                print(f"  ⚠️  404 Error: {error_msg}")
                print(f"  ⚠️  Possible reasons:")
                print(f"     1. Imagen model not available in your region")
                print(f"     2. API key doesn't have Imagen access")
                print(f"     3. Model name/endpoint changed")
                print(f"  💡 Solution: Imagen might require Vertex AI setup or different authentication")
                raise Exception(f"Imagen API 404: {error_msg}. Imagen may require Vertex AI or different setup.")
            
            # Other errors
            error_text = response.text[:500] if response.text else "Unknown error"
            print(f"  Error response: {error_text}")
            raise Exception(f"Imagen API returned status {response.status_code}: {error_text}")
            
        except requests.exceptions.RequestException as e:
            print(f"  Network error: {e}")
            raise Exception(f"Network error calling Imagen API: {e}")
        except Exception as e:
            print(f"  Imagen API call failed: {e}")
            raise Exception(f"Could not generate image via Imagen API: {e}")
    
    def _generate_image_via_vertex_ai(self, prompt: str, width: int = 1920, height: int = 1080, output_filename: str = None) -> str:
        """
        Generate image using Vertex AI endpoint with Vertex AI key.
        Uses: https://aiplatform.googleapis.com/v1/publishers/google/models/
        API Key: AQ.Ab8RN6JeCVCM0eF4ueL0EVe_P-XWVyrpyNMX_xeY1HMJcnVcxw
        
        This is the PRIMARY method used for BOTH complete diagram AND individual relationships.
        """
        import time
        import re
        import requests
        import base64
        import json
        
        if output_filename:
            print(f"  Output filename: {output_filename}")
        else:
            print(f"  Making ONE API call for complete diagram...")
        
        # Use Vertex AI endpoint with Vertex AI key
        vertex_ai_key = self.vertex_ai_key
        print(f"  Using Vertex AI endpoint with Vertex AI key")
        print(f"  Vertex AI Key: {vertex_ai_key[:10]}...{vertex_ai_key[-10:]}")
        
        # Try gemini-2.5-flash-image models via Vertex AI endpoint
        models_to_try = [
            'gemini-2.5-flash-image',
            'gemini-2.5-flash-image-preview',
            'gemini-2.0-flash-exp-image-generation',
            'gemini-2.5-flash-lite'  # Add lite version
        ]
        
        max_retries = 3
        last_error = None
        
        for model_name in models_to_try:
            for retry in range(max_retries):
                try:
                    print(f"  Using Vertex AI model: {model_name}")
                    print(f"  Prompt length: {len(prompt)} characters")
                    
                    # Use Vertex AI endpoint format (key as query parameter, not Authorization header)
                    url = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model_name}:streamGenerateContent"
                    
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    # Use key as query parameter (as shown in user's curl example)
                    params = {
                        "key": vertex_ai_key
                    }
                    
                    payload = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.4
                        }
                    }
                    
                    response = requests.post(url, headers=headers, params=params, json=payload, timeout=120)
                    
                    # Check response status
                    if response.status_code == 200:
                        # Parse JSON response from Vertex AI
                        result = response.json()
                        
                        # Handle stream response (array of chunks) or single response
                        if isinstance(result, list):
                            # Stream response - collect all chunks
                            full_response = ""
                            for chunk in result:
                                if 'candidates' in chunk and len(chunk['candidates']) > 0:
                                    candidate = chunk['candidates'][0]
                                    if 'content' in candidate and 'parts' in candidate['content']:
                                        for part in candidate['content']['parts']:
                                            if 'text' in part:
                                                full_response += part['text']
                                            elif 'inlineData' in part:
                                                # Image data found
                                                image_data = part['inlineData']
                                                if image_data.get('mimeType', '').startswith('image/'):
                                                    image_bytes = base64.b64decode(image_data['data'])
                                                    filename = output_filename or "complete_sysml_diagram_gemini.png"
                                                    filepath = self.output_dir / filename
                                                    with open(filepath, 'wb') as f:
                                                        f.write(image_bytes)
                                                    print(f"  ✓ Saved Vertex AI-generated image to: {filepath}")
                                                    return str(filepath)
                        else:
                            # Single response object
                            if 'candidates' in result and len(result['candidates']) > 0:
                                candidate = result['candidates'][0]
                                if 'content' in candidate and 'parts' in candidate['content']:
                                    for part in candidate['content']['parts']:
                                        if 'inlineData' in part:
                                            # Image data found
                                            image_data = part['inlineData']
                                            if image_data.get('mimeType', '').startswith('image/'):
                                                image_bytes = base64.b64decode(image_data['data'])
                                                filename = output_filename or "complete_sysml_diagram_gemini.png"
                                                filepath = self.output_dir / filename
                                                with open(filepath, 'wb') as f:
                                                    f.write(image_bytes)
                                                print(f"  ✓ Saved Vertex AI-generated image to: {filepath}")
                                                return str(filepath)
                    
                    # If no image in response, check error
                    if response.status_code != 200:
                        error_msg = response.text[:500] if response.text else f"HTTP {response.status_code}"
                        raise Exception(f"Vertex AI API returned status {response.status_code}: {error_msg}")
                    
                    # If no image data found
                    raise Exception(f"No image data in response from {model_name}")
                    
                except Exception as e:
                    error_str = str(e)
                    last_error = e
                    
                    # Check if quota exceeded
                    if '429' in error_str or 'quota' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                        if retry < max_retries - 1:
                            # Extract wait time from error
                            wait_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                            if wait_match:
                                wait_seconds = float(wait_match.group(1))
                                wait_seconds = max(wait_seconds, 10)
                            else:
                                wait_seconds = 60 * (retry + 1)  # 60s, 120s
                            
                            print(f"  ⚠️  Quota exceeded for {model_name}. Waiting {wait_seconds:.0f}s... (retry {retry+1}/{max_retries})")
                            time.sleep(wait_seconds)
                            continue
                        else:
                            # Try next model
                            print(f"  ✗ {model_name} quota exhausted after retries, trying next model...")
                            break
                    elif '404' in error_str or 'not found' in error_str.lower():
                        # Model not found, try next model immediately
                        print(f"  ✗ {model_name} not found, trying next model...")
                        break
                    else:
                        # Other error, try next model
                        print(f"  ✗ {model_name} error: {str(e)[:100]}, trying next model...")
                        break
        
        # All models failed
        raise Exception(f"All Gemini API models failed. Last error: {last_error}")
    
    def _generate_image_via_alternative_endpoint(self, prompt: str, width: int = 1920, height: int = 1080) -> str:
        """Alternative method using different Imagen API endpoint."""
        import requests
        
        try:
            # Alternative endpoint format
            url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
            
            headers = {
                "Content-Type": "application/json",
            }
            
            params = {
                "key": self.api_key
            }
            
            payload = {
                "instances": [{
                    "prompt": prompt
                }],
                "parameters": {
                    "sampleCount": 1,
                    "aspectRatio": f"{width}:{height}",
                    "safetyFilterLevel": "block_some"
                }
            }
            
            print("  Trying alternative Imagen endpoint...")
            response = requests.post(url, headers=headers, params=params, json=payload, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if 'predictions' in result and len(result['predictions']) > 0:
                    pred = result['predictions'][0]
                    image_b64 = pred.get('bytesBase64Encoded') or pred.get('image') or pred.get('base64')
                    if image_b64:
                        image_bytes = base64.b64decode(image_b64)
                        filename = "complete_sysml_diagram_gemini.png"
                        filepath = self.output_dir / filename
                        with open(filepath, 'wb') as f:
                            f.write(image_bytes)
                        print(f"  ✓ Saved Gemini Imagen-generated image to: {filepath}")
                        return str(filepath)
            
            raise Exception(f"Alternative endpoint returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"Alternative endpoint failed: {e}")
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                print("⚠️  API quota exceeded. Falling back to JSON-based generation...")
            else:
                print("Falling back to JSON-based generation...")
            # Fallback: Try to load JSON if available, otherwise generate from SysML parsing
            json_file = sysml_file_path.replace('.sysml', '.json')
            if os.path.exists(json_file):
                print(f"  Loading existing JSON file: {json_file}")
                data = self.load_json(json_file)
                return self.generate_complete_diagram(data, width, height)
            elif os.path.exists('complete_slide.json'):
                print(f"  Loading complete_slide.json")
                data = self.load_json('complete_slide.json')
                return self.generate_complete_diagram(data, width, height)
            else:
                print("  ❌ No JSON file available for fallback. Please convert SysML to JSON first.")
                raise Exception(f"Gemini API failed and no JSON fallback available. Original error: {e}")
    
    def _render_diagram_from_spec(self, spec: Dict, width: int, height: int) -> str:
        """
        Render a diagram from Gemini-generated specification.
        """
        from PIL import Image, ImageDraw, ImageFont
        import math
        
        # Create image
        img = Image.new('RGB', (width, height), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_elem = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_elem = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # System boundary
        boundary_margin = 100
        boundary_x = boundary_margin
        boundary_y = 120
        boundary_width = width - 2 * boundary_margin
        boundary_height = height - boundary_y - boundary_margin
        
        # Draw system boundary
        boundary_color = '#1A1A1A'
        draw.rectangle(
            [boundary_x, boundary_y, boundary_x + boundary_width, boundary_y + boundary_height],
            outline=boundary_color, width=5
        )
        
        # System title
        system_title = spec.get('system_title', 'System')
        title_bbox = draw.textbbox((0, 0), system_title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = boundary_x + (boundary_width - title_width) // 2
        title_y = boundary_y + 20
        draw.text((title_x, title_y), system_title, fill=boundary_color, font=font_title)
        
        # Draw elements from specification
        element_positions = {}
        actor_radius = 60
        
        for elem in spec.get('elements', []):
            elem_name = elem['name']
            elem_type = elem['type']
            pos_info = elem.get('position', {})
            size_info = elem.get('size', {})
            
            x = boundary_x + pos_info.get('x', 200)
            y = boundary_y + 100 + pos_info.get('y', 200)
            w = size_info.get('width', 200)
            h = size_info.get('height', 100)
            
            colors = self.colors.get(elem_type, self.colors['PART'])
            
            if elem_type == 'USE_CASE':
                bbox = [x, y - h//2, x + w, y + h//2]
                draw.ellipse(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 8, bbox[1] + 8, 
                                 bbox[0] + w*0.5, bbox[1] + h*0.4]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.ellipse(highlight_bbox, fill=highlight_color, outline=None)
            elif elem_type == 'PART':
                bbox = [x, y - h//2, x + w, y + h//2]
                draw.rectangle(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 5, bbox[1] + 5, 
                                 bbox[2] - 5, bbox[1] + (bbox[3] - bbox[1])*0.35]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.rectangle(highlight_bbox, fill=highlight_color, outline=None)
            elif elem_type == 'ACTOR':
                center_x, center_y = x, y
                bbox = [center_x - actor_radius, center_y - actor_radius,
                       center_x + actor_radius, center_y + actor_radius]
                draw.ellipse(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_size = actor_radius * 0.5
                highlight_bbox = [center_x - highlight_size*0.7, center_y - highlight_size*0.7,
                                 center_x - highlight_size*0.7 + highlight_size*0.8,
                                 center_y - highlight_size*0.7 + highlight_size*0.8]
                highlight_color = self._lighten_color(colors['bg'], 0.6)
                draw.ellipse(highlight_bbox, fill=highlight_color, outline=None)
                element_positions[elem_name] = {
                    'type': 'ACTOR', 'center_x': center_x, 'center_y': center_y,
                    'x': center_x - actor_radius, 'y': center_y - actor_radius,
                    'width': actor_radius * 2, 'height': actor_radius * 2
                }
                # Draw text for actor
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = center_x - text_width // 2
                text_y = center_y + actor_radius + 10
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_small)
                continue
            elif elem_type == 'SUBJECT':
                bbox = [x, y - h//2, x + w, y + h//2]
                draw.rounded_rectangle(bbox, radius=15, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 5, bbox[1] + 5, 
                                 bbox[2] - 5, bbox[1] + (bbox[3] - bbox[1])*0.35]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.rounded_rectangle(highlight_bbox, radius=10, fill=highlight_color, outline=None)
            
            # Store position for arrows
            element_positions[elem_name] = {
                'type': elem_type, 'x': x, 'y': y, 'width': w, 'height': h
            }
            
            # Draw text
            if elem_type == 'USE_CASE':
                words = elem_name.split()
                lines = [' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])] if len(words) > 1 else [elem_name]
                line_height = 28
                start_y = y - (len(lines) * line_height) // 2
                for j, line in enumerate(lines):
                    text_bbox = draw.textbbox((0, 0), line, font=font_small)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = x + (w - text_width) // 2
                    draw.text((text_x, start_y + j * line_height), line, fill=colors['text'], font=font_small)
            else:
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_elem if elem_type != 'ACTOR' else font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x + (w - text_width) // 2 if elem_type != 'ACTOR' else center_x - text_width // 2
                text_y = y - (text_bbox[3] - text_bbox[1]) // 2 if elem_type != 'ACTOR' else center_y + actor_radius + 10
                draw.text((text_x, text_y), elem_name, fill=colors['text'], 
                         font=font_elem if elem_type != 'ACTOR' else font_small)
        
        # Draw associations
        for assoc in spec.get('associations', []):
            from_name = assoc['from']
            to_name = assoc['to']
            from_pos = element_positions.get(from_name)
            to_pos = element_positions.get(to_name)
            
            if from_pos and to_pos:
                # Calculate arrow points
                if from_pos['type'] == 'PART':
                    arrow_start_x = from_pos['x'] + from_pos['width']
                    arrow_start_y = from_pos['y']
                elif from_pos['type'] == 'ACTOR':
                    arrow_start_x = from_pos['center_x'] + actor_radius
                    arrow_start_y = from_pos['center_y']
                else:
                    arrow_start_x = from_pos['x'] + from_pos['width'] // 2
                    arrow_start_y = from_pos['y']
                
                if to_pos['type'] == 'ACTOR':
                    arrow_end_x = to_pos['center_x'] - actor_radius
                    arrow_end_y = to_pos['center_y']
                    self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                   False, '#000000', 3, orthogonal=True)
                else:
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                    self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                   False, '#000000', 3, orthogonal=False)
        
        # Save image
        filename = "complete_sysml_diagram_gemini.png"
        filepath = self.output_dir / filename
        img.save(filepath, 'PNG', quality=95)
        return str(filepath)
    
    def generate_complete_diagram(self, full_data: Dict, width: int = 1920, height: int = 1080) -> str:
        """
        Generate a complete SysML diagram with ALL associations and elements.
        Shows the full system context in one well-formatted diagram.
        """
        from PIL import Image, ImageDraw, ImageFont
        import math
        
        # Create image
        img = Image.new('RGB', (width, height), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_elem = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font_title = ImageFont.load_default()
            font_elem = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Extract all elements
        elements = full_data.get('elements', [])
        system_elem = None
        components = []
        use_cases = []
        actors = []
        subjects = []
        
        for elem in elements:
            elem_type = elem.get('element_type', '')
            if elem_type == 'SYSTEM':
                system_elem = elem
            elif elem_type == 'PART':
                components.append(elem)
            elif elem_type == 'USE_CASE':
                use_cases.append(elem)
            elif elem_type == 'ACTOR':
                actors.append(elem)
            elif elem_type == 'SUBJECT':
                subjects.append(elem)
        
        # System boundary
        boundary_margin = 100
        boundary_x = boundary_margin
        boundary_y = 120
        boundary_width = width - 2 * boundary_margin
        boundary_height = height - boundary_y - boundary_margin
        
        # Draw system boundary
        boundary_color = '#1A1A1A'
        draw.rectangle(
            [boundary_x, boundary_y, boundary_x + boundary_width, boundary_y + boundary_height],
            outline=boundary_color, width=5
        )
        
        # System title
        system_title = system_elem.get('text_content', full_data.get('slide_title', 'System')) if system_elem else full_data.get('slide_title', 'System')
        title_bbox = draw.textbbox((0, 0), system_title, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = boundary_x + (boundary_width - title_width) // 2
        title_y = boundary_y + 20
        draw.text((title_x, title_y), system_title, fill=boundary_color, font=font_title)
        
        # Inner area with better margins
        inner_margin = 100
        inner_x = boundary_x + inner_margin
        inner_y = boundary_y + 120
        inner_width = boundary_width - 2 * inner_margin
        inner_height = boundary_height - 140
        
        # Position all elements with improved smart layout
        element_positions = {}
        actor_radius = 60  # Slightly smaller for better spacing
        
        # Position USE CASES (ellipses) - center-left area
        uc_width = 420
        uc_height = 180
        uc_spacing = 60
        if len(use_cases) > 0:
            total_uc_width = len(use_cases) * (uc_width + uc_spacing) - uc_spacing
            start_uc_x = inner_x + 100  # Start from left with margin
            uc_y = inner_y + inner_height // 2  # Center vertically
            
            for i, uc in enumerate(use_cases):
                uc_x = start_uc_x + i * (uc_width + uc_spacing)
                elem_id = uc.get('element_id')
                element_positions[elem_id] = {
                    'x': uc_x, 'y': uc_y, 'width': uc_width, 'height': uc_height,
                    'type': 'USE_CASE', 'elem': uc
                }
        
        # Position ACTORS (circles) - on right side of use cases, distributed vertically
        if actors and len(use_cases) > 0:
            uc_pos = element_positions[use_cases[0].get('element_id')]
            actor_x = uc_pos['x'] + uc_width + 80  # Position to the right of use case
            
            for i, actor in enumerate(actors):
                # Distribute actors vertically with proper spacing
                if len(actors) == 1:
                    act_y = uc_pos['y']
                else:
                    # Space actors evenly within use case height + some margin
                    total_spacing = uc_pos['height'] + 100
                    spacing = total_spacing / max(1, len(actors) - 1) if len(actors) > 1 else 0
                    start_y = uc_pos['y'] - uc_pos['height']//2 - 30
                    act_y = start_y + i * spacing
                
                elem_id = actor.get('element_id')
                element_positions[elem_id] = {
                    'x': actor_x - actor_radius, 'y': act_y - actor_radius,
                    'width': actor_radius * 2, 'height': actor_radius * 2,
                    'type': 'ACTOR', 'elem': actor, 'center_x': actor_x, 'center_y': act_y
                }
        elif actors:
            # No use cases - position actors on right side
            for i, actor in enumerate(actors):
                actor_x = inner_x + inner_width - actor_radius - 40
                actor_y = inner_y + 150 + i * 140
                elem_id = actor.get('element_id')
                element_positions[elem_id] = {
                    'x': actor_x - actor_radius, 'y': actor_y - actor_radius,
                    'width': actor_radius * 2, 'height': actor_radius * 2,
                    'type': 'ACTOR', 'elem': actor, 'center_x': actor_x, 'center_y': actor_y
                }
        
        # Position COMPONENTS (rectangles) - bottom area, arranged horizontally with spacing
        comp_width = 260
        comp_height = 100
        comp_spacing = 50
        if len(components) > 0:
            total_comp_width = len(components) * (comp_width + comp_spacing) - comp_spacing
            start_comp_x = inner_x + (inner_width - total_comp_width) // 2
            comp_y = inner_y + inner_height - 80  # Position near bottom
            
            for i, comp in enumerate(components):
                comp_x = start_comp_x + i * (comp_width + comp_spacing)
                elem_id = comp.get('element_id')
                element_positions[elem_id] = {
                    'x': comp_x, 'y': comp_y, 'width': comp_width, 'height': comp_height,
                    'type': 'PART', 'elem': comp
                }
        
        # Position SUBJECTS (rounded rectangles) - top area, centered
        subj_width = 240
        subj_height = 90
        subj_spacing = 50
        if len(subjects) > 0:
            total_subj_width = len(subjects) * (subj_width + subj_spacing) - subj_spacing
            start_subj_x = inner_x + (inner_width - total_subj_width) // 2
            subj_y = inner_y + 60  # Position near top
            
            for i, subj in enumerate(subjects):
                subj_x = start_subj_x + i * (subj_width + subj_spacing)
                elem_id = subj.get('element_id')
                element_positions[elem_id] = {
                    'x': subj_x, 'y': subj_y, 'width': subj_width, 'height': subj_height,
                    'type': 'SUBJECT', 'elem': subj
                }
        
        # Draw all elements
        for elem_id, pos in element_positions.items():
            elem = pos['elem']
            elem_type = pos['type']
            elem_name = elem.get('text_content', '')
            colors = self.colors.get(elem_type, self.colors['PART'])
            
            if elem_type == 'USE_CASE':
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                draw.ellipse(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 8, bbox[1] + 8, 
                                 bbox[0] + pos['width']*0.5, bbox[1] + pos['height']*0.4]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.ellipse(highlight_bbox, fill=highlight_color, outline=None)
                # Text
                words = elem_name.split()
                lines = [' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])] if len(words) > 1 else [elem_name]
                line_height = 28
                start_y = pos['y'] - (len(lines) * line_height) // 2
                for j, line in enumerate(lines):
                    text_bbox = draw.textbbox((0, 0), line, font=font_small)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = pos['x'] + (pos['width'] - text_width) // 2
                    draw.text((text_x, start_y + j * line_height), line, fill=colors['text'], font=font_small)
            
            elif elem_type == 'PART':
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                draw.rectangle(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 5, bbox[1] + 5, 
                                 bbox[2] - 5, bbox[1] + (bbox[3] - bbox[1])*0.35]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.rectangle(highlight_bbox, fill=highlight_color, outline=None)
                # Text
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_elem)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = pos['x'] + (pos['width'] - text_width) // 2
                text_y = pos['y'] - (text_bbox[3] - text_bbox[1]) // 2
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_elem)
            
            elif elem_type == 'ACTOR':
                center_x = pos.get('center_x', pos['x'] + actor_radius)
                center_y = pos.get('center_y', pos['y'] + actor_radius)
                bbox = [center_x - actor_radius, center_y - actor_radius,
                       center_x + actor_radius, center_y + actor_radius]
                draw.ellipse(bbox, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_size = actor_radius * 0.5
                highlight_bbox = [center_x - highlight_size*0.7, center_y - highlight_size*0.7,
                                 center_x - highlight_size*0.7 + highlight_size*0.8,
                                 center_y - highlight_size*0.7 + highlight_size*0.8]
                highlight_color = self._lighten_color(colors['bg'], 0.6)
                draw.ellipse(highlight_bbox, fill=highlight_color, outline=None)
                # Text
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = center_x - text_width // 2
                text_y = center_y + actor_radius + 10
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_small)
            
            elif elem_type == 'SUBJECT':
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                draw.rounded_rectangle(bbox, radius=15, fill=colors['bg'], outline=colors['border'], width=4)
                # Shine
                highlight_bbox = [bbox[0] + 5, bbox[1] + 5, 
                                 bbox[2] - 5, bbox[1] + (bbox[3] - bbox[1])*0.35]
                highlight_color = self._lighten_color(colors['bg'], 0.5)
                draw.rounded_rectangle(highlight_bbox, radius=10, fill=highlight_color, outline=None)
                # Text
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = pos['x'] + (pos['width'] - text_width) // 2
                text_y = pos['y'] - (text_bbox[3] - text_bbox[1]) // 2
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_small)
        
        # Draw ALL relationship arrows (not just ASSOCIATION)
        relationships = self.extract_relationships(full_data)
        for rel in relationships:
            # Include ALL relationship types (ASSOCIATION, PARTICIPATES, SUBJECT_OF, etc.)
            
            from_name = rel['from_element']['name']
            to_name = rel['to_element']['name']
            from_pos = None
            to_pos = None
            
            for elem_id, pos in element_positions.items():
                elem = pos['elem']
                if elem.get('text_content') == from_name:
                    from_pos = pos
                if elem.get('text_content') == to_name:
                    to_pos = pos
            
            if from_pos and to_pos:
                # Calculate arrow start
                if from_pos['type'] == 'PART':
                    arrow_start_x = from_pos['x'] + from_pos['width']
                    arrow_start_y = from_pos['y']
                elif from_pos['type'] == 'ACTOR':
                    arrow_start_x = from_pos.get('center_x', from_pos['x'] + actor_radius) + actor_radius
                    arrow_start_y = from_pos.get('center_y', from_pos['y'] + actor_radius)
                elif from_pos['type'] == 'SUBJECT':
                    arrow_start_x = from_pos['x'] + from_pos['width']
                    arrow_start_y = from_pos['y']
                else:
                    arrow_start_x = from_pos['x'] + from_pos['width'] // 2
                    arrow_start_y = from_pos['y']
                
                # Calculate arrow end
                if to_pos['type'] == 'ACTOR':
                    actor_center_x = to_pos.get('center_x', to_pos['x'] + actor_radius)
                    actor_center_y = to_pos.get('center_y', to_pos['y'] + actor_radius)
                    arrow_end_x = actor_center_x - actor_radius
                    arrow_end_y = actor_center_y
                    self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                   False, '#000000', 3, orthogonal=True)
                elif to_pos['type'] == 'PART':
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                    self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                   False, '#000000', 3, orthogonal=False)
                elif to_pos['type'] == 'SUBJECT':
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                    self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                   False, '#000000', 3, orthogonal=False)
        
        # Save image
        filename = "complete_sysml_diagram_gemini.png"
        filepath = self.output_dir / filename
        img.save(filepath, 'PNG', quality=95)
        return str(filepath)
    
    def generate_image_with_context(self, relationship: Dict, full_data: Dict, 
                                    width: int = 1920, height: int = 1080) -> str:
        """
        Generate image for an INDIVIDUAL relationship showing ONLY relevant elements.
        For each relationship, shows:
        - System boundary with title
        - Relevant use case (ellipse inside boundary)
        - Specific component (rectangle inside boundary)
        - Specific actor (circle inside or outside boundary)
        - Arrow showing the relationship
        """
        # Create image with light thematic background (very light purple-cyan)
        base_color = (245, 240, 250)  # Very light purple-cyan
        img = Image.new('RGB', (width, height), color=base_color)
        draw = ImageDraw.Draw(img)
        
        # Draw light thematic gradient background
        for y in range(height):
            ratio = y / height
            r = int(245 + ratio * 5)
            g = int(240 + ratio * 10)
            b = int(250 + ratio * 5)
            r = min(255, max(235, r))
            g = min(255, max(235, g))
            b = min(255, max(245, b))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Load fonts
        try:
            font_title = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
            font_elem = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
            font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
            font_rel = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        except:
            font_title = ImageFont.load_default()
            font_elem = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_rel = ImageFont.load_default()
        
        # Extract elements from full_data
        elements = full_data.get('elements', [])
        system_title = full_data.get('slide_title', 'System')
        
        # Get system element
        system_elem = None
        for elem in elements:
            if elem.get('element_type') == 'SYSTEM':
                system_elem = elem
                break
        
        # Get the specific elements for THIS relationship only
        from_name = relationship['from_element']['name']
        to_name = relationship['to_element']['name']
        from_type = relationship['from_element']['type']
        to_type = relationship['to_element']['type']
        
        # Find the specific component and actor elements
        from_elem = None
        to_elem = None
        relevant_use_case = None
        relevant_subject = None
        
        for elem in elements:
            elem_name = elem.get('text_content', '')
            elem_type = elem.get('element_type', '')
            
            if elem_name == from_name and elem_type == from_type:
                from_elem = elem
            if elem_name == to_name and elem_type == to_type:
                to_elem = elem
        
        # Find relevant use case - check actor_to_use_case or subject_to_use_case relationships
        # For part_to_actor, find use case that the actor connects to
        if to_type == 'ACTOR':
            # Check connections_summary to find use case connected to this actor
            connections_summary = full_data.get('connections_summary', {})
            actor_to_uc = connections_summary.get('actor_to_use_case', [])
            for rel_str in actor_to_uc:
                if to_name in rel_str and ' → ' in rel_str:
                    parts = rel_str.split(' → ')
                    if len(parts) == 2 and parts[0] == to_name:
                        uc_name = parts[1]
                        # Find the use case element
                        for elem in elements:
                            if elem.get('text_content') == uc_name and elem.get('element_type') == 'USE_CASE':
                                relevant_use_case = elem
                                break
                    if relevant_use_case:
                        break
        
        # For actor_to_use_case relationships, the use case is the target
        if to_type == 'USE_CASE':
            relevant_use_case = to_elem
        
        # For part_to_subject relationships, find the subject
        if to_type == 'SUBJECT':
            relevant_subject = to_elem
            # Also find use case connected to subject
            connections_summary = full_data.get('connections_summary', {})
            subj_to_uc = connections_summary.get('subject_to_use_case', [])
            for rel_str in subj_to_uc:
                if to_name in rel_str:
                    uc_name = rel_str.split(' → ')[1].split(' ')[0] if ' → ' in rel_str else None
                    if uc_name:
                        for elem in elements:
                            if elem.get('text_content') == uc_name and elem.get('element_type') == 'USE_CASE':
                                relevant_use_case = elem
                                break
        
        # If no use case found yet, get the first one (fallback)
        if not relevant_use_case:
            for elem in elements:
                if elem.get('element_type') == 'USE_CASE':
                    relevant_use_case = elem
                    break
        
        # System boundary (outer rectangle)
        boundary_margin = 100
        boundary_x = boundary_margin
        boundary_y = 120  # Space for relationship title
        boundary_width = width - 2 * boundary_margin
        boundary_height = height - boundary_y - boundary_margin
        
        # Draw system boundary rectangle
        boundary_color = '#1A1A1A'  # Dark for high contrast
        draw.rectangle(
            [boundary_x, boundary_y, boundary_x + boundary_width, boundary_y + boundary_height],
            outline=boundary_color, width=5
        )
        
        # System title at top of boundary
        title_text = system_elem.get('text_content', system_title) if system_elem else system_title
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = boundary_x + (boundary_width - title_width) // 2
        title_y = boundary_y + 20
        draw.text((title_x, title_y), title_text, fill=boundary_color, font=font_title)
        
        # Inner area for positioning elements
        inner_margin = 60
        inner_x = boundary_x + inner_margin
        inner_y = boundary_y + 80
        inner_width = boundary_width - 2 * inner_margin
        inner_height = boundary_height - 100
        
        # Position ONLY the relevant elements for this relationship
        element_positions = {}
        actor_radius = 70  # Increased size
        
        # Position USE CASE (ellipse) inside boundary - center-left (increased size)
        if relevant_use_case:
            uc_width = 480
            uc_height = 240
            uc_x = inner_x + 150
            uc_y = inner_y + inner_height // 2
            elem_id = relevant_use_case.get('element_id')
            element_positions[elem_id] = {
                'x': uc_x, 'y': uc_y, 'width': uc_width, 'height': uc_height,
                'type': 'USE_CASE', 'elem': relevant_use_case
            }
        
        # Position COMPONENT (rectangle) inside boundary - bottom-left (increased size)
        if from_elem and from_type == 'PART':
            comp_width = 320
            comp_height = 140
            comp_x = inner_x + 100
            comp_y = inner_y + inner_height - 120
            elem_id = from_elem.get('element_id')
            element_positions[elem_id] = {
                'x': comp_x, 'y': comp_y, 'width': comp_width, 'height': comp_height,
                'type': 'PART', 'elem': from_elem
            }
        
        # Position ACTOR (circle) - INSIDE boundary, on edge of use case ellipse
        if to_elem and to_type == 'ACTOR':
            # Position actor INSIDE the boundary, tangent to use case ellipse edge
            if relevant_use_case and relevant_use_case.get('element_id') in element_positions:
                uc_pos = element_positions[relevant_use_case.get('element_id')]
                # Position actor circle tangent to use case ellipse on the right side
                # Actor center positioned to be tangent to ellipse (slightly inside ellipse edge)
                # Ellipse right edge is at: uc_pos['x'] + uc_pos['width']
                # Position actor so it's just touching the ellipse edge
                actor_x = uc_pos['x'] + uc_pos['width'] - 10  # Slightly inside, tangent to ellipse
                actor_y = uc_pos['y']  # Align with use case center vertically
                elem_id = to_elem.get('element_id')
                element_positions[elem_id] = {
                    'x': actor_x - actor_radius, 'y': actor_y - actor_radius,
                    'width': actor_radius * 2, 'height': actor_radius * 2,
                    'type': 'ACTOR', 'elem': to_elem, 'center_x': actor_x, 'center_y': actor_y
                }
            else:
                # No use case - position inside boundary near right edge
                actor_x = boundary_x + boundary_width - actor_radius - 20  # Inside boundary
                actor_y = inner_y + inner_height // 2
                elem_id = to_elem.get('element_id')
                element_positions[elem_id] = {
                    'x': actor_x - actor_radius, 'y': actor_y - actor_radius,
                    'width': actor_radius * 2, 'height': actor_radius * 2,
                    'type': 'ACTOR', 'elem': to_elem, 'center_x': actor_x, 'center_y': actor_y
                }
        
        # Position SUBJECT (rounded rectangle) if relevant (increased size)
        if relevant_subject:
            subj_width = 300
            subj_height = 130
            subj_x = inner_x + inner_width - 250
            subj_y = inner_y + 150
            elem_id = relevant_subject.get('element_id')
            element_positions[elem_id] = {
                'x': subj_x, 'y': subj_y, 'width': subj_width, 'height': subj_height,
                'type': 'SUBJECT', 'elem': relevant_subject
            }
        
        # Also position from_elem if it's an actor (INSIDE boundary, on use case edge)
        if from_elem and from_type == 'ACTOR':
            # Position INSIDE boundary, tangent to use case if present
            if relevant_use_case and relevant_use_case.get('element_id') in element_positions:
                uc_pos = element_positions[relevant_use_case.get('element_id')]
                actor_x = uc_pos['x'] + uc_pos['width'] - 10  # Tangent to ellipse
                actor_y = uc_pos['y'] - 80  # Slightly above use case center
            else:
                actor_x = boundary_x + boundary_width - actor_radius - 20  # Inside boundary
                actor_y = inner_y + inner_height // 2 - 100
            elem_id = from_elem.get('element_id')
            element_positions[elem_id] = {
                'x': actor_x - actor_radius, 'y': actor_y - actor_radius,
                'width': actor_radius * 2, 'height': actor_radius * 2,
                'type': 'ACTOR', 'elem': from_elem, 'center_x': actor_x, 'center_y': actor_y
            }
        
        # Draw all relevant elements
        for elem_id, pos in element_positions.items():
            elem = pos['elem']
            elem_type = pos['type']
            elem_name = elem.get('text_content', '')
            colors = self.colors.get(elem_type, self.colors['PART'])
            
            if elem_type == 'USE_CASE':
                # Ellipse inside boundary - no shading, prominent boundary
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                # Draw main ellipse with white fill and prominent border
                draw.ellipse(bbox, fill='#FFFFFF', outline=colors['border'], width=6)
                # Text (word wrap)
                words = elem_name.split()
                lines = []
                if len(words) > 2:
                    mid = len(words) // 2
                    lines = [' '.join(words[:mid]), ' '.join(words[mid:])]
                elif len(words) == 2:
                    lines = [words[0], words[1]]
                else:
                    lines = [elem_name]
                line_height = 28
                start_y = pos['y'] - (len(lines) * line_height) // 2
                for j, line in enumerate(lines):
                    text_bbox = draw.textbbox((0, 0), line, font=font_small)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_x = pos['x'] + (pos['width'] - text_width) // 2
                    draw.text((text_x, start_y + j * line_height), line, fill=colors['text'], font=font_small)
            elif elem_type == 'PART':
                # Rectangle inside boundary - no shading, prominent boundary
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                # Draw main rectangle with white fill and prominent border
                draw.rectangle(bbox, fill='#FFFFFF', outline=colors['border'], width=6)
                # Text
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_elem)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = pos['x'] + (pos['width'] - text_width) // 2
                text_y = pos['y'] - (text_bbox[3] - text_bbox[1]) // 2
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_elem)
            elif elem_type == 'ACTOR':
                # Circle - no shading, prominent boundary
                center_x = pos.get('center_x', pos['x'] + actor_radius)
                center_y = pos.get('center_y', pos['y'] + actor_radius)
                bbox = [center_x - actor_radius, center_y - actor_radius,
                       center_x + actor_radius, center_y + actor_radius]
                # Draw main circle with white fill and prominent border
                draw.ellipse(bbox, fill='#FFFFFF', outline=colors['border'], width=6)
                # Text below or above circle
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = center_x - text_width // 2
                # Text below if inside boundary, above if outside
                if center_y > boundary_y + 50:
                    text_y = center_y + actor_radius + 10
                else:
                    text_y = center_y - actor_radius - 25
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_small)
            elif elem_type == 'SUBJECT':
                # Rounded rectangle inside boundary - no shading, prominent boundary
                bbox = [pos['x'], pos['y'] - pos['height']//2,
                       pos['x'] + pos['width'], pos['y'] + pos['height']//2]
                # Draw main rounded rectangle with white fill and prominent border
                draw.rounded_rectangle(bbox, radius=15, fill='#FFFFFF', outline=colors['border'], width=6)
                # Text
                text_bbox = draw.textbbox((0, 0), elem_name, font=font_small)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = pos['x'] + (pos['width'] - text_width) // 2
                text_y = pos['y'] - (text_bbox[3] - text_bbox[1]) // 2
                draw.text((text_x, text_y), elem_name, fill=colors['text'], font=font_small)
        
        # Draw the relationship arrow
        from_pos = None
        to_pos = None
        
        for elem_id, pos in element_positions.items():
            elem = pos['elem']
            if elem.get('text_content') == from_name:
                from_pos = pos
            if elem.get('text_content') == to_name:
                to_pos = pos
        
        # Draw arrow from source to target
        # For associations with actors, arrow must cross/reach the boundary
        if from_pos and to_pos:
            # Calculate arrow start (from element edge)
            if from_pos['type'] == 'PART':
                arrow_start_x = from_pos['x'] + from_pos['width']
                arrow_start_y = from_pos['y']
            elif from_pos['type'] == 'ACTOR':
                arrow_start_x = from_pos.get('center_x', from_pos['x'] + actor_radius)
                arrow_start_y = from_pos.get('center_y', from_pos['y'] + actor_radius)
            elif from_pos['type'] == 'SUBJECT':
                arrow_start_x = from_pos['x'] + from_pos['width']
                arrow_start_y = from_pos['y']
            else:
                arrow_start_x = from_pos['x'] + from_pos['width'] // 2
                arrow_start_y = from_pos['y']
            
            # Calculate arrow end (to element edge)
            if to_pos['type'] == 'ACTOR':
                # Actor is INSIDE boundary, on use case edge
                # Use 90-degree (orthogonal) arrow for cleaner connection
                # Arrow must touch the circle edge precisely (no gap, no overlap)
                actor_center_x = to_pos.get('center_x', to_pos['x'] + actor_radius)
                actor_center_y = to_pos.get('center_y', to_pos['y'] + actor_radius)
                # For orthogonal arrow: horizontal segment ends at circle's left edge x-coordinate
                # Vertical segment connects to circle at its center y (touching left side)
                arrow_end_x = actor_center_x - actor_radius  # Circle's left edge x-coordinate
                arrow_end_y = actor_center_y  # Circle's center y (where arrow touches left edge)
                # Draw 90-degree arrow from component to actor (touches circle precisely)
                self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                               False, '#000000', 4, orthogonal=True)
            else:
                # Internal association (no boundary crossing)
                if to_pos['type'] == 'PART':
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                elif to_pos['type'] == 'SUBJECT':
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                elif to_pos['type'] == 'USE_CASE':
                    arrow_end_x = to_pos['x']
                    arrow_end_y = to_pos['y']
                else:
                    arrow_end_x = to_pos['x'] + to_pos['width'] // 2
                    arrow_end_y = to_pos['y']
                
                # Draw arrow (direct line for internal associations)
                arrow_color = '#000000'
                line_style = relationship.get('line_style', 'SOLID')
                self._draw_arrow(draw, arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                               line_style == 'DASHED', arrow_color, 4)
        
        # Draw relationship title at top
        rel_title = relationship.get('description', f"{from_name} → {to_name}")
        title_bbox = draw.textbbox((0, 0), rel_title, font=font_rel)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (width - title_width) // 2
        draw.text((title_x, 30), rel_title, fill='#2C3E50', font=font_rel)
        
        # Save image
        safe_name = re.sub(r'[^\w\s-]', '', relationship['description']).replace(' ', '_')
        filename = f"{safe_name}_{relationship['relationship_id']}.png"
        filepath = self.output_dir / filename
        
        img.save(filepath, 'PNG', quality=95)
        return str(filepath)
    
    def save_metadata(self, relationships: List[Dict], output_path: str = 'relationship_images_metadata.json', sysml_comments: List[Dict] = None):
        """Save metadata about all generated images."""
        metadata = {
            'relationships': relationships,
            'categories': {},
            'sysml_comments': sysml_comments or []
        }
        
        # Group by category
        for rel in relationships:
            category = rel.get('relationship_category', 'other')
            if category not in metadata['categories']:
                metadata['categories'][category] = []
            metadata['categories'][category].append(rel['relationship_id'])
        
        # Try to load existing sysml_comments if not provided
        if not sysml_comments and os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if 'sysml_comments' in existing:
                        metadata['sysml_comments'] = existing['sysml_comments']
            except:
                pass
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\nMetadata saved to: {output_path}")
        if metadata['sysml_comments']:
            print(f"  • SysML comments: {len(metadata['sysml_comments'])}")


def main():
    """Main function to generate images from JSON file."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate images for SysML relationships using Gemini API')
    parser.add_argument('json_file', help='Path to the JSON file (e.g., complete_slide.json)')
    parser.add_argument('--api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--output-dir', default='generated_images', help='Output directory for images')
    
    args = parser.parse_args()
    
    try:
        generator = GeminiImageGenerator(api_key=args.api_key)
        generator.output_dir = Path(args.output_dir)
        generator.output_dir.mkdir(exist_ok=True)
        
        print(f"Loading JSON from: {args.json_file}")
        relationships = generator.generate_all_images(args.json_file)
        
        print(f"\n✓ Generated {len([r for r in relationships if r.get('image_path')])} images")
        generator.save_metadata(relationships)
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

