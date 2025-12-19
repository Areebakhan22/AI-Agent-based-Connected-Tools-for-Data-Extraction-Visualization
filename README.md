# SysML to Google Slides Converter

This project implements **Milestone 1** of an AI automation system that converts SysML v2 style files into visual Google Slides presentations.

## Overview

The tool reads a local SysML file, extracts:
- **Parts**: System components (rendered as rectangles)
- **Connections**: Relationships between parts (rendered as arrows)

And automatically generates a Google Slides presentation with the visualization.

## Features

- ✅ **LLM-based parsing** - Uses Ollama (local LLM) for semantic understanding of SysML
- ✅ Parse SysML v2 style files with AI-driven extraction
- ✅ Extract `part` definitions and `connect` relationships
- ✅ Generate Google Slides with shapes and connectors
- ✅ Hierarchical layout for better visualization
- ✅ Fallback to regex parser if LLM unavailable
- ✅ Modular, beginner-friendly code structure

## Prerequisites

- Python 3.7 or higher
- Google account with access to Google Slides API
- **Ollama** (for LLM-based parsing) - See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for setup
- **Cursor/VS Code** with **SysIDE Modeler extension** (optional, for diagram visualization) - See [SYSIDE_SETUP.md](SYSIDE_SETUP.md) or [QUICK_INSTALL_SYSIDE.md](QUICK_INSTALL_SYSIDE.md)

## Setup

### 1. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Ollama (For LLM-based Parsing)

**📖 For detailed Ollama setup instructions, see [OLLAMA_SETUP.md](OLLAMA_SETUP.md)**

Quick setup:
1. **Install Ollama**: Visit https://ollama.ai and install for your OS
2. **Start Ollama service**: `ollama serve`
3. **Download model**: `ollama pull llama3`
4. The Python `ollama` package is already in `requirements.txt`

**Note:** You can skip this step and use `--no-llm` flag to use regex parser instead.

### 3. Google Cloud Setup (Required for Google Slides API)

**📖 For detailed step-by-step instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

Quick summary:
1. **Create a Google Cloud Project** at https://console.cloud.google.com/
2. **Enable Google Slides API** in "APIs & Services" > "Library"
3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Create OAuth client ID (Desktop app type)
   - Download and save as `credentials.json` in project root

### 4. Setup SysIDE Modeler (Optional - for Diagram Visualization)

**📖 For quick installation, see [QUICK_INSTALL_SYSIDE.md](QUICK_INSTALL_SYSIDE.md)**

**📖 For detailed instructions, see [SYSIDE_SETUP.md](SYSIDE_SETUP.md)**

Quick setup:
1. **Install Extension**: Open Cursor → `Ctrl+Shift+X` → Search "SysIDE Modeler" → Install
2. **Install Tools**: `Ctrl+Shift+P` → "SysIDE Modeler: Install SysIDE Tools" → Follow prompts
3. **Reload Window**: `Ctrl+Shift+P` → "Reload Window"
4. **Verify**: Open `.sysml` file → Check syntax highlighting → Try "SysIDE: Open Diagram" command

**Note:** SysIDE is optional. Your slides generator works independently. SysIDE provides interactive diagram visualization in Cursor.

### 5. Verify Setup

Make sure you have:
- Virtual environment activated
- Ollama installed and running (or use `--no-llm` flag)
- `credentials.json` in the project root (for Google Slides API)
- All Python dependencies installed
- (Optional) SysIDE Modeler extension installed for diagram visualization

## Usage

### Two Ways to Visualize SysML

**Option 1: Interactive Diagrams (SysIDE Modeler)**
- Open `.sysml` file in Cursor
- Use Command Palette: `SysIDE: Open Diagram`
- Interactive editing and visualization

**Option 2: Automated Slides (This Tool)**
- Generate Google Slides or PowerPoint presentations
- Command-line automation
- LLM-powered extraction

Both work with the same `.sysml` files!

### Basic Usage (Slides Generation)

**Important:** Make sure to activate the virtual environment first:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py OpsCon.sysml
```

### Using Different Models

```bash
# Use default model (llama3)
python main.py OpsCon.sysml

# Use a different Ollama model
python main.py OpsCon.sysml --model mistral

# Use regex parser (fallback, no LLM required)
python main.py OpsCon.sysml --no-llm
```

### Example SysML File Format

```sysml
package Example {
    part def ComponentA {
        doc /* Description of Component A */
    }
    
    part def ComponentB {
        doc /* Description of Component B */
    }
    
    connect ComponentA to ComponentB
}
```

## Project Structure

```
sysml-to-slides/
├── main.py              # Main entry point script
├── llm_service.py       # LLM service for Ollama integration
├── llm_parser.py        # LLM-based SysML parser (primary)
├── sysml_parser.py      # Regex-based parser (fallback)
├── slides_generator.py  # Google Slides generation logic
├── pptx_generator.py   # PowerPoint generation logic
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── OLLAMA_SETUP.md     # Ollama setup guide
├── SYSIDE_SETUP.md     # SysIDE Modeler detailed setup guide
├── QUICK_INSTALL_SYSIDE.md  # Quick SysIDE installation
├── install_syside.sh   # SysIDE installation script
├── OpsCon.sysml        # Example SysML file
└── credentials.json    # Google OAuth credentials (you need to add this)
```

## How It Works

1. **LLM-based Parsing** (`llm_parser.py` + `llm_service.py`):
   - Reads the SysML file as text
   - Sends content to Ollama (local LLM) for semantic understanding
   - LLM extracts parts, connections, hierarchy, and relationships
   - Returns structured JSON data
   - **Fallback**: Uses regex parser (`sysml_parser.py`) if LLM unavailable

2. **Generation** (`slides_generator.py`):
   - Authenticates with Google Slides API
   - Creates a new presentation
   - Calculates hierarchical layout positions for parts
   - Adds rectangle shapes for each part
   - Adds arrow connectors for each connection

3. **Orchestration** (`main.py`):
   - Coordinates the parsing and generation steps
   - Handles command-line arguments (model selection, fallback mode)
   - Provides user feedback and error handling
   - Displays extracted data in JSON format

## Output

The script will:
- Print extracted parts and connections to console
- Display structured JSON data
- Create a Google Slides presentation
- Provide a URL to view the presentation

## Limitations (Milestone 1 Scope)

- ❌ No UI - command-line only
- ❌ No cloud upload - local file processing only
- ❌ No real-time sync - one-time conversion
- ❌ No bidirectional conversion (Slides → SysML) - forward flow only
- ⚠️ Simple layout - accuracy over aesthetics

## Troubleshooting

### "credentials.json not found"
- Make sure you've downloaded OAuth credentials from Google Cloud Console
- Rename the file to exactly `credentials.json`
- Place it in the project root directory

### "File not found" error
- Check that the SysML file path is correct
- Use relative or absolute paths as needed

### Authentication issues
- Delete `token.json` and re-authenticate
- Make sure Google Slides API is enabled in your project

### Ollama/LLM issues
- **"Could not connect to Ollama"**: Make sure `ollama serve` is running
- **"Model not found"**: Run `ollama pull llama3` (or your chosen model)
- **Slow performance**: Try a smaller model like `mistral` or `phi3`
- **Want to skip LLM**: Use `--no-llm` flag to use regex parser instead

## Future Milestones

- **Milestone 2**: Detailed mapping (10-15 elements) and conversion
- **Milestone 3**: Model testing with proper script and basic UI

## License

This project is part of a freelance development contract.

