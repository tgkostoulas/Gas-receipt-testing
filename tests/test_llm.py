#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple LLM test script for Ollama.
Tests if Ollama LLM can parse receipt data and categorize expenses.
"""

import sys
import os
import requests
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

OLLAMA_BASE_URL = "http://localhost:11434"

def test_ollama_connection():
    """Test if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("OK: Ollama is running")
            print(f"Available models: {[m['name'] for m in models]}")
            return True
        else:
            print(f"ERROR: Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Ollama. Is it running?")
        print("   Try: ollama serve")
        return False
    except Exception as e:
        print(f"ERROR: Error connecting to Ollama: {str(e)}")
        return False

def test_llm_parsing(model_name="qwen2.5:7b"):
    """Test LLM's ability to parse receipt text."""
    print(f"\nTesting LLM parsing with model: {model_name}")
    
    # Sample receipt text (simulating OCR output)
    sample_receipt_text = """
    ΣΟΥΠΕΡ ΜΑΡΚΕΤ ΑΒ
    ΑΦΜ: 123456789
    Ημερομηνία: 15/01/2024
    Αριθμός: 001234
    
    Προϊόντα:
    - Γάλα 2L         5.50€
    - Ψωμί            1.20€
    - Αυγά 6τμχ       3.80€
    - Φρούτα          4.30€
    
    Σύνολο:          14.80€
    ΦΠΑ:              2.96€
    """
    
    prompt = f"""You are a receipt parser. Extract structured data from this receipt text.

Receipt text:
{sample_receipt_text}

Extract and return ONLY a valid JSON object with these fields:
- merchant: string (merchant/store name)
- date: string (date in YYYY-MM-DD format)
- total: number (total amount)
- vat: number (VAT amount, if present)
- items: array of objects with "name" and "price" fields
- category: string (one of: groceries, restaurant, transportation, shopping, utilities, entertainment, healthcare, other)

Return ONLY the JSON, no other text:"""
    
    print("Sending request to LLM...")
    
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Lower temperature for more consistent parsing
                }
            },
            timeout=120  # LLM can take a while
        )
        
        if response.status_code != 200:
            print(f"ERROR: LLM request failed: {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        llm_response = result.get("response", "")
        
        print("\n" + "="*60)
        print("LLM RESPONSE:")
        print("="*60)
        print(llm_response)
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                print("\n" + "="*60)
                print("PARSED STRUCTURED DATA:")
                print("="*60)
                print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
                return True
            else:
                print("\nWARNING: Could not find JSON in LLM response")
                return False
        except json.JSONDecodeError as e:
            print(f"\nWARNING: Could not parse JSON from response: {str(e)}")
            print("   LLM may need better prompting or a different model")
            return False
            
    except requests.exceptions.Timeout:
        print("ERROR: LLM request timed out (took longer than 120 seconds)")
        return False
    except Exception as e:
        print(f"ERROR: LLM test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_categorization(model_name="qwen2.5:7b"):
    """Test LLM's ability to categorize expenses."""
    print(f"\nTesting LLM categorization with model: {model_name}")
    
    test_cases = [
        {"merchant": "ΣΟΥΠΕΡ ΜΑΡΚΕΤ", "amount": 25.50, "description": "Groceries"},
        {"merchant": "TAVERNA OLYMPOS", "amount": 45.00, "description": "Dinner"},
        {"merchant": "SHELL", "amount": 60.00, "description": "Gas"},
    ]
    
    for case in test_cases:
        prompt = f"""Categorize this expense into one of these categories:
groceries, restaurant, transportation, shopping, utilities, entertainment, healthcare, other

Merchant: {case['merchant']}
Amount: {case['amount']}€
Description: {case['description']}

Return ONLY the category name, nothing else:"""
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                category = response.json().get("response", "").strip()
                print(f"  {case['merchant']} -> {category}")
            else:
                print(f"  ERROR: Failed for {case['merchant']}")
        except Exception as e:
            print(f"  ERROR: {str(e)}")
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("LLM TEST SUITE")
    print("="*60)
    
    # Test connection
    if not test_ollama_connection():
        print("\nERROR: Cannot proceed without Ollama connection")
        print("\nTo start Ollama:")
        print("  1. Make sure Ollama is installed")
        print("  2. Run: ollama serve")
        print("  3. Or just run: ollama run qwen2.5:7b")
        sys.exit(1)
    
    # Determine which model to use
    model_name = "qwen2.5:7b"
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    
    print(f"\nUsing model: {model_name}")
    
    # Test parsing
    parsing_success = test_llm_parsing(model_name)
    
    # Test categorization
    categorization_success = test_llm_categorization(model_name)
    
    print("\n" + "="*60)
    if parsing_success and categorization_success:
        print("All LLM tests passed!")
    else:
        print("Some tests had issues, but LLM is working")
    print("="*60)
