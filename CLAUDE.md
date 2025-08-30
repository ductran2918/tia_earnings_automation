# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based earnings automation tool that extracts financial data from PDF earnings reports using Google Gemini AI. The application uses Streamlit for the web interface and provides a complete financial data extraction pipeline.

## Current Implementation Status

### ✅ FULLY IMPLEMENTED Features

**Core Application (`app/main.py` - 374 lines)**
- Complete Streamlit web interface with dual-column layout
- File upload with comprehensive validation (PDF type, 25MB size limit)
- PDF processing using `pdfplumber` for text extraction and metadata
- Full LLM integration with Google Gemini for structured data extraction
- Results display with evidence text and validation
- Temporary file management with timestamped storage
- Error handling for corrupted/encrypted PDFs

**Key Functions Implemented:**
- `save_temp_file()`: Timestamp-based temporary file storage in `.tmp/` directory
- `get_pdf_info()`: PDF metadata extraction (page count, text availability)
- `read_page_preview()`: First page text preview (300 characters)
- `extract_full_pdf_text()`: Complete PDF text extraction
- `extract_financial_data_with_llm()`: Structured financial data extraction using Gemini
- `format_file_size()`: Human-readable file size formatting

**Data Extraction Capabilities:**
- Revenue and net profit extraction with evidence
- Company name and report type identification
- Period detection and currency preservation
- Structured JSON output with validation
- Evidence text showing exact source quotes

## Development Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key (stored in `.env` as `GEMINI_API_KEY`)

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run app/main.py
```

## Architecture

### Core Components
- **UI Framework**: Streamlit with dual-column responsive layout
- **PDF Processing**: `pdfplumber` for text extraction and metadata
- **AI Processing**: Google Gemini (`gemini-1.5-flash`) for financial data extraction
- **File Management**: Temporary storage with cleanup and validation
- **Data Output**: Structured JSON with evidence tracking

### Key Dependencies (from requirements.txt)
- `streamlit==1.39.0`: Web UI framework
- `pdfplumber==0.11.7`: PDF text extraction
- `google-generativeai==0.8.5`: LLM integration
- `pandas==2.3.2`: Data manipulation
- `python-dotenv==1.1.1`: Environment variable management
- Supporting libraries: `pdfminer.six`, `pillow`, `numpy`, `pypdf2`

### Application Flow
1. **Upload**: PDF file upload with validation (type, size, structure)
2. **Processing**: Text extraction using pdfplumber with error handling
3. **Analysis**: Full document text sent to Gemini LLM for structured extraction
4. **Display**: Results shown with metrics, evidence text, and validation
5. **Storage**: Temporary files managed with cleanup capabilities

## File Structure

```
├── app/
│   └── main.py           # Complete Streamlit application (374 lines)
├── .tmp/                 # Temporary PDF storage (auto-created)
├── requirements.txt      # All dependencies installed
├── .env                  # Environment variables (GEMINI_API_KEY required)
├── mvp_build_order.md    # Original development roadmap
├── prompt_step*.md       # Step-specific implementation guides
└── CLAUDE.md             # This documentation
```

## Configuration

### Environment Variables
Required in `.env` file:
- `GEMINI_API_KEY`: Google Gemini API key for LLM processing

### LLM Configuration (Fixed Settings)
- Model: `gemini-1.5-flash`
- Temperature: `0.0` (consistent results)
- Max tokens: `1024`
- JSON-only output with strict formatting

### User Settings (Sidebar)
- Company name hint for validation (optional)

## What's Working

### Complete Features
1. **File Upload & Validation**: PDF type checking, size limits, corruption detection
2. **PDF Processing**: Full text extraction, page counting, preview generation  
3. **LLM Integration**: Structured data extraction with evidence tracking
4. **Results Display**: Formatted metrics with evidence text and validation
5. **Error Handling**: Comprehensive error management for all failure modes
6. **File Management**: Temporary storage with cleanup and session state

### Extraction Capabilities
- Revenue detection with value, unit, period, and evidence
- Net profit extraction (not operating profit)
- Company name identification
- Report type classification  
- Currency preservation (no conversion)
- Period formatting (Q2 2025, etc.)
- Evidence quotes from source text

## Next Development Opportunities

The application is functionally complete but could benefit from:

1. **CSV Export**: Add download functionality for extracted data
2. **Batch Processing**: Multiple file uploads and processing
3. **History Tracking**: Session-based extraction history
4. **Caching**: File hash-based result caching to avoid re-processing
5. **Additional Metrics**: Cash flow, EBITDA, other financial metrics
6. **Data Validation**: Cross-reference multiple mentions of same metric
7. **Performance**: Streaming for large documents
8. **Configuration**: User-adjustable LLM parameters

## Testing Approach

- Upload various PDF formats (quarterly reports, annual reports)
- Test error scenarios (encrypted PDFs, corrupted files, missing API key)
- Validate extraction accuracy against known financial reports
- Check evidence text matches and period detection
- Verify file cleanup and session state management