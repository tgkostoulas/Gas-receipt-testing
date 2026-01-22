#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined OCR + LLM pipeline test.
Tests the full flow: Image → OCR → LLM Parsing → Structured Data
"""

import sys
import os
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from paddleocr import PaddleOCR

# Add backend to path to import receipt_parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from receipt_parser import parse_receipt
from ocr_postprocess import postprocess_ocr_text

def ocr_extract(image_path):
    """Extract text from receipt image using OCR."""
    print(f"Step 1: Extracting text from image...")
    
    try:
        # Try Greek first, fallback to English
        try:
            ocr = PaddleOCR(lang='el')  # Greek
            print("Using Greek language model")
        except:
            ocr = PaddleOCR(lang='en')  # Fallback to English
            print("Using English language model (Greek not available)")
        result = ocr.predict(image_path)
        
        if not result:
            print("ERROR: No result returned")
            return None
        
        # Handle new PaddleOCR v3.x format (dictionary)
        text_lines = []
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            page_result = result[0]
            rec_texts = page_result.get('rec_texts', [])
            text_lines = [text for text in rec_texts if text]
        # Handle old format
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            for line in result[0]:
                if line and isinstance(line, (list, tuple)) and len(line) >= 2:
                    if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                        text_lines.append(line[1][0])
                    else:
                        text_lines.append(str(line[1]))
        
        if not text_lines:
            print("ERROR: No text detected in image")
            return None
        
        # Post-process OCR text to fix common errors (e.g., Λ -> Α)
        text_lines = postprocess_ocr_text(text_lines)
        
        full_text = "\n".join(text_lines)
        print(f"Extracted {len(text_lines)} lines of text")
        return full_text
        
    except Exception as e:
        print(f"ERROR: OCR failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def llm_parse_receipt(receipt_text, model_name="qwen2.5:7b"):
    """Parse receipt text using LLM (gas receipts only)."""
    print(f"\nStep 2: Parsing gas receipt with LLM ({model_name})...")
    return parse_receipt(receipt_text, model_name)

def test_pipeline(image_path, model_name="qwen2.5:7b"):
    """Test the full OCR → LLM pipeline."""
    print("="*60)
    print("FULL PIPELINE TEST")
    print("="*60)
    print(f"Image: {image_path}")
    print(f"Model: {model_name}\n")
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found: {image_path}")
        return False
    
    # Step 1: OCR
    receipt_text = ocr_extract(image_path)
    if not receipt_text:
        return False
    
    print("\n" + "-"*60)
    print("EXTRACTED TEXT:")
    print("-"*60)
    print(receipt_text)
    
    # Step 2: LLM Parsing
    parsed_data = llm_parse_receipt(receipt_text, model_name)
    if not parsed_data:
        return False
    
    # Step 3: Display Results
    print("\n" + "="*60)
    print("FINAL RESULT - STRUCTURED DATA:")
    print("="*60)
    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("Pipeline test completed successfully!")
    print("="*60)
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_pipeline.py <path_to_receipt_image> [model_name]")
        print("\nExample:")
        print("  python test_pipeline.py C:\\Users\\thano\\Desktop\\receipt.jpg")
        print("  python test_pipeline.py receipt.jpg qwen2.5:7b")
        sys.exit(1)
    
    image_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:7b"
    
    success = test_pipeline(image_path, model_name)
    sys.exit(0 if success else 1)
