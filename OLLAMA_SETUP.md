# Ollama Setup Guide

This guide will help you set up Ollama for LLM-based SysML parsing.

## What is Ollama?

Ollama is a tool that runs large language models (LLMs) locally on your machine. It allows you to use AI models like Llama 3, Mistral, and others without needing internet or API keys.

## Installation Steps

### Step 1: Install Ollama

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from: https://ollama.ai/download

Or visit: https://ollama.ai for installation instructions for your OS.

### Step 2: Start Ollama Service

After installation, start the Ollama service:

```bash
ollama serve
```

This will start Ollama on `http://localhost:11434`. Keep this terminal open while using the tool.

### Step 3: Download a Model

Download the Llama 3 model (recommended):

```bash
ollama pull llama3
```

This will download the model (about 4.7GB). The first time may take a few minutes.

**Alternative models you can try:**
- `ollama pull mistral` (smaller, faster)
- `ollama pull codellama` (better for code)
- `ollama pull phi3` (very small, fast)

### Step 4: Install Python Package

Install the Ollama Python package in your virtual environment:

```bash
# Activate your virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install ollama package
pip install ollama
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Step 5: Verify Installation

Test that Ollama is working:

```bash
ollama list
```

You should see `llama3` (or your chosen model) in the list.

Test the Python integration:

```python
import ollama
response = ollama.chat(model='llama3', messages=[
    {'role': 'user', 'content': 'Hello!'}
])
print(response['message']['content'])
```

## Usage

### Running with LLM (Default)

```bash
python main.py OpsCon.sysml
```

This will use Ollama with the default model (llama3).

### Using a Different Model

```bash
python main.py OpsCon.sysml --model mistral
```

### Fallback to Regex Parser

If Ollama is not available or you want to use the original regex parser:

```bash
python main.py OpsCon.sysml --no-llm
```

## Troubleshooting

### "Could not connect to Ollama"

**Solution:** Make sure Ollama service is running:
```bash
ollama serve
```

### "Model 'llama3' not found"

**Solution:** Download the model:
```bash
ollama pull llama3
```

### "Module 'ollama' not found"

**Solution:** Install the package:
```bash
pip install ollama
```

### Slow Performance

**Solutions:**
1. Use a smaller model: `--model mistral` or `--model phi3`
2. Ensure you have enough RAM (8GB+ recommended)
3. Use GPU if available (Ollama will use it automatically if detected)

### Out of Memory

**Solutions:**
1. Use a smaller model: `ollama pull phi3`
2. Close other applications
3. Increase system swap space

## Model Recommendations

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| **llama3** | ~4.7GB | Medium | High | Best balance |
| **mistral** | ~4.1GB | Fast | High | Faster processing |
| **phi3** | ~2.3GB | Very Fast | Good | Low memory systems |
| **codellama** | ~3.8GB | Medium | High | Code-focused tasks |

## Next Steps

Once Ollama is set up:

1. Test with your SysML file:
   ```bash
   python main.py OpsCon.sysml
   ```

2. Compare LLM vs Regex parsing:
   ```bash
   # LLM parsing
   python main.py OpsCon.sysml
   
   # Regex parsing
   python main.py OpsCon.sysml --no-llm
   ```

3. The LLM approach should provide better semantic understanding and handle variations in SysML syntax better than regex.

## Additional Resources

- Ollama Documentation: https://github.com/ollama/ollama
- Available Models: https://ollama.ai/library
- Python Ollama Package: https://github.com/ollama/ollama-python

