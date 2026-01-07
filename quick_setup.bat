@echo off
REM Quick Setup Script for Visualproj (Windows)
REM This script automates the setup process

echo ==========================================
echo 🚀 Visualproj Quick Setup
echo ==========================================
echo.

REM Check Python
echo 📋 Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+ first.
    pause
    exit /b 1
)
python --version
echo.

REM Check Node.js
echo 📋 Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 16+ first.
    pause
    exit /b 1
)
node --version
echo.

REM Step 1: Create virtual environment
echo 📦 Step 1: Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ⚠ Virtual environment already exists
)
echo.

REM Step 2: Activate and install Python dependencies
echo 📦 Step 2: Installing Python dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt
echo ✓ Python dependencies installed
echo.

REM Step 3: Install additional packages
echo 📦 Step 3: Installing additional packages...
pip install google-genai pillow requests 2>nul
echo ✓ Additional packages installed
echo.

REM Step 4: Frontend setup
echo 📦 Step 4: Setting up frontend...
cd frontend
if not exist "node_modules" (
    echo Installing Node.js dependencies (this may take a few minutes)...
    call npm install
    echo ✓ Frontend dependencies installed
) else (
    echo ⚠ Frontend dependencies already installed
)
cd ..
echo.

REM Step 5: Create necessary directories
echo 📁 Step 5: Creating directories...
if not exist "generated_images" mkdir generated_images
if not exist "frontend\public\generated_images" mkdir frontend\public\generated_images
echo ✓ Directories created
echo.

REM Summary
echo ==========================================
echo ✅ Setup Complete!
echo ==========================================
echo.
echo 📋 Next Steps:
echo.
echo 1. Generate images (if you have pipeline_output.json):
echo    venv\Scripts\activate
echo    python gemini_image_generator.py frontend\public\pipeline_output.json
echo.
echo 2. Copy files to frontend:
echo    python copy_images_to_frontend.py
echo.
echo 3. Start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open browser:
echo    http://localhost:3000
echo.
echo 📚 For detailed instructions, see: COMPLETE_SETUP_GUIDE.md
echo.
pause

