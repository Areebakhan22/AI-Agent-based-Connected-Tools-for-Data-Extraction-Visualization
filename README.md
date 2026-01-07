# 🚀 Complete Setup Guide: Running This Project on a New Device

This guide will walk you through setting up the entire project from scratch on a new computer/device.

## 🔄 Complete Workflow Overview

The **main workflow** for this project is:

```
OpsCon.sysml (SysML file)
    ↓
[Parse with Ollama LLM] → Create pipeline_output.json
    ↓
[Extract Comments] → Add to metadata
    ↓
[Generate Images] → Individual relationships + Complete diagram
    ↓
[Frontend Display] → View all images in browser
```

**Key Points:**
- 📝 **Input:** `OpsCon.sysml` file (you'll edit this for your use case)
- 🔄 **Process:** Automated pipeline handles everything
- 🎨 **Output:** Interactive frontend with all relationship images

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Clone/Copy Project](#step-1-clonecopy-project)
3. [Step 2: Python Environment Setup](#step-2-python-environment-setup)
4. [Step 3: Install Python Dependencies](#step-3-install-python-dependencies)
5. [Step 3.5: Ollama Setup (REQUIRED for SysML Parsing)](#step-35-ollama-setup-required---parsing-sysml-files)
6. [Step 4: Configure API Keys](#step-4-configure-api-keys)
7. [Step 5: Frontend Setup](#step-5-frontend-setup)
8. [Step 6: Run Complete Pipeline](#step-6-run-complete-pipeline)
9. [Step 7: Run Frontend](#step-7-run-frontend)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.7 or higher** installed
  - Check: `python3 --version` or `python --version`
  - Download: https://www.python.org/downloads/

- **Node.js 16+ and npm** installed (for frontend)
  - Check: `node --version` and `npm --version`
  - Download: https://nodejs.org/

- **Git** (optional, for cloning) or ability to copy project files

---

## Step 1: Clone/Copy Project

### Option A: Clone from GitHub (Recommended)

```bash
git clone -b testing git@github.com:Areebakhan22/AI-Agent-based-Connected-Tools-for-Data-Extraction-Visualization.git
cd AI-Agent-based-Connected-Tools-for-Data-Extraction-Visualization
```

### Option B: Copy project folder
1. Copy the entire project folder to the new device
2. Open terminal/command prompt in the project directory

---

## Step 2: Python Environment Setup

### 2.1 Create Virtual Environment

**Linux/Mac:**
```bash
cd AI-Agent-based-Connected-Tools-for-Data-Extraction-Visualization
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
cd AI-Agent-based-Connected-Tools-for-Data-Extraction-Visualization
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### 2.2 Verify Python Version
```bash
python --version  # Should be 3.7 or higher
```

---

## Step 3: Install Python Dependencies

### 3.1 Install Core Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client` - Google Slides API
- `google-auth-httplib2` - Authentication
- `google-auth-oauthlib` - OAuth
- `google-generativeai` - Gemini API
- `ollama` - LLM integration
- `python-pptx` - PowerPoint generation

### 3.2 Install Additional Dependencies for Image Generation

```bash
pip install google-genai pillow requests
```

**Note:** The `google-genai` package is required for Vertex AI image generation.

---

## Step 3.5: Ollama Setup (REQUIRED - Parsing SysML Files)

**⚠️ IMPORTANT:** Ollama is **REQUIRED** for the main workflow. The project needs Ollama to parse your `OpsCon.sysml` file and create `pipeline_output.json`.

### Why Ollama is Required

The complete workflow is:
1. **Parse SysML file** (`OpsCon.sysml`) → Requires Ollama LLM
2. **Create JSON** (`pipeline_output.json`) → Generated automatically
3. **Extract comments** → From SysML file
4. **Generate images** → Individual + Complete diagram
5. **Display in frontend** → View everything in browser

**Ollama enables Step 1** - parsing the SysML file to understand its structure.

- ✅ **Need Ollama:** If you have a `.sysml` file and want to convert it to JSON
- ❌ **Don't Need Ollama:** If you already have `pipeline_output.json` ready

### 3.5.1 Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
- Download from: https://ollama.ai/download
- Run the installer

### 3.5.2 Start Ollama Service

Open a **new terminal window** and run:
```bash
ollama serve
```

**Keep this terminal open** - Ollama must be running while parsing SysML files.

### 3.5.3 Download a Model

In a **different terminal** (keep `ollama serve` running), download a model:

```bash
ollama pull llama3
```

This downloads ~4.7GB. First time may take 5-10 minutes.

**Alternative models:**
- `ollama pull mistral` (smaller, faster)
- `ollama pull phi3` (very small, fast)

### 3.5.4 Verify Ollama

```bash
ollama list
```

You should see your model (e.g., `llama3`) in the list.

### 3.5.5 Using Ollama to Parse SysML

**Only if you need to convert SysML to JSON:**

```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Parse SysML file to JSON
python3 llm_parser.py OpsCon.sysml --output pipeline_output.json
```

**Or use the complete pipeline:**
```bash
python3 run_complete_pipeline.py OpsCon.sysml
```

**Note:** After Ollama is set up, you'll use it in the complete pipeline to parse your SysML file.

---

## Step 4: Configure API Keys

### 4.1 Gemini API Key (Required for Image Generation)

You have **two options**:

#### Option A: Use the Provided API Key (Already in Code)

The project already has a default Gemini API key embedded:
```
AIzaSyAvqHJIbaV01HbEKgRcV-Nb9AuLLOflezU
```

This key is automatically used if you don't set an environment variable.

#### Option B: Set Your Own API Key

**Get a Gemini API Key:**
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

**Set as environment variable:**

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your-api-key-here"
```

**Or edit the code directly:**
- Open `gemini_image_generator.py`
- Find line 46: `DEFAULT_API_KEY = "..."`
- Replace with your key

### 4.2 Vertex AI Key (Required for Image Generation)

The project uses Vertex AI for image generation. The default key is already in the code:
```
AQ.Ab8RN6JeCVCM0eF4ueL0EVe_P-XWVyrpyNMX_xeY1HMJcnVcxw
```

**To use your own Vertex AI key:**

**Linux/Mac:**
```bash
export VERTEX_AI_KEY="your-vertex-ai-key-here"
```

**Windows:**
```cmd
set VERTEX_AI_KEY=your-vertex-ai-key-here
```

**Or edit the code:**
- Open `gemini_image_generator.py`
- Find line 77: `DEFAULT_VERTEX_AI_KEY = "..."`
- Replace with your key

### 4.3 Verify API Keys

Test your API keys:
```bash
python3 check_gemini_quota.py
```

This will show:
- ✅ If API keys are valid
- ⚠️  If quota is exceeded
- ⏰ Wait time if quota is exceeded

---

## Step 5: Frontend Setup

### 5.1 Navigate to Frontend Directory

```bash
cd frontend
```

### 5.2 Install Node.js Dependencies

```bash
npm install
```

This installs:
- React 18
- Vite (build tool)
- Tailwind CSS
- Bootstrap

**Note:** This may take 2-5 minutes depending on your internet speed.

### 5.3 Verify Installation

```bash
npm list --depth=0
```

You should see all packages installed successfully.

---

## Step 6: Run Complete Pipeline

This is the **main workflow** - it does everything automatically:
1. Parses `OpsCon.sysml` with Ollama LLM → Creates `pipeline_output.json`
2. Extracts comments from SysML file
3. Generates all relationship images (individual + complete diagram)
4. Copies everything to frontend
5. Starts React frontend automatically

### 6.1 Prepare Your SysML File

1. **Edit your SysML file** (`OpsCon.sysml`) with your system model
2. **Make sure Ollama is running:**
   ```bash
   # In a separate terminal, keep this running:
   ollama serve
   ```

### 6.2 Run the Complete Pipeline

**From project root directory:**

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Run the complete pipeline
python3 run_complete_pipeline.py OpsCon.sysml
```

**What this does automatically:**
- ✅ **Parse SysML** with Ollama LLM → Creates `pipeline_output.json` (overwrites if exists)
- ✅ **Extract comments** from SysML file → Adds to metadata
- ✅ **Generate individual relationship images** (using Vertex AI)
- ✅ **Generate complete diagram** (using Vertex AI)
- ✅ **Save metadata** with all relationship info and comments
- ✅ **Copy files to frontend** automatically
- ✅ **Start React frontend** automatically (opens browser)

**Expected output:**
```
======================================================================
🚀 Complete Pipeline: SysML → LLM → JSON → Gemini Images → React
======================================================================

📋 Pipeline Flow:
   1. Read SysML file (OpsCon.sysml)
   2. Parse with LLM → Create/REWRITE JSON file
   3. Extract comments from SysML file
   4. Generate individual relationship images
   5. Generate complete diagram image
   6. Copy all files to frontend
   7. Start React frontend (if enabled)

[1/6] Parsing SysML file with LLM...
  ✓ SysML parsed successfully
  Parts: 11
  Connections: 6

[2/6] Converting to relationship JSON format...
  ✓ JSON file REWRITTEN: pipeline_output.json

[3/6] Extracting comments from SysML file...
  ✓ Extracted 1 comment(s) from SysML file

[4/6] Generating images with Gemini API...
  Generating image 1/6: Provide mission detail → Verifiy mission detail
    ✓ Saved Vertex AI-generated image to: generated_images/...
  ...
  ✓ Generated 7 images

[5/6] Copying files to React frontend...
  ✓ Files copied to frontend/public

[6/6] Starting React frontend...
  ✓ React app is starting...
```

### 6.3 What Gets Generated

After running the pipeline, you'll have:
- ✅ `pipeline_output.json` - Relationship data (auto-generated from SysML)
- ✅ `relationship_images_metadata.json` - Metadata with comments and image paths
- ✅ `generated_images/*.png` - All relationship images + complete diagram
- ✅ All files copied to `frontend/public/`

---

## Step 7: Run Frontend (If Not Auto-Started)

The complete pipeline (`run_complete_pipeline.py`) automatically starts the React frontend. However, if you need to start it manually:

```bash
cd frontend
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 7.2 Open in Browser

Open your browser and navigate to:
```
http://localhost:5173
```

**Note:** Vite may use port 5173, 5174, or another port - check the terminal output.

### 7.3 What You Should See

- **Left Sidebar:**
  - About section (if SysML comments exist)
  - Relationship list with filter dropdown
  - Search bar

- **Main Area:**
  - Selected relationship image
  - Relationship details

- **Bottom:**
  - Statistics cards

---

## Troubleshooting

### Problem: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
pip install google-genai pillow requests
```

### Problem: API Quota Exceeded

**Solution:**
```bash
# Check quota status
python3 check_gemini_quota.py

# Wait for quota reset (usually 1-60 minutes)
# Then retry image generation
```

**Or:**
- Get a new API key with higher quota
- Enable billing in Google Cloud Console for higher limits

### Problem: Frontend shows "No relationships found"

**Check:**
1. Verify `frontend/public/pipeline_output.json` exists
2. Verify `frontend/public/relationship_images_metadata.json` exists
3. Check browser console (F12) for errors
4. Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)

### Problem: Images not displaying

**Check:**
1. Verify images exist: `ls frontend/public/generated_images/`
2. Verify image paths in metadata are correct
3. Check browser console for 404 errors
4. Run `copy_images_to_frontend.py` again

### Problem: About section not showing

**Solution:**
```bash
# Extract comments from SysML file
python3 extract_sysml_comments.py OpsCon.sysml frontend/public/relationship_images_metadata.json

# Copy to frontend
python3 copy_images_to_frontend.py

# Restart frontend dev server
```

### Problem: Port already in use

**Solution:**
```bash
# Find process using port 5173
lsof -ti:5173 | xargs kill -9  # Linux/Mac
# or
netstat -ano | findstr :5173  # Windows, then kill PID

# Or use different port
npm run dev -- --port 3000
```

### Problem: Node modules not installing

**Solution:**
```bash
# Clear cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json  # Linux/Mac
# or
rmdir /s node_modules && del package-lock.json  # Windows

npm install
```

### Problem: "Could not connect to Ollama" error

**Solution:**
1. Make sure Ollama is installed: `ollama --version`
2. Start Ollama service: `ollama serve` (in a separate terminal)
3. Keep the `ollama serve` terminal open while parsing
4. Download a model: `ollama pull llama3`
5. Verify: `ollama list` should show your model

**Note:** If you already have JSON, you don't need Ollama at all!

---

## Quick Reference Commands

### Setup (One-time)
```bash
# Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install google-genai pillow requests

# Ollama (REQUIRED)
ollama serve  # Keep running in separate terminal
ollama pull llama3

# Frontend
cd frontend
npm install
cd ..
```

### Daily Usage (Complete Workflow)
```bash
# 1. Start Ollama (if not already running)
#    In separate terminal:
ollama serve

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac

# 3. Edit your SysML file
#    Edit OpsCon.sysml with your changes

# 4. Run complete pipeline (does everything automatically)
python3 run_complete_pipeline.py OpsCon.sysml

# 5. Start frontend (if not auto-started)
cd frontend
npm run dev
```

**That's it!** The complete pipeline handles:
- ✅ Parsing SysML → Creating JSON
- ✅ Extracting comments
- ✅ Generating all images
- ✅ Copying to frontend

### Check Status
```bash
# Check API quota
python3 check_gemini_quota.py

# Verify files
ls frontend/public/generated_images/*.png | wc -l  # Count images
ls frontend/public/*.json  # Verify JSON files
```

---

## File Structure Overview

```
Visualproj/
├── venv/                          # Python virtual environment
├── frontend/
│   ├── public/
│   │   ├── pipeline_output.json          # Input JSON (relationships)
│   │   ├── relationship_images_metadata.json  # Metadata (with images info)
│   │   └── generated_images/             # Generated images
│   ├── src/
│   │   ├── App.jsx                       # Main React app
│   │   └── components/
│   │       ├── RelationshipViewer.jsx    # Main viewer component
│   │       └── AboutSection.jsx          # About section component
│   └── package.json                      # Node.js dependencies
├── generated_images/                     # Python-generated images
├── gemini_image_generator.py             # Main image generator
├── check_gemini_quota.py                 # API quota checker
├── copy_images_to_frontend.py            # Copy utility
├── extract_sysml_comments.py             # Extract SysML comments
├── requirements.txt                      # Python dependencies
└── OpsCon.sysml                         # Sample SysML file
```

---

## API Key Quotas

### Free Tier Limits (Gemini API)

| Resource | Limit |
|----------|-------|
| Requests per minute | 15 |
| Requests per day | 1,500 |
| Images per day | 500 (with Vertex AI) |

**Note:** Quotas reset:
- Per-minute: Every 60 seconds
- Daily: At midnight Pacific Time

### Monitoring Quota

```bash
python3 check_gemini_quota.py
```

---

## Next Steps After Setup

1. **Test with sample data:**
   ```bash
   python3 gemini_image_generator.py frontend/public/pipeline_output.json
   cd frontend && npm run dev
   ```

2. **Use your own SysML file:**
   - Create/edit `pipeline_output.json` with your relationships
   - Run image generator
   - View in frontend

3. **Customize:**
   - Edit `frontend/src/components/RelationshipViewer.jsx` for UI changes
   - Edit `gemini_image_generator.py` for image generation logic

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Verify all prerequisites are installed
3. Check browser console (F12) for frontend errors
4. Check terminal output for Python errors
5. Verify API keys are correct and have quota

---

## Summary Checklist

- [ ] Python 3.7+ installed
- [ ] Node.js 16+ installed
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Additional packages installed (`google-genai pillow requests`)
- [ ] **Ollama installed and model downloaded** (`ollama pull llama3`)
- [ ] Frontend dependencies installed (`npm install` in frontend/)
- [ ] API keys configured (or using defaults)
- [ ] **Ollama service running** (`ollama serve` in separate terminal)
- [ ] **SysML file ready** (`OpsCon.sysml` edited with your model)
- [ ] **Complete pipeline run** (`python3 run_complete_pipeline.py OpsCon.sysml`)
- [ ] Frontend running (`npm run dev` in frontend/ - or auto-started by pipeline)
- [ ] Browser opened to http://localhost:3000 (or port shown)

**Once all checked, you're ready to use the project! 🎉**

---

## Complete Workflow Summary

```
1. Edit OpsCon.sysml (your SysML file)
   ↓
2. Run: python3 run_complete_pipeline.py OpsCon.sysml
   ↓
3. Pipeline automatically (in order):
   - [1/6] Parses SysML with Ollama → Creates pipeline_output.json
   - [2/6] Converts to relationship JSON format
   - [3/6] Extracts comments from SysML file
   - [4/6] Generates individual relationship images + complete diagram
   - [5/6] Copies JSON, images, and metadata to frontend
   - [6/6] Starts React frontend automatically
   ↓
4. Browser opens → View all images, filters, and "About" section!
```

**That's the complete flow!** 🚀
