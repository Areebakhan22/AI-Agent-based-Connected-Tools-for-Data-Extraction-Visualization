#!/usr/bin/env python3
"""
Backend API Server for Interactive SysML Diagrams

Provides REST API and WebSocket support for real-time diagram editing.
Integrates with existing LLM pipeline output.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import threading
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app, 
    cors_allowed_origins="*", 
    async_mode='threading',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Store diagram state in memory (use Redis for production)
diagram_states: Dict[str, Dict] = {}
diagram_lock = threading.Lock()

# Base directory for JSON files
BASE_DIR = Path(__file__).parent.parent


def load_json_file(filename: str) -> Optional[Dict]:
    """Load JSON file from project directory."""
    file_path = BASE_DIR / filename
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return None


def save_json_file(filename: str, data: Dict):
    """Save JSON file to project directory."""
    file_path = BASE_DIR / filename
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filename}: {e}")


@app.route('/api/diagrams', methods=['GET'])
def get_diagrams():
    """Get list of available diagrams from react_diagrams.json (SysML generated)."""
    diagrams = []
    
    # Load react_diagrams.json which contains SysML-generated diagrams
    react_data = load_json_file('react_diagrams.json')
    
    if react_data and 'diagrams' in react_data:
        for diagram in react_data['diagrams']:
            diagrams.append({
                'id': diagram.get('id', ''),
                'title': diagram.get('title', 'Untitled'),
                'is_full_diagram': diagram.get('metadata', {}).get('is_full_diagram', False),
                'system_name': react_data.get('system_name', 'SysML System')
            })
    else:
        # Fallback: try to find SysML source files and suggest generation
        sysml_files = list(BASE_DIR.glob('*.sysml'))
        for sysml_file in sysml_files:
            diagrams.append({
                'id': sysml_file.stem,
                'title': f"{sysml_file.stem} (needs generation)",
                'needs_generation': True,
                'sysml_file': sysml_file.name
            })
    
    return jsonify(diagrams)


@app.route('/api/diagram/<diagram_id>', methods=['GET'])
def get_diagram(diagram_id: str):
    """Get diagram data by ID from react_diagrams.json."""
    # Load react_diagrams.json
    react_data = load_json_file('react_diagrams.json')
    
    if react_data and 'diagrams' in react_data:
        # Find the specific diagram
        for diagram in react_data['diagrams']:
            if diagram.get('id') == diagram_id:
                return jsonify(diagram)
    
    # Check if diagram is in memory state
    with diagram_lock:
        if diagram_id in diagram_states:
            return jsonify(diagram_states[diagram_id])
    
    return jsonify({'error': 'Diagram not found. Run: python3 generate_react_diagrams.py OpsCon.json'}), 404


@app.route('/api/diagram/<diagram_id>', methods=['POST'])
def update_diagram(diagram_id: str):
    """Update diagram state."""
    data = request.json
    
    with diagram_lock:
        diagram_states[diagram_id] = data
    
    # Broadcast update to all connected clients
    socketio.emit('diagram_update', {
        'type': 'diagram_update',
        'data': data
    }, room=diagram_id)
    
    # Optionally save to JSON file
    filename = f"{diagram_id}_updated.json"
    save_json_file(filename, data)
    
    return jsonify({'status': 'updated', 'diagram_id': diagram_id})


@socketio.on('connect')
def handle_connect(auth):
    """Handle WebSocket connection."""
    print(f"WebSocket connection attempt - auth: {auth}")
    diagram_id = request.args.get('diagramId')
    if not diagram_id and auth:
        diagram_id = auth.get('diagramId')
    
    print(f"Client connecting to diagram: {diagram_id}")
    
    if diagram_id:
        join_room(diagram_id)
        print(f"✓ Client joined room: {diagram_id}")
        
        # Send current state to new client
        with diagram_lock:
            if diagram_id in diagram_states:
                emit('diagram_update', {
                    'type': 'diagram_update',
                    'data': diagram_states[diagram_id]
                })
            else:
                # Try to load from react_diagrams.json
                react_data = load_json_file('react_diagrams.json')
                if react_data and 'diagrams' in react_data:
                    for diagram in react_data['diagrams']:
                        if diagram.get('id') == diagram_id:
                            diagram_states[diagram_id] = diagram
                            emit('diagram_update', {
                                'type': 'diagram_update',
                                'data': diagram
                            })
                            break
    else:
        print("⚠️  No diagram_id provided in connection")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print("Client disconnected")


@socketio.on('node_update')
def handle_node_update(data: Dict):
    """Handle node drag/rename updates from clients."""
    diagram_id = data.get('diagramId')
    update_type = data.get('type')
    
    if not diagram_id:
        return
    
    with diagram_lock:
        # Load or get current state
        if diagram_id not in diagram_states:
            filename = f"{diagram_id}.json"
            file_data = load_json_file(filename)
            if file_data:
                diagram_states[diagram_id] = file_data
            else:
                diagram_states[diagram_id] = {'nodes': [], 'links': []}
        
        state = diagram_states[diagram_id]
        
        # Apply update based on type
        if update_type == 'node_moved':
            node_id = data.get('nodeId')
            position = data.get('position', {})
            
            # Update node position in state
            if 'nodes' in state:
                for node in state.get('nodes', []):
                    if node.get('id') == node_id:
                        node['x'] = position.get('x', node.get('x', 0))
                        node['y'] = position.get('y', node.get('y', 0))
                        node['fx'] = position.get('x')
                        node['fy'] = position.get('y')
                        break
        
        elif update_type == 'node_renamed':
            node_id = data.get('nodeId')
            new_name = data.get('name')
            
            # Update node name in state
            if 'nodes' in state:
                for node in state.get('nodes', []):
                    if node.get('id') == node_id:
                        node['name'] = new_name
                        break
        
        # Broadcast update to all clients (except sender)
        emit('node_update', data, room=diagram_id, include_self=False)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'sysml-diagram-api'})

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests."""
    return '', 204  # No content

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Route not found', 'path': request.path}), 404


if __name__ == '__main__':
    print("Starting SysML Diagram API Server...")
    print("API: http://localhost:5000/api")
    print("WebSocket: ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)

