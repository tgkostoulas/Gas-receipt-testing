# Gas Station Tracker - Greece

A specialized fuel tracking application for Greek gas stations. Upload gas receipts to automatically extract data, find station locations, and track fuel consumption.

## Features

- ⛽ **Gas Receipt OCR**: Automatic text extraction from Greek gas station receipts
- 🤖 **AI Parsing**: Extract merchant, date, fuel type, liters, price per liter, total, VAT
- 🗺️ **Station Location**: Automatically find gas station location using Google Places API
- 📊 **Price Tracking**: Track prices from your receipts
- 🌐 **Web Interface**: Simple browser-based UI for uploading and viewing receipts

## Prerequisites

- **Python 3.12** (required for PaddleOCR compatibility)
- **Node.js 18+** (for web frontend)
- **Ollama** (for local LLM processing)
- **Google Places API Key** (optional, for station location lookup)

## Installation

### Windows

1. **Install Python 3.12**
   - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: `python --version` (should show 3.12.x)

2. **Install Node.js**
   - Download from https://nodejs.org/
   - Verify: `node --version`

3. **Install Ollama**
   - Download from https://ollama.ai/download
   - Install and start Ollama
   - Pull the model: `ollama pull qwen2.5:7b`

4. **Enable Windows Long Path Support** (required for PaddleOCR)
   - Open Registry Editor (regedit)
   - Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
   - Set `LongPathsEnabled` to `1`
   - Restart your computer

5. **Set Up Python Environment**
   ```powershell
   # Create virtual environment
   python -m venv venv312
   
   # Activate it
   venv312\Scripts\activate
   
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Install test dependencies
   cd tests
   pip install -r requirements.txt
   cd ..
   ```

6. **Set Up Web Frontend**
   ```powershell
   cd web
   npm install
   cd ..
   ```

7. **Configure Google Places API** (optional)
   - Create `backend/.env` file:
     ```
     GOOGLE_PLACES_API_KEY=your_api_key_here
     ```
   - Get API key from https://console.cloud.google.com/
   - Enable "Places API" in Google Cloud Console

### macOS

1. **Install Python 3.12**
   ```bash
   # Using Homebrew
   brew install python@3.12
   
   # Or download from https://www.python.org/downloads/
   ```

2. **Install Node.js**
   ```bash
   brew install node
   # Or download from https://nodejs.org/
   ```

3. **Install Ollama**
   ```bash
   brew install ollama
   ollama pull qwen2.5:7b
   ```

4. **Set Up Python Environment**
   ```bash
   # Create virtual environment
   python3.12 -m venv venv312
   
   # Activate it
   source venv312/bin/activate
   
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt
   cd ..
   
   # Install test dependencies
   cd tests
   pip install -r requirements.txt
   cd ..
   ```

5. **Set Up Web Frontend**
   ```bash
   cd web
   npm install
   cd ..
   ```

6. **Configure Google Places API** (optional)
   - Create `backend/.env` file:
     ```
     GOOGLE_PLACES_API_KEY=your_api_key_here
     ```
   - Get API key from https://console.cloud.google.com/
   - Enable "Places API" in Google Cloud Console

## Usage

### Testing OCR and LLM

Before running the full app, test that OCR and LLM are working:

**Windows:**
```powershell
venv312\Scripts\activate
python tests/test_pipeline.py tests\5161.JPEG
```

**macOS:**
```bash
source venv312/bin/activate
python tests/test_pipeline.py tests/5161.JPEG
```

### Running the Web Application

1. **Start Backend Server**

   **Windows:**
   ```powershell
   venv312\Scripts\activate
   cd backend
   python server.py
   ```
   Backend runs on http://localhost:5000

   **macOS:**
   ```bash
   source venv312/bin/activate
   cd backend
   python server.py
   ```
   Backend runs on http://localhost:5000

2. **Start Frontend** (new terminal)

   **Windows:**
   ```powershell
   cd web
   npm run dev
   ```

   **macOS:**
   ```bash
   cd web
   npm run dev
   ```
   Frontend runs on http://localhost:3000

3. **Use the Application**
   - Open http://localhost:3000 in your browser
   - Click "Choose File" and select a gas receipt image
   - Click "Upload and Process"
   - View extracted data and station location (if API key is configured)

## Project Structure

```
receipt/
├── backend/              # Flask backend server
│   ├── server.py        # Main server file
│   ├── receipt_parser.py # LLM receipt parser
│   ├── station_finder.py # Google Places integration
│   ├── ocr_postprocess.py # OCR error correction
│   └── requirements.txt # Python dependencies
├── web/                  # React frontend
│   ├── src/
│   │   ├── App.jsx      # Main React component
│   │   └── App.css      # Styles
│   └── package.json     # Node dependencies
├── tests/                # Test scripts
│   ├── test_ocr.py      # OCR testing
│   ├── test_llm.py      # LLM testing
│   └── test_pipeline.py # Full pipeline test
└── README.md            # This file
```

## Troubleshooting

### PaddleOCR Installation Issues

**Windows:**
- Ensure Python 3.12 is installed (not 3.13)
- Enable Windows Long Path support (see Installation step 4)
- If installation fails, try: `pip install paddlepaddle==3.2.2 paddleocr==3.3.0`

**macOS:**
- Ensure Python 3.12 is installed
- If installation fails, try: `pip install paddlepaddle==3.2.2 paddleocr==3.3.0`

### Ollama Not Running

- **Windows:** Check if Ollama service is running in Task Manager
- **macOS:** Run `ollama serve` in terminal
- Verify: `ollama list` should show `qwen2.5:7b`

### Google Places API Not Working

- Verify API key is in `backend/.env`
- Check API key is enabled for "Places API" in Google Cloud Console
- Station lookup will be skipped if API key is not set (app still works)

## Technology Stack

- **Backend:** Flask (Python)
- **OCR:** PaddleOCR (Greek language support)
- **LLM:** Ollama (qwen2.5:7b)
- **Frontend:** React + Vite
- **Maps:** Google Places API (optional)

## License

MIT
