#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple OCR test script for PaddleOCR.
Tests if OCR can extract text from a receipt image.
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from paddleocr import PaddleOCR

def test_ocr(image_path, lang='en'):
    """Test OCR on a receipt image."""
    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found: {image_path}")
        return False
    
    print(f"Testing OCR on: {image_path}")
    print(f"Language: {lang}")
    print("Initializing PaddleOCR (this may take a moment on first run)...")
    
    try:
        # Initialize PaddleOCR
        # Map common language names to codes
        lang_map = {
            'greek': 'el',
            'el': 'el',
            'english': 'en',
            'en': 'en'
        }
        lang_code = lang_map.get(lang.lower(), lang)
        
        # Try the specified language, fall back to English if not available
        try:
            ocr = PaddleOCR(lang=lang_code)
            print(f"PaddleOCR initialized with language: {lang_code}")
        except ValueError as e:
            if lang_code != 'en':
                print(f"WARNING: Language '{lang_code}' not available, trying English instead...")
                ocr = PaddleOCR(lang='en')
                print("PaddleOCR initialized with language: en (English)")
            else:
                raise
        
        print("Processing image...")
        
        # Perform OCR (use predict method for newer PaddleOCR versions)
        try:
            result = ocr.predict(image_path)
        except AttributeError:
            # Fallback to older API
            result = ocr.ocr(image_path)
        
        if not result:
            print("WARNING: No result returned")
            return False
        
        # Handle new PaddleOCR v3.x format (dictionary)
        text_lines = []
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            page_result = result[0]
            rec_texts = page_result.get('rec_texts', [])
            rec_scores = page_result.get('rec_scores', [])
            
            if not rec_texts:
                print("WARNING: No text detected in image")
                return False
            
            for i, text in enumerate(rec_texts):
                confidence = rec_scores[i] if i < len(rec_scores) else 1.0
                if text:
                    text_lines.append(text)
                    print(f"  [{confidence:.2f}] {text}")
        
        # Handle old PaddleOCR format (nested lists)
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            if not result[0]:
                print("WARNING: No text detected in image")
                return False
            
            for line in result[0]:
                if line:
                    if isinstance(line, (list, tuple)) and len(line) >= 2:
                        if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                            text = line[1][0]
                            confidence = line[1][1]
                        else:
                            text = str(line[1])
                            confidence = 1.0
                    else:
                        text = str(line)
                        confidence = 1.0
                    
                    if text:
                        text_lines.append(text)
                        print(f"  [{confidence:.2f}] {text}")
        else:
            print(f"WARNING: Unexpected result format: {type(result)}")
            return False
        
        print("\n" + "="*60)
        print("FULL TEXT (concatenated):")
        print("="*60)
        full_text = "\n".join(text_lines)
        print(full_text)
        
        print(f"\nExtracted {len(text_lines)} lines of text")
        print("\nOCR test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR: OCR test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <path_to_receipt_image> [language]")
        print("\nLanguages: en (English), ch (Chinese), or try: grc, el, greek")
        print("\nExample:")
        print("  python test_ocr.py C:\\Users\\thano\\Desktop\\receipt.jpg")
        print("  python test_ocr.py receipt.jpg en")
        sys.exit(1)
    
    image_path = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'en'
    success = test_ocr(image_path, lang)
    sys.exit(0 if success else 1)
