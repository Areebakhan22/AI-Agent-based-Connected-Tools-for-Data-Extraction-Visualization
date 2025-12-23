# Troubleshooting Guide

## 404 Error on Port 5000

If you're seeing "Failed to load resource: the server responded with a status of 404 (NOT FOUND)":

### 1. Check if Backend is Running

```bash
# Check if backend process is running
ps aux | grep api_server.py

# Test backend health
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "ok", "service": "sysml-diagram-api"}
```

### 2. Common 404 Causes

**Favicon Request (Harmless)**
- Browsers automatically request `/favicon.ico`
- This is now handled and returns 204 (No Content)
- You can ignore this error

**Missing Route**
- Check browser console for the exact URL that's failing
- All API routes should start with `/api/`

### 3. Verify API Routes

Test these endpoints:

```bash
# List diagrams
curl http://localhost:5000/api/diagrams

# Get specific diagram
curl http://localhost:5000/api/diagram/full_combined

# Health check
curl http://localhost:5000/api/health
```

### 4. Restart Backend

If backend isn't running:

```bash
cd /home/bit-and-bytes/Desktop/Visualproj/backend
python3 api_server.py
```

### 5. Check Frontend Proxy

The frontend uses Vite proxy. Verify `frontend/vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true
  }
}
```

### 6. Browser Console

Check browser console (F12) for:
- Exact URL that's failing
- Network tab shows the failed request
- Error details

### 7. Common Issues

**Backend not installed:**
```bash
pip install flask flask-cors flask-socketio python-socketio eventlet
```

**Port already in use:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill <PID>
```

**CORS errors:**
- Backend should have CORS enabled (already configured)
- Check browser console for CORS errors

## Debugging Steps

1. **Check backend logs:**
   ```bash
   tail -f /tmp/backend_fixed.log
   ```

2. **Check frontend console:**
   - Open browser DevTools (F12)
   - Check Console and Network tabs

3. **Test API directly:**
   ```bash
   curl -v http://localhost:5000/api/diagrams
   ```

4. **Verify react_diagrams.json exists:**
   ```bash
   ls -la /home/bit-and-bytes/Desktop/Visualproj/react_diagrams.json
   ```

If the file doesn't exist, generate it:
```bash
python3 generate_react_diagrams.py OpsCon.json --model llama3
```

