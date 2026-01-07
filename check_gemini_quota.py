#!/usr/bin/env python3
"""
Check Gemini API Quota Status

This script checks if your Gemini API key has available quota
and which models are accessible.
"""

from google import genai
import os
import re
from datetime import datetime

def check_quota(api_key: str):
    """Check Gemini API quota status."""
    client = genai.Client(api_key=api_key)
    
    print('=' * 70)
    print('Gemini API Quota Status Check')
    print('=' * 70)
    print(f'API Key: {api_key[:20]}...{api_key[-10:]}')
    print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print()
    
    # Test 1: Basic API access
    print('Test 1: Basic API Access (Text Generation)')
    print('-' * 70)
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='Hello'
        )
        print('✓ API key is valid')
        print('✓ Text generation quota: Available')
    except Exception as e:
        error_str = str(e)
        if '429' in error_str or 'quota' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
            print('✗ QUOTA EXCEEDED')
            print(f'  Error: {str(e)[:200]}')
            
            # Extract retry delay
            retry_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
            if retry_match:
                wait_seconds = float(retry_match.group(1))
                print(f'  ⏰ Wait time: {wait_seconds:.0f} seconds ({wait_seconds/60:.1f} minutes)')
                print(f'  ⏰ Retry after: {(datetime.now().timestamp() + wait_seconds):.0f}')
        elif '401' in error_str:
            print('✗ AUTHENTICATION ERROR - Invalid API key')
        else:
            print(f'✗ Error: {str(e)[:200]}')
    
    print()
    
    # Test 2: Image generation models
    print('Test 2: Image Generation Models')
    print('-' * 70)
    
    models_to_test = [
        ('imagen-4.0-generate-001', 'Imagen 4.0'),
        ('gemini-2.5-flash-image', 'Gemini 2.5 Flash Image'),
        ('gemini-2.5-flash-image-preview', 'Gemini 2.5 Flash Image Preview'),
        ('gemini-2.0-flash-exp-image-generation', 'Gemini 2.0 Flash Exp Image'),
    ]
    
    results = {}
    for model, name in models_to_test:
        print(f'Testing {name} ({model})...', end=' ')
        try:
            from google.genai import types
            if 'imagen' in model.lower():
                response = client.models.generate_images(
                    model=model,
                    prompt='A simple test',
                    config=types.GenerateImagesConfig(number_of_images=1)
                )
            else:
                response = client.models.generate_content(
                    model=model,
                    contents='Generate a simple diagram',
                    config=types.GenerateContentConfig()
                )
            print('✓ Available')
            results[model] = 'available'
        except Exception as e:
            error_str = str(e)
            if '429' in error_str or 'quota' in error_str.lower() or 'RESOURCE_EXHAUSTED' in error_str:
                print('✗ QUOTA EXCEEDED')
                retry_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                if retry_match:
                    wait_seconds = float(retry_match.group(1))
                    print(f'    Wait: {wait_seconds:.0f}s ({wait_seconds/60:.1f}m)')
                results[model] = 'quota_exceeded'
            elif '400' in error_str and 'billed' in error_str.lower():
                print('✗ BILLING REQUIRED')
                results[model] = 'billing_required'
            elif '404' in error_str:
                print('✗ MODEL NOT FOUND')
                results[model] = 'not_found'
            else:
                print(f'✗ {str(e)[:50]}')
                results[model] = 'error'
    
    print()
    print('=' * 70)
    print('Summary')
    print('=' * 70)
    
    available = [m for m, s in results.items() if s == 'available']
    quota_exceeded = [m for m, s in results.items() if s == 'quota_exceeded']
    billing_required = [m for m, s in results.items() if s == 'billing_required']
    
    if available:
        print(f'✓ Available models: {len(available)}')
        for m in available:
            print(f'  - {m}')
    
    if quota_exceeded:
        print(f'\n⚠️  Quota exceeded models: {len(quota_exceeded)}')
        for m in quota_exceeded:
            print(f'  - {m}')
        print('\n💡 Solution: Wait for quota reset or enable billing')
    
    if billing_required:
        print(f'\n⚠️  Billing required models: {len(billing_required)}')
        for m in billing_required:
            print(f'  - {m}')
        print('\n💡 Solution: Enable billing in Google Cloud Console')
    
    print()
    print('=' * 70)


if __name__ == '__main__':
    import sys
    
    # Get API key from command line or use default
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyAvqHJIbaV01HbEKgRcV-Nb9AuLLOflezU'
    
    check_quota(api_key)

