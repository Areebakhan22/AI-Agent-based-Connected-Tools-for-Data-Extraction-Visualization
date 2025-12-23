# Quick Start: React + D3.js Interactive Diagrams

## 🚀 3-Step Setup

### 1. Generate Diagram Data

```bash
python generate_react_diagrams.py OpsCon.json --model llama3
```

### 2. Start Backend

```bash
./start_backend.sh
# Or: cd backend && python api_server.py
```

### 3. Start Frontend

```bash
./start_frontend.sh
# Or: cd frontend && npm install && npm run dev
```

### 4. Open Browser

Navigate to: **http://localhost:3000**

## ✨ Features

- **Drag nodes**: Click and drag any shape
- **Rename nodes**: Double-click text to edit
- **Fixed arrows**: Automatically follow nodes (cannot be removed)
- **Real-time sync**: Changes sync across all clients
- **HD rendering**: Vector graphics, perfect scaling

## 📁 File Structure

```
frontend/          # React app
backend/           # Flask API server
react_renderer.py  # Integration with existing pipeline
```

## 🔧 Troubleshooting

**Backend won't start?**
```bash
pip install -r backend/requirements.txt
```

**Frontend won't start?**
```bash
cd frontend && npm install
```

**WebSocket errors?**
- Ensure backend is running on port 5000
- Check browser console for errors

## 📖 Full Documentation

See `REACT_DIAGRAM_SETUP.md` for complete guide.

