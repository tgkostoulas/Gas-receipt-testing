#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Flask backend for receipt OCR and LLM processing.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from paddleocr import PaddleOCR
from receipt_parser import parse_receipt
from station_finder import find_gas_station
from ocr_postprocess import postprocess_ocr_text

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
OLLAMA_BASE_URL = "http://localhost:11434"

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize OCR (lazy loading - will be initialized on first use)
ocr = None

def get_ocr():
    """Lazy load OCR to avoid initialization on import."""
    global ocr
    if ocr is None:
        try:
            ocr = PaddleOCR(lang='el')  # Greek
        except:
            ocr = PaddleOCR(lang='en')  # Fallback to English
    return ocr

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ocr_extract(image_path):
    """Extract text from receipt image using OCR."""
    try:
        ocr_instance = get_ocr()
        result = ocr_instance.predict(image_path)
        
        if not result:
            return None
        
        # Handle new PaddleOCR v3.x format (dictionary)
        text_lines = []
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            page_result = result[0]
            rec_texts = page_result.get('rec_texts', [])
            text_lines = [text for text in rec_texts if text]
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            for line in result[0]:
                if line and isinstance(line, (list, tuple)) and len(line) >= 2:
                    if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                        text_lines.append(line[1][0])
                    else:
                        text_lines.append(str(line[1]))
        
        if not text_lines:
            return None
        
        # Post-process OCR text to fix common errors (e.g., Λ -> Α)
        text_lines = postprocess_ocr_text(text_lines)
        
        return "\n".join(text_lines)
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None

# LLM parsing is now handled by receipt_parser.py

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})

@app.route('/api/process-receipt', methods=['POST'])
def process_receipt():
    """Process receipt image: OCR + LLM parsing."""
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Step 1: OCR
        ocr_text = ocr_extract(filepath)
        if not ocr_text:
            return jsonify({"error": "OCR failed to extract text"}), 500
        
        # Step 2: LLM Parsing (gas receipts only)
        parsed_data = parse_receipt(ocr_text)
        if not parsed_data:
            return jsonify({"error": "LLM parsing failed"}), 500
        
        # Step 3: Find gas station location (if API key is set)
        station_info = None
        if parsed_data.get('merchant'):
            # Auto-enable if API key is set
            api_key = os.getenv('GOOGLE_PLACES_API_KEY', '')
            if api_key:
                # Pass price from receipt if available
                receipt_price = parsed_data.get('price_per_liter')
                station_info = find_gas_station(
                    parsed_data['merchant'],
                    receipt_price=receipt_price
                )
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "ocr_text": ocr_text,
            "parsed_data": parsed_data,
            "station_info": station_info  # None if API key not set or not found
        })
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting receipt processing server...")
    print("Make sure Ollama is running on http://localhost:11434")
    app.run(debug=True, port=5000, host='0.0.0.0')
