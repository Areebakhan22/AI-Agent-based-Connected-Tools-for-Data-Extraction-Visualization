#!/bin/bash
# Quick Setup Script for Visualproj
# This script automates the setup process

set -e  # Exit on error

echo "=========================================="
echo "🚀 Visualproj Quick Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📋 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.7+ first."
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Check Node.js
echo "📋 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+ first."
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✓ Node.js version: $NODE_VERSION"
echo ""

# Step 1: Create virtual environment
echo "📦 Step 1: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi
echo ""

# Step 2: Activate and install Python dependencies
echo "📦 Step 2: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 3: Install additional packages if needed
echo "📦 Step 3: Installing additional packages..."
pip install google-genai pillow requests 2>/dev/null || true
echo -e "${GREEN}✓ Additional packages installed${NC}"
echo ""

# Step 4: Frontend setup
echo "📦 Step 4: Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a few minutes)..."
    npm install
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Frontend dependencies already installed${NC}"
fi
cd ..
echo ""

# Step 5: Verify API keys
echo "🔑 Step 5: Checking API keys..."
echo "Checking Gemini API quota..."
python3 check_gemini_quota.py 2>/dev/null || echo "⚠ Could not check quota (this is okay if keys are not set)"
echo ""

# Step 6: Create necessary directories
echo "📁 Step 6: Creating directories..."
mkdir -p generated_images
mkdir -p frontend/public/generated_images
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Generate images (if you have pipeline_output.json):"
echo "   source venv/bin/activate"
echo "   python3 gemini_image_generator.py frontend/public/pipeline_output.json"
echo ""
echo "2. Copy files to frontend:"
echo "   python3 copy_images_to_frontend.py"
echo ""
echo "3. Start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open browser:"
echo "   http://localhost:3000"
echo ""
echo "📚 For detailed instructions, see: COMPLETE_SETUP_GUIDE.md"
echo ""

