# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based earnings automation tool for Tech in Asia's editorial team that extracts financial data from PDF earnings reports and converts them to charts and articles. The project uses Streamlit for the web interface and Google Gemini AI for intelligent data extraction.

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
# Activate virtual environment
source .venv/bin/activate

# Run the main application
streamlit run app/main.py

# Alternative: Run with specific port
streamlit run app/main.py --server.port 8501
```

## Architecture

### Core Components
- **PDF Processing**: Uses `pdfplumber` and `pdfminer.six` for text extraction from earnings PDFs
- **AI Processing**: Google Gemini API via `google-generativeai` for intelligent data extraction
- **Data Handling**: `pandas` for data manipulation and CSV persistence
- **UI**: Streamlit web interface for file uploads and results display
- **Caching**: File hash-based caching to avoid redundant API calls

### Key Dependencies
- `streamlit`: Web UI framework
- `pdfplumber`: PDF text extraction
- `google-generativeai`: LLM integration for data extraction
- `pandas`: Data manipulation and CSV operations
- `python-dotenv`: Environment variable management

### Data Flow
1. PDF upload via Streamlit interface
2. Text extraction per page using pdfplumber
3. Snippet finding using regex for revenue/profit patterns
4. LLM processing of snippets to extract structured data
5. Results display with evidence text and page references
6. CSV persistence with file hash tracking

## MVP Build Order

The project follows a structured 12-step build plan (see `mvp_build_order.md`):

### Core Steps (1-8)
1. **Streamlit shell**: Basic file uploader interface
2. **Temp file handling**: Save uploaded PDFs temporarily
3. **Page text extraction**: Extract text from each PDF page
4. **Snippet finder**: Regex-based financial metric detection
5. **Config panel**: API key and model parameter inputs
6. **LLM integration**: Send snippets to Gemini for structured extraction
7. **Result UI**: Display extracted metrics with evidence
8. **CSV persistence**: Save results with file hash tracking

### Enhancement Steps (9-12)
9. **Caching**: Reuse results for identical files and settings
10. **Error handling**: Robust error management and logging
11. **Period detection**: Auto-detect reporting periods from text
12. **History interface**: View and export historical extractions

## Environment Variables

Required in `.env` file:
- `GEMINI_API_KEY`: Google Gemini API key for LLM processing

## File Structure

```
├── app/
│   └── main.py           # Main Streamlit application (Steps 1-2 implemented)
├── .tmp/                 # Temporary PDF storage (auto-created)
├── .venv/                # Python virtual environment
├── .streamlit/           # Streamlit configuration
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
├── mvp_build_order.md    # 12-step development roadmap
├── prompt_step*.md       # Step-specific implementation guides
└── CLAUDE.md             # This file
```

**Note**: Planned directories not yet created:
- `extractors/` - PDF processing modules (Step 3+)
- `data/` - Processed data and CSV files (Step 8+)  
- `samples/` - Sample PDF files for testing

## Current Implementation Status

**✅ Completed (Steps 1-2)**:
- Streamlit shell with file uploader interface (`app/main.py`)
- PDF validation (MIME type, file size, page count)
- Temporary file handling with timestamped storage (`.tmp/`)
- Basic PDF processing with pdfplumber integration
- Error handling for corrupted/encrypted PDFs

**🔲 Remaining (Steps 3-12)**:
- Page text extraction and snippet detection (regex-based)
- Configuration panel for API keys and LLM parameters  
- Google Gemini integration for structured data extraction
- Results UI with evidence display and CSV persistence
- Advanced features: caching, period detection, history interface

## Development Workflow

- Follow the step-by-step build order from `mvp_build_order.md`
- Current active development at Step 3 (page text extraction)
- Each step should be demoable and add ≤ 60 lines of code
- Use `.tmp/` directory for uploaded file storage during development
- Leverage existing virtual environment (`.venv/`) with all dependencies installed

## Testing

- Test with both sample PDFs after each development step
- Verify text extraction produces readable content
- Ensure LLM responses return valid JSON format
- Test error scenarios (missing API key, malformed PDFs, API failures)
- Validate CSV persistence and data integrity