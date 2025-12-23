#!/usr/bin/env python3
"""
State Manager for Diagram Data

Manages diagram state persistence and synchronization.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import threading

class DiagramStateManager:
    """Manages diagram state with thread-safe operations."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.states: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self.state_dir = self.base_dir / 'diagram_states'
        self.state_dir.mkdir(exist_ok=True)
    
    def load_state(self, diagram_id: str) -> Optional[Dict]:
        """Load diagram state from file."""
        state_file = self.state_dir / f"{diagram_id}.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading state for {diagram_id}: {e}")
        
        return None
    
    def save_state(self, diagram_id: str, state: Dict):
        """Save diagram state to file."""
        state_file = self.state_dir / f"{diagram_id}.json"
        
        try:
            state['_metadata'] = {
                'last_updated': datetime.now().isoformat(),
                'diagram_id': diagram_id
            }
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving state for {diagram_id}: {e}")
    
    def get_state(self, diagram_id: str) -> Optional[Dict]:
        """Get diagram state (from memory or file)."""
        with self.lock:
            if diagram_id in self.states:
                return self.states[diagram_id]
            
            # Try loading from file
            state = self.load_state(diagram_id)
            if state:
                self.states[diagram_id] = state
            return state
    
    def update_state(self, diagram_id: str, updates: Dict):
        """Update diagram state."""
        with self.lock:
            if diagram_id not in self.states:
                self.states[diagram_id] = self.load_state(diagram_id) or {}
            
            # Merge updates
            self.states[diagram_id].update(updates)
            
            # Save to file
            self.save_state(diagram_id, self.states[diagram_id])
    
    def list_diagrams(self) -> List[str]:
        """List all available diagram IDs."""
        diagram_ids = set()
        
        # From memory
        with self.lock:
            diagram_ids.update(self.states.keys())
        
        # From files
        if self.state_dir.exists():
            for file in self.state_dir.glob('*.json'):
                diagram_ids.add(file.stem)
        
        return sorted(list(diagram_ids))

