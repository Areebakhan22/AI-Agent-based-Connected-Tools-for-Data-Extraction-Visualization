# React + D3.js Interactive Diagram Setup Guide

This guide explains how to set up and use the new React + D3.js interactive diagram system that replaces Google Slides while preserving your existing LLM pipeline.

## Architecture Overview

```
┌─────────────────────────────────────┐
│  Existing LLM Pipeline (UNCHANGED)  │
│  - llm_service.py                    │
│  - visualize_sysml.py               │
│  - SemanticModelProcessor           │
│  - RelationshipSplitter              │
│  - GraphLayoutEngine                │
└──────────────┬──────────────────────┘
               │
               │ JSON Output
               ▼
┌─────────────────────────────────────┐
│  React Renderer (NEW)               │
│  - react_renderer.py                │
│  - generate_react_diagrams.py      │
└──────────────┬──────────────────────┘
               │
               │ React JSON Format
               ▼
┌─────────────────────────────────────┐
│  Backend API Server (NEW)            │
│  - backend/api_server.py             │
│  - WebSocket support                 │
│  - State management                  │
└──────────────┬──────────────────────┘
               │
               │ REST API / WebSocket
               ▼
┌─────────────────────────────────────┐
│  React Frontend (NEW)               │
│  - React components                  │
│  - D3.js rendering                  │
│  - Real-time updates                │
└─────────────────────────────────────┘
```

## Prerequisites

1. **Python 3.8+** (already installed)
2. **Node.js 16+** and npm
3. **Existing LLM pipeline** (already working)

## Installation

### 1. Install Backend Dependencies

```bash
# Activate virtual environment (if using)
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Quick Start

### Step 1: Generate React Diagram Data

Generate React-compatible JSON from your existing SysML JSON:

```bash
python generate_react_diagrams.py OpsCon.json --model llama3
```

This will:
- Use your existing LLM pipeline (unchanged)
- Process semantic understanding
- Split by relationships
- Calculate layouts
- Generate React-compatible JSON

Output: `react_diagrams.json`

### Step 2: Start Backend Server

In one terminal:

```bash
# Option 1: Use script
./start_backend.sh

# Option 2: Manual
cd backend
python api_server.py
```

Backend will run on: `http://localhost:5000`

### Step 3: Start Frontend

In another terminal:

```bash
# Option 1: Use script
./start_frontend.sh

# Option 2: Manual
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

### Step 4: Open Browser

Navigate to: `http://localhost:3000`

## Features

### ✅ Interactive Editing

- **Drag nodes**: Click and drag any shape to reposition
- **Rename nodes**: Double-click text to edit (or use contenteditable)
- **Fixed arrows**: Arrows automatically follow nodes (cannot be removed)
- **Real-time sync**: Changes sync across all connected clients

### ✅ High-Definition Rendering

- **Vector graphics**: SVG-based, scales perfectly
- **Retina-ready**: Crisp on high-DPI displays
- **Professional quality**: Gradients, shadows, precise positioning

### ✅ Real-Time Collaboration

- **WebSocket support**: Multiple users can edit simultaneously
- **Bi-directional updates**: Frontend ↔ Backend ↔ Frontend
- **State persistence**: Changes saved to JSON files

## Integration with Existing Pipeline

The React renderer **does not modify** your existing pipeline. It works alongside it:

```python
# Your existing code (unchanged)
from visualize_sysml import (
    SemanticModelProcessor,
    RelationshipSplitter,
    GraphLayoutEngine
)

# New React renderer (adds to pipeline)
from react_renderer import ReactRenderer

# Use existing pipeline
processor = SemanticModelProcessor()
enriched = processor.process(json_data)
splitter = RelationshipSplitter()
sub_models = splitter.split_by_relationships(enriched)
layout_engine = GraphLayoutEngine()
for sub_model in sub_models:
    sub_model['layout'] = layout_engine.calculate_layout(sub_model)

# Add React rendering (NEW)
react_renderer = ReactRenderer()
react_data = react_renderer.render(sub_models, system_name)
react_renderer.save(react_data, 'react_diagrams.json')
```

## File Structure

```
Visualproj/
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   └── InteractiveDiagram.jsx
│   │   ├── services/
│   │   │   ├── apiClient.js
│   │   │   └── websocketClient.js
│   │   ├── utils/
│   │   │   ├── d3Renderer.js
│   │   │   └── diagramDataAdapter.js
│   │   └── App.jsx
│   └── package.json
│
├── backend/                     # Flask backend
│   ├── api_server.py
│   ├── state_manager.py
│   └── requirements.txt
│
├── react_renderer.py            # React renderer (NEW)
├── generate_react_diagrams.py   # Integration script (NEW)
│
└── [Existing files - UNCHANGED]
    ├── visualize_sysml.py
    ├── llm_service.py
    └── ...
```

## API Endpoints

### REST API

- `GET /api/diagrams` - List all available diagrams
- `GET /api/diagram/<id>` - Get diagram data
- `POST /api/diagram/<id>` - Update diagram state
- `GET /api/health` - Health check

### WebSocket Events

- `connect` - Client connects to diagram room
- `node_update` - Node drag/rename update
- `diagram_update` - Full diagram update
- `disconnect` - Client disconnects

## Troubleshooting

### Backend won't start

```bash
# Check if port 5000 is in use
lsof -i :5000

# Install missing dependencies
pip install -r backend/requirements.txt
```

### Frontend won't start

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### WebSocket connection fails

- Ensure backend is running on port 5000
- Check CORS settings in `backend/api_server.py`
- Verify firewall settings

### Diagrams not loading

- Check browser console for errors
- Verify JSON file exists and is valid
- Ensure backend API is accessible

## Development

### Making Changes

1. **Frontend changes**: Edit files in `frontend/src/`
2. **Backend changes**: Edit `backend/api_server.py`
3. **Rendering changes**: Edit `react_renderer.py`

### Testing

```bash
# Test backend
curl http://localhost:5000/api/health

# Test frontend
# Open http://localhost:3000 in browser
```

## Production Deployment

For production:

1. **Build frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Serve static files**: Use nginx or serve `frontend/dist/`

3. **Backend**: Use gunicorn or uWSGI:
   ```bash
   gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 api_server:app
   ```

4. **Use Redis**: Replace in-memory state with Redis for scalability

## Next Steps

1. ✅ Generate React diagrams: `python generate_react_diagrams.py OpsCon.json`
2. ✅ Start backend: `./start_backend.sh`
3. ✅ Start frontend: `./start_frontend.sh`
4. ✅ Open browser: `http://localhost:3000`
5. ✅ Test dragging and renaming nodes
6. ✅ Test real-time updates (open in multiple browsers)

## Support

For issues or questions:
- Check console logs (browser and terminal)
- Verify all services are running
- Check network tab for API/WebSocket errors

