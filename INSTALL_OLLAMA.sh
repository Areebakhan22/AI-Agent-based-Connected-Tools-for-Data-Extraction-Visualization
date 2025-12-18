#!/bin/bash
# Quick Ollama Installation Script for Linux

echo "Installing Ollama..."
echo "==================="

# Check if already installed
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed!"
    ollama --version
    exit 0
fi

# Install Ollama
echo "Downloading and installing Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

# Check installation
if command -v ollama &> /dev/null; then
    echo "✓ Ollama installed successfully!"
    
    # Start Ollama service in background
    echo "Starting Ollama service..."
    ollama serve &
    
    # Wait a moment for service to start
    sleep 2
    
    # Download llama3 model
    echo "Downloading llama3 model (this may take a few minutes)..."
    ollama pull llama3
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "To use Ollama:"
    echo "  1. Start service: ollama serve"
    echo "  2. Test: python test_ollama.py"
    echo "  3. Run: python main.py OpsCon.sysml"
else
    echo "✗ Installation failed. Please install manually:"
    echo "  Visit: https://ollama.ai"
fi

