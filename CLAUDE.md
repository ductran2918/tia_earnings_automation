# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based earnings automation tool built for **Tech in Asia's editorial team** to automate earnings reporting from PDFs to charts and articles. The application extracts financial data from PDF earnings reports using Google Gemini AI and includes Firebase integration for centralized data storage. It uses Streamlit for the web interface and provides a complete financial data extraction pipeline.

## Current Implementation Status

### ✅ FULLY IMPLEMENTED Features

**Core Application (`app/main.py` - 440 lines)**
- Complete Streamlit web interface with responsive dual-column layout
- File upload with comprehensive validation (PDF type, 25MB size limit)
- PDF processing using `pdfplumber` for text extraction and metadata
- Full LLM integration with Google Gemini (`gemini-1.5-flash`) for structured data extraction
- Results display with evidence text and validation
- Temporary file management with timestamped storage in `.tmp/` directory
- Error handling for corrupted/encrypted PDFs
- **NEW: Firebase Firestore integration with connection testing**
- **NEW: Environment-based configuration with .env support**

**Key Functions Implemented:**
- `save_temp_file()`: Timestamp-based temporary file storage in `.tmp/` directory
- `get_pdf_info()`: PDF metadata extraction (page count, text availability)  
- `read_page_preview()`: First page text preview (300 characters)
- `extract_full_pdf_text()`: Complete PDF text extraction from all pages
- `extract_financial_data_with_llm()`: Structured financial data extraction using Gemini
- `format_file_size()`: Human-readable file size formatting
- **`initialize_firebase()`**: Firebase Admin SDK initialization with error handling
- **Main sidebar with Firebase connection testing capability**

**Data Extraction Capabilities:**
- Revenue and net profit extraction with evidence text
- Company name and report type identification  
- Period detection and currency preservation (no conversion)
- Structured JSON output with validation
- Evidence text showing exact source quotes from PDF
- Company name validation against user hint input

## Development Setup

### Prerequisites
- Python 3.8+ (currently running Python 3.13)
- Google Gemini API key
- Firebase project with service account credentials
- Virtual environment recommended

### Installation
```bash
# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
Create `.env` file in root directory with:
```env
GEMINI_API_KEY=your_gemini_api_key_here
FIREBASE_CREDENTIALS_PATH=path_to_firebase_service_account.json
```

### Running the Application
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the main application
streamlit run app/main.py

# Alternative: Run with specific port
streamlit run app/main.py --server.port 8501
```

### Firebase Setup
- Firebase project: `financial-data-extractor-142aa`
- Service account key: `financial-data-extractor-142aa-firebase-adminsdk-fbsvc-c3eacd481a.json`
- Connection testing available in application sidebar

## Architecture

### Core Components
- **UI Framework**: Streamlit with responsive dual-column layout and sidebar
- **PDF Processing**: `pdfplumber` for text extraction and metadata analysis
- **AI Processing**: Google Gemini (`gemini-1.5-flash`) for structured financial data extraction  
- **Database**: Firebase Firestore for centralized data storage
- **File Management**: Temporary storage with timestamped cleanup and validation
- **Data Output**: Structured JSON with evidence tracking and validation

### Key Dependencies (from requirements.txt)
- `streamlit==1.39.0`: Web UI framework
- `pdfplumber==0.11.7`: PDF text extraction and processing
- `google-generativeai==0.8.5`: LLM integration for data extraction
- **`firebase-admin`**: Firebase SDK for Firestore database operations
- `pandas==2.3.2`: Data manipulation and analysis
- `python-dotenv==1.1.1`: Environment variable management
- Supporting libraries: `pdfminer.six`, `pillow`, `numpy`, `pypdf2`

### Application Flow
1. **Upload**: PDF file upload with comprehensive validation (type, size, corruption check)
2. **Processing**: Text extraction using pdfplumber with complete error handling
3. **Analysis**: Full document text sent to Gemini LLM for structured financial data extraction
4. **Display**: Results shown with metrics, evidence text, and user input validation
5. **Storage**: Temporary files managed with timestamped cleanup capabilities
6. **Integration**: Firebase connection testing and future database storage capability

## File Structure

```
├── app/
│   └── main.py                                           # Complete Streamlit application (440 lines)
├── .tmp/                                                 # Temporary PDF storage (auto-created)
├── .venv/                                                # Python virtual environment
├── .claude/                                              # Claude Code configuration
├── .streamlit/                                           # Streamlit configuration
├── requirements.txt                                      # All dependencies (49 packages)
├── .env                                                  # Environment variables (GEMINI_API_KEY, FIREBASE_CREDENTIALS_PATH)
├── financial-data-extractor-142aa-firebase-adminsdk-*.json # Firebase service account credentials
├── next_features_to_build.md                            # Comprehensive roadmap for next 4 features
├── mvp_build_order.md                                   # Original development roadmap  
├── prompt_step*.md                                      # Step-specific implementation guides
├── README.md                                            # Project description for Tech in Asia team
├── .gitignore                                           # Git ignore patterns
└── CLAUDE.md                                            # This documentation
```

## Configuration

### Environment Variables (.env)
Required configuration in `.env` file:
- `GEMINI_API_KEY`: Google Gemini API key for LLM processing  
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON file

### LLM Configuration (Fixed Settings)
- Model: `gemini-1.5-flash` (cost-optimized for consistent results)
- Temperature: `0.0` (deterministic output)
- Max tokens: `1024` (structured JSON responses)
- JSON-only output with strict formatting and validation

### User Settings (Application Sidebar)
- Company name hint for result validation (optional)
- Firebase connection testing capability
- Future: Smart PDF page trimming settings

## What's Working

### Complete Features
1. **File Upload & Validation**: PDF type checking, 25MB size limits, corruption detection
2. **PDF Processing**: Full text extraction, page counting, metadata analysis, preview generation  
3. **LLM Integration**: Structured data extraction with evidence tracking and JSON validation
4. **Results Display**: Formatted metrics with evidence text and user hint validation
5. **Error Handling**: Comprehensive error management for all failure modes (encrypted, corrupted, missing API keys)
6. **File Management**: Temporary storage with timestamped cleanup and session state management
7. **Firebase Integration**: Connection testing, credential validation, and SDK initialization
8. **Environment Management**: `.env` support with secure credential handling

### Extraction Capabilities
- Revenue detection with value, unit, period, and evidence text
- Net profit extraction (specifically net profit, not operating profit)
- Company name identification with user hint validation
- Report type classification and period detection  
- Currency preservation (no automatic conversion)
- Period formatting (Q2 2025, "Three months ended June 30, 2025", etc.)
- Evidence quotes showing exact source sentences from PDF

## Next Development Priorities

Based on `next_features_to_build.md`, the **4 key features to build next**:

### 1. Smart PDF Page Trimming (HIGH PRIORITY) 
- **Objective**: 80-90% cost reduction in LLM token usage
- **Implementation**: Scan pages for financial keywords, only process relevant pages
- **Expected Impact**: Immediate cost savings for processing 300+ companies

### 2. Enhanced LLM Prompt (HIGH PRIORITY)
- **Objective**: Extract all ~20 financial data points instead of current 2
- **Implementation**: Expand prompt to include costs, EBITDA, assets, liabilities, cash flow
- **Expected Impact**: Complete financial dataset per company

### 3. Database Integration (MEDIUM PRIORITY)
- **Objective**: Store extracted data in Firebase Firestore
- **Implementation**: Add "Save to Database" functionality after extraction
- **Expected Impact**: Centralized storage for 300 companies across multiple years

### 4. Duplicate Detection System (LOW PRIORITY)
- **Objective**: Prevent processing duplicate financial statements  
- **Implementation**: Pre-processing database checks for existing company + period combinations
- **Expected Impact**: Resource optimization and better user experience

## Testing Approach

### Current Testing Strategy
- Upload various PDF formats (quarterly reports, annual reports, 10-K, 10-Q)
- Test error scenarios (encrypted PDFs, corrupted files, missing API keys, oversized files)
- Validate extraction accuracy against known financial reports
- Check evidence text matches and period detection accuracy  
- Verify file cleanup and session state management
- Test Firebase connection and credential validation
- Validate company name matching against user hints

### Recommended Test Cases
- **File Validation**: Test 25MB+ files, non-PDF files, encrypted/password-protected PDFs
- **Extraction Accuracy**: Test with Tech in Asia's target companies (Grab, Sea Limited, etc.)
- **Edge Cases**: PDFs with no financial data, image-only PDFs, multi-currency reports
- **Firebase Integration**: Test connection failures, missing credentials, database operations