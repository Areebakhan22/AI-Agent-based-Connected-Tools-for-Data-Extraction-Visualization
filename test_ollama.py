#!/usr/bin/env python3
"""
Quick test script to verify Ollama integration.

This script tests if Ollama is properly set up and can be used.
Run this before using the main script.
"""

import sys

def test_ollama_import():
    """Test if ollama package is installed."""
    try:
        import ollama
        print("✓ Ollama package is installed")
        return True
    except ImportError:
        print("✗ Ollama package not found")
        print("  Install it with: pip install ollama")
        return False

def test_ollama_connection():
    """Test if Ollama service is running."""
    try:
        import ollama
        response = ollama.list()
        # Handle both dict and object response formats
        if hasattr(response, 'models'):
            models = [model.model for model in response.models]
        elif isinstance(response, dict):
            models = [model['name'] for model in response.get('models', [])]
        else:
            models = []
        print(f"✓ Ollama service is running")
        print(f"  Available models: {', '.join(models) if models else 'None'}")
        return True
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False

def test_model_availability(model='llama3'):
    """Test if specified model is available."""
    try:
        import ollama
        response = ollama.list()
        # Handle both dict and object response formats
        if hasattr(response, 'models'):
            available_models = [m.model for m in response.models]
        elif isinstance(response, dict):
            available_models = [m['name'] for m in response.get('models', [])]
        else:
            available_models = []
        model_found = any(model in model_name for model_name in available_models)
        
        if model_found:
            print(f"✓ Model '{model}' is available")
            return True
        else:
            print(f"✗ Model '{model}' not found")
            print(f"  Download it with: ollama pull {model}")
            return False
    except Exception as e:
        print(f"✗ Error checking model: {e}")
        return False

def test_llm_service():
    """Test if LLM service can be imported and initialized."""
    try:
        from llm_service import LLMService
        service = LLMService(model='llama3')
        print("✓ LLM service can be initialized")
        return True
    except Exception as e:
        print(f"✗ Error initializing LLM service: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Ollama Integration...")
    print("=" * 50)
    
    tests = [
        ("Ollama Package", test_ollama_import),
        ("Ollama Connection", test_ollama_connection),
        ("Model Availability", lambda: test_model_availability('llama3')),
        ("LLM Service", test_llm_service),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n[{name}]")
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 50)
    print("Summary:")
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    if all_passed:
        print("\n✓ All tests passed! Ollama is ready to use.")
        print("  You can now run: python main.py OpsCon.sysml")
        return 0
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("  See OLLAMA_SETUP.md for detailed setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

