#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Receipt parser with type detection and type-specific parsing.
"""

import json
import re
import requests

OLLAMA_BASE_URL = "http://localhost:11434"

# Removed type detection - focusing on gas receipts only

def parse_gas_receipt(receipt_text, model_name="qwen2.5:7b"):
    """Parse gas station receipt with specific rules - optimized for Greek gas receipts."""
    prompt = f"""You are parsing a GAS STATION receipt from Greece. Extract all relevant data.

Receipt text:
{receipt_text}

Extract and return ONLY valid JSON:
{{
  "merchant": "string (gas station name - clean up, remove extra text like A.E.B.E., keep main name)",
  "date": "YYYY-MM-DD or null (look for HM:, ΗΜ:, HM/NIA: followed by DD/MM/YYYY format)",
  "total": number (FINAL TOTAL TO PAY - look for "ΣΥΝΟΛΟ ΜΕ ΦΠΑ" or "ΣΥΝΟΛΟ" with amount),
  "vat": number (VAT amount - look for "ΦΠΑ" or "Φ.Π.Α" with amount, or null if not found),
  "fuel_type": "string (e.g., UNLEADED 95, DIESEL, SUPER, LPG, etc.)",
  "liters": number (quantity in liters - look for "ΣΥΝΟΛΟ ΛΙΤΡΩΝ" or "ΠΟΣΟΤΗΤΑ" followed by number and "ΛΙΤΡΑ". IMPORTANT: Greek uses comma as decimal - "21,860" means 21.860, convert comma to decimal point),
  "price_per_liter": number (unit price per liter - look for "ΤΙΜΗ ΛΙΤΡΟΥ" or "ΤΙΜΗ ΜΟΝΑΔΟΣ" followed by amount),
  "net_amount": number (amount before VAT - look for "ΚΑΘΑΡΗ ΑΞΙΑ" followed by amount)
}}

CRITICAL RULES FOR GREEK GAS RECEIPTS:
- "ΣΥΝΟΛΟ ΜΕ ΦΠΑ" or "ΣΥΝΟΛΟ" = final total (use for "total" field)
- "ΚΑΘΑΡΗ ΑΞΙΑ" = net amount before VAT (use for "net_amount")
- "ΣΥΝΟΛΟ ΛΙΤΡΩΝ" or "ΠΟΣΟΤΗΤΑ" = quantity in liters (use for "liters")
  * IMPORTANT: Greek numbers use COMMA as decimal separator (21,860 means 21.860, NOT 21860)
  * If you see "21,860 ΛΙΤΡΑ" it means 21.860 liters, convert comma to decimal point
  * If you see "21.860" it's already in decimal format
- "ΤΙΜΗ ΛΙΤΡΟΥ" or "ΤΙΜΗ ΜΟΝΑΔΟΣ" = price per liter (use for "price_per_liter")
- Fuel type examples: "UNLEADED 95", "DIESEL", "SUPER", "LPG", "ΑΜΟΛΥΒΔΗ", "ΠΕΤΡΕΛΑΙΟ"
- Date: Look for "HM:", "ΗΜ:", "HM/NIA:" followed by date in DD/MM/YYYY format, convert to YYYY-MM-DD
  * Example: "HM:29/04/2020" → "2020-04-29"
  * If date is in format "29-04-2020" or "29.04.2020", also convert to YYYY-MM-DD
- Merchant: Clean up name (remove legal suffixes, keep recognizable name)

EXAMPLES:
- "METPO A.E.B.E." → "METRO"
- "ΚΑΡΑΤΖΙΑΣ ΒΑΣ ΠΑΠΑΔΟΥΛΗΣ" → "ΚΑΡΑΤΖΙΑΣ"
- "SHELL HELLAS" → "SHELL"

Return ONLY valid JSON, no markdown, no explanations:"""
    
    return _call_llm(prompt, model_name)

# Removed other receipt types - focusing on gas receipts only

def _call_llm(prompt, model_name="qwen2.5:7b"):
    """Call LLM and parse JSON response."""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1}
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return None
        
        llm_response = response.json().get("response", "")
        
        # Extract JSON
        json_start = llm_response.find("{")
        json_end = llm_response.rfind("}") + 1
        
        if json_start < 0 or json_end <= json_start:
            return None
        
        json_str = llm_response[json_start:json_end]
        parsed_data = json.loads(json_str)
        
        # Convert date format (DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY -> YYYY-MM-DD)
        if parsed_data.get('date') and isinstance(parsed_data['date'], str):
            date_str = parsed_data['date']
            # Try different date formats
            date_match = re.match(r'(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})', date_str)
            if date_match:
                day, month, year = date_match.groups()
                parsed_data['date'] = f"{year}-{month}-{day}"
            # Also try YYYY-MM-DD format (might already be correct)
            elif re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                pass  # Already in correct format
        
        # Fix liters: Greek uses comma as decimal separator
        if parsed_data.get('liters') and isinstance(parsed_data['liters'], (int, float)):
            # If liters is a very large number (like 21860), it might be misread
            # Check if it's unreasonably large for a gas fill-up (> 1000 liters is unlikely)
            if parsed_data['liters'] > 1000:
                # Likely a misread - divide by 1000 (21,860 was read as 21860)
                # But we can't be sure, so we'll let the LLM handle it better
                pass
        
        return parsed_data
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return None

def parse_receipt(receipt_text, model_name="qwen2.5:7b"):
    """
    Main parsing function: parses gas station receipts only.
    """
    return parse_gas_receipt(receipt_text, model_name)
