#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR post-processing to fix common misreadings, especially for Greek text.
"""

def fix_greek_ocr_errors(text):
    """
    Fix common OCR errors in Greek text.
    Especially fixes Λ (lambda) being read as Α (alpha).
    """
    if not text:
        return text
    
    # Common Greek OCR errors
    replacements = {
        # Lambda (Λ) misreadings - context-dependent
        # "ΣΥΝΟΛΟ ΑΙΤΡΩΝ" -> "ΣΥΝΟΛΟ ΛΙΤΡΩΝ" (liters)
        'ΣΥΝΟΛΟ ΑΙΤΡΩΝ': 'ΣΥΝΟΛΟ ΛΙΤΡΩΝ',
        'ΣΥΝΟΛΟ ΑΙΤΡΑ': 'ΣΥΝΟΛΟ ΛΙΤΡΑ',
        'ΠΟΣΟΤΗΤΑ ΑΙΤΡΩΝ': 'ΠΟΣΟΤΗΤΑ ΛΙΤΡΩΝ',
        'ΠΟΣΟΤΗΤΑ ΑΙΤΡΑ': 'ΠΟΣΟΤΗΤΑ ΛΙΤΡΑ',
        # "ΤΙΜΗ ΑΙΤΡΟΥ" -> "ΤΙΜΗ ΛΙΤΡΟΥ" (price per liter)
        'ΤΙΜΗ ΑΙΤΡΟΥ': 'ΤΙΜΗ ΛΙΤΡΟΥ',
        'ΤΙΜΗ ΜΟΝΑΔΟΣ ΑΙΤΡΟΥ': 'ΤΙΜΗ ΜΟΝΑΔΟΣ ΛΙΤΡΟΥ',
        # More general: "ΑΙΤΡ" -> "ΛΙΤΡ" when followed by certain patterns
        ' ΑΙΤΡΩΝ': ' ΛΙΤΡΩΝ',
        ' ΑΙΤΡΑ': ' ΛΙΤΡΑ',
        ' ΑΙΤΡΟΥ': ' ΛΙΤΡΟΥ',
        ' ΑΙΤΡΟ': ' ΛΙΤΡΟ',
    }
    
    # Apply replacements
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # More aggressive: if we see "ΑΙΤΡ" in context of quantities/prices, replace with "ΛΙΤΡ"
    # But be careful - only in specific contexts
    import re
    # Pattern: number followed by "ΑΙΤΡ" (likely should be "ΛΙΤΡ")
    text = re.sub(r'(\d+[.,]\d+)\s*ΑΙΤΡ', r'\1 ΛΙΤΡ', text)
    text = re.sub(r'(\d+[.,]\d+)\s*ΑΙΤΡΩΝ', r'\1 ΛΙΤΡΩΝ', text)
    text = re.sub(r'(\d+[.,]\d+)\s*ΑΙΤΡΑ', r'\1 ΛΙΤΡΑ', text)
    
    return text

def postprocess_ocr_text(text_lines):
    """
    Post-process OCR extracted text lines to fix common errors.
    """
    if not text_lines:
        return text_lines
    
    processed = []
    for line in text_lines:
        if line:
            fixed = fix_greek_ocr_errors(line)
            processed.append(fixed)
        else:
            processed.append(line)
    
    return processed
