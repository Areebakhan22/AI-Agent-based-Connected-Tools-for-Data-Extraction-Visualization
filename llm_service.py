"""
LLM Service Module

This module handles interactions with Ollama (local LLM) for semantic
understanding of SysML files. It replaces regex-based parsing with
AI-driven interpretation.
"""

import json
import ollama
from typing import Dict, Optional
import re


class LLMService:
    """
    Service for interacting with Ollama LLM to parse SysML files.
    """
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        """
        Initialize LLM service.
        
        Args:
            model: Ollama model name (default: "llama3")
            base_url: Ollama API base URL (default: localhost)
        """
        self.model = model
        self.base_url = base_url
        # Test connection on initialization
        self._check_ollama_connection()
    
    def _check_ollama_connection(self):
        """
        Check if Ollama is running and model is available.
        """
        try:
            # Try to list models to verify Ollama is running
            response = ollama.list()
            # Handle both dict and object response formats
            if hasattr(response, 'models'):
                available_models = [model.model for model in response.models]
            elif isinstance(response, dict):
                available_models = [model['name'] for model in response.get('models', [])]
            else:
                available_models = []
            
            # Check if our model is available
            model_found = any(self.model in model_name for model_name in available_models)
            
            if not model_found:
                print(f"⚠️  Warning: Model '{self.model}' not found in Ollama.")
                print(f"   Available models: {', '.join(available_models) if available_models else 'None'}")
                print(f"   Please run: ollama pull {self.model}")
            else:
                print(f"✓ Ollama connection verified. Using model: {self.model}")
        except Exception as e:
            print(f"⚠️  Warning: Could not connect to Ollama: {e}")
            print(f"   Make sure Ollama is running. Start it with: ollama serve")
            print(f"   Or install it from: https://ollama.ai")
    
    def extract_sysml(self, sysml_content: str) -> Dict:
        """
        Use LLM to extract structured information from SysML content.
        
        Args:
            sysml_content: Raw SysML file content as string
            
        Returns:
            Dictionary with 'parts', 'hierarchy', and 'connections' keys
            {
                'parts': [{'name': 'PartName', 'doc': 'description', 'parent': 'ParentName' or None, 'is_top_level': True/False}, ...],
                'hierarchy': {'ParentName': ['Child1', 'Child2', ...], ...},
                'connections': [{'from': 'SourcePart', 'to': 'TargetPart'}, ...]
            }
        """
        # Create comprehensive prompt for LLM
        prompt = self._create_extraction_prompt(sysml_content)
        
        try:
            # Call Ollama API
            print(f"🤖 Using {self.model} to interpret SysML...")
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a SysML v2 expert. Extract structured information from SysML files and return valid JSON only.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'temperature': 0.1,  # Low temperature for consistent, structured output
                }
            )
            
            # Extract response content
            llm_response = response['message']['content']
            
            # Parse JSON from response (LLM might include markdown code blocks)
            structured_data = self._parse_llm_response(llm_response)
            
            # Normalize and validate the structure
            normalized_data = self._normalize_structure(structured_data)
            
            print(f"✓ LLM extraction completed successfully")
            return normalized_data
            
        except Exception as e:
            print(f"✗ Error calling Ollama: {e}")
            raise
    
    def _create_extraction_prompt(self, sysml_content: str) -> str:
        """
        Create a detailed prompt for SysML extraction.
        
        Args:
            sysml_content: Raw SysML content
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze this SysML v2 file and extract all structured information.

SysML Content:
```
{sysml_content}
```

Extract and return ONLY valid JSON (no markdown, no explanations) with this exact structure:
{{
  "parts": [
    {{
      "name": "PartName",
      "doc": "description or empty string",
      "parent": "ParentName or null",
      "is_top_level": true or false
    }}
  ],
  "actors": [
    {{
      "name": "ActorName",
      "doc": "description or empty string"
    }}
  ],
  "use_cases": [
    {{
      "name": "UseCaseName",
      "doc": "description or empty string",
      "objectives": ["objective1", "objective2"]
    }}
  ],
  "hierarchy": {{
    "ParentName": ["Child1", "Child2"]
  }},
  "connections": [
    {{
      "from": "SourcePart",
      "to": "TargetPart"
    }}
  ]
}}

Rules:
1. Extract ALL parts (both "part def" and nested "part" declarations)
2. Mark top-level parts (defined with "part def") with "is_top_level": true
3. Mark nested parts with "is_top_level": false and set their "parent"
4. Extract ALL actors (declared with "actor" keyword)
5. Extract ALL use cases (declared with "use case" keyword)
6. Extract objectives from use cases (from "objective" blocks with "doc" comments)
7. Extract ALL "connect X to Y" statements as connections
   - For Individual Relationship Diagrams: Identify Source Part and Target Actor
   - Each connection represents: Part (Rectangle) → Actor (Circle/Port on Use Case Oval)
8. Build hierarchy mapping parent names to arrays of child names
9. Extract documentation from "doc" comments if present
10. Return ONLY the JSON object, no additional text

Individual Relationship Diagram Mapping:
- Use Case → Large Oval (Center position)
- Part → Rectangle (Peripheral position)
- Actor → Small Circle (Port) anchored to Use Case Oval's edge
- Connection: Arrow from closest edge of Part Rectangle to center of Actor Circle
- All shapes and connections should be medium-sized
- Must fit within 16:9 aspect ratio

Return the JSON now:"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict:
        """
        Parse JSON from LLM response, handling markdown code blocks.
        
        Args:
            response: Raw LLM response string
            
        Returns:
            Parsed dictionary
        """
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response.strip()
        
        # Parse JSON
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Failed to parse LLM JSON response. Attempting to fix...")
            # Try to extract just the JSON part
            json_str = self._extract_json_from_text(json_str)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"✗ Error: Could not parse LLM response as JSON")
                print(f"   Response preview: {response[:200]}...")
                raise ValueError(f"Invalid JSON response from LLM: {e}")
    
    def _extract_json_from_text(self, text: str) -> str:
        """
        Attempt to extract valid JSON from text that might have extra content.
        """
        # Find the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text
    
    def _normalize_structure(self, data: Dict) -> Dict:
        """
        Normalize and validate the extracted data structure.
        Ensures it matches the expected format.
        
        Args:
            data: Raw parsed data from LLM
            
        Returns:
            Normalized dictionary with required structure
        """
        # Initialize structure
        normalized = {
            'parts': [],
            'actors': [],
            'use_cases': [],
            'hierarchy': {},
            'connections': []
        }
        
        # Normalize parts
        if 'parts' in data and isinstance(data['parts'], list):
            for part in data['parts']:
                normalized_part = {
                    'name': str(part.get('name', '')),
                    'doc': str(part.get('doc', '')),
                    'parent': part.get('parent') if part.get('parent') else None,
                    'is_top_level': bool(part.get('is_top_level', False))
                }
                normalized['parts'].append(normalized_part)
        
        # Normalize actors
        if 'actors' in data and isinstance(data['actors'], list):
            for actor in data['actors']:
                normalized_actor = {
                    'name': str(actor.get('name', '')),
                    'doc': str(actor.get('doc', ''))
                }
                normalized['actors'].append(normalized_actor)
        else:
            # If actors not extracted, try to infer from connections
            part_names = {p['name'] for p in normalized['parts']}
            if 'connections' in data:
                for conn in data['connections']:
                    for elem in [conn.get('from'), conn.get('to')]:
                        if elem and elem not in part_names:
                            # Might be an actor
                            if not any(a['name'] == elem for a in normalized['actors']):
                                normalized['actors'].append({'name': str(elem), 'doc': ''})
        
        # Normalize use cases
        if 'use_cases' in data and isinstance(data['use_cases'], list):
            for uc in data['use_cases']:
                normalized_uc = {
                    'name': str(uc.get('name', '')),
                    'doc': str(uc.get('doc', '')),
                    'objectives': uc.get('objectives', []) if isinstance(uc.get('objectives'), list) else []
                }
                normalized['use_cases'].append(normalized_uc)
        
        # Normalize hierarchy
        if 'hierarchy' in data and isinstance(data['hierarchy'], dict):
            normalized['hierarchy'] = data['hierarchy']
        
        # Normalize connections
        if 'connections' in data and isinstance(data['connections'], list):
            for conn in data['connections']:
                normalized_conn = {
                    'from': str(conn.get('from', '')),
                    'to': str(conn.get('to', ''))
                }
                normalized['connections'].append(normalized_conn)
        
        return normalized

