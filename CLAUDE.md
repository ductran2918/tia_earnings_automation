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
- Full LLM integration with OpenRouter API for structured data extraction
- Results display with evidence text and validation
- Temporary file management with timestamped storage in `.tmp/` directory
- Error handling for corrupted/encrypted PDFs
- **NEW: Firebase Firestore integration with connection testing**
- **NEW: Environment-based configuration with .env support**
- **NEW: Lazy client initialization pattern for reliable Streamlit Cloud deployment**

**OpenRouter Client Management (`app/client.py` - 71 lines)**
- Centralized OpenAI client configuration with OpenRouter base URL
- **Lazy initialization pattern**: Client created on-demand, not at module import time
- **`get_client()`**: Returns cached OpenAI client instance (creates on first call)
- Resolves Streamlit Cloud deployment issue where `st.secrets` is unavailable at import time
- API key loading priority: Streamlit secrets → Environment variables (.env)
- Global caching (`_client_instance`) for performance optimization
- Clear error messages if `OPENROUTER_API_KEY` is missing

**Company-Specific Extraction Modules**
- **Grab Extraction (`app/grab_extraction.py` - 163 lines)**: Extracts 23 Grab-specific metrics across Deliveries, Mobility, and Financial Services segments
- **Sea Group Extraction (`app/sea_group_extraction.py` - 177 lines)**: Extracts 41 Sea Group-specific metrics across Digital Entertainment/Garena, E-commerce/Shopee, and Digital Financial Services/SeaMoney segments
- **Alibaba Group Extraction (`app/alibaba_extraction.py` - 210 lines)**: Extracts 36 Alibaba-specific metrics across consolidated financials and 7 business segments (Taobao/Tmall, International, Cainiao, Cloud Intelligence, Local Services, Digital Media & Entertainment, All Others)
- All modules follow identical architecture pattern with lazy client initialization
- Company-specific prompts loaded from `prompt/` directory
- Robust JSON parsing with markdown block handling, NULL→null conversion, and missing comma insertion
- Bracket-matching fallback extraction for malformed JSON

**Key Functions Implemented:**
- `save_temp_file()`: Timestamp-based temporary file storage in `.tmp/` directory
- `get_pdf_info()`: PDF metadata extraction (page count, text availability)
- `read_page_preview()`: First page text preview (300 characters)
- `extract_full_pdf_text()`: Complete PDF text extraction from all pages
- `extract_financial_data_with_llm()`: Structured financial data extraction using OpenRouter LLM
- `extract_public_company_data_with_llm()`: Public company name extraction from PDFs
- **`extract_grab_data_with_llm()`**: Grab-specific financial data extraction (23 metrics)
- **`extract_sea_group_data_with_llm()`**: Sea Group-specific financial data extraction (41 metrics)
- **`extract_alibaba_data_with_llm()`**: Alibaba Group-specific financial data extraction (36 metrics)
- `format_file_size()`: Human-readable file size formatting
- **`get_client()`**: Lazy-loaded OpenAI client with caching (app/client.py)
- **`initialize_firebase()`**: Firebase Admin SDK initialization with error handling
- **Main sidebar with Firebase connection testing capability**

**Data Extraction Capabilities:**
- **Generic Extraction**: Revenue and net profit extraction with evidence text
- **Grab-Specific**: 23 metrics including GMV, incentives, user metrics (MTU), segment financials for Deliveries, Mobility, and Financial Services
- **Sea Group-Specific**: 41 metrics including group financials, Digital Entertainment/Garena metrics (bookings, users, ARPU), E-commerce/Shopee metrics (marketplace revenue, VAS), and Digital Financial Services/SeaMoney metrics
- **Alibaba Group-Specific**: 36 metrics including consolidated financials (revenue, profit, expenses, cash, assets), segment revenue and adjusted EBITDA for 7 business units (Taobao/Tmall, International Digital Commerce, Cainiao Logistics, Cloud Intelligence, Local Services, Digital Media & Entertainment, All Others), balance sheet data, cash flow statements, and employee count. Extracts USD values only (not RMB).
- Company name and report type identification
- Period detection and currency preservation (no conversion, except Alibaba which converts RMB to USD per prompt instructions)
- Structured JSON output with validation
- Evidence text showing exact source quotes from PDF (for generic extraction)
- Company slug validation and auto-correction

## Development Setup

### Prerequisites
- Python 3.8+ (currently running Python 3.13)
- OpenRouter API key (for LLM access)
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
OPENROUTER_API_KEY=your_openrouter_api_key_here
FIREBASE_CREDENTIALS_PATH=path_to_firebase_service_account.json
```

**Note**: For Streamlit Cloud deployment, set `OPENROUTER_API_KEY` in Streamlit secrets. The lazy client initialization pattern ensures secrets are loaded after Streamlit starts.

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
- **AI Processing**: OpenRouter API (OpenAI-compatible) for structured financial data extraction
- **Client Management**: Lazy initialization pattern for OpenAI client (`app/client.py`)
- **Database**: Firebase Firestore for centralized data storage
- **File Management**: Temporary storage with timestamped cleanup and validation
- **Data Output**: Structured JSON with evidence tracking and validation

### Key Dependencies (from requirements.txt)
- `streamlit==1.39.0`: Web UI framework
- `pdfplumber==0.11.7`: PDF text extraction and processing
- **`openai`**: OpenAI SDK for OpenRouter API integration
- **`firebase-admin`**: Firebase SDK for Firestore database operations
- `pandas==2.3.2`: Data manipulation and analysis
- `python-dotenv==1.1.1`: Environment variable management
- Supporting libraries: `pdfminer.six`, `pillow`, `numpy`, `pypdf2`

### Application Flow
1. **Upload**: PDF file upload with comprehensive validation (type, size, corruption check)
2. **Processing**: Text extraction using pdfplumber with complete error handling
3. **Client Initialization**: Lazy-loaded OpenAI client created on first API call (ensures Streamlit secrets available)
4. **Analysis**: Full document text sent to OpenRouter LLM for structured financial data extraction
5. **Display**: Results shown with metrics, evidence text, and user input validation
6. **Storage**: Temporary files managed with timestamped cleanup capabilities
7. **Integration**: Firebase connection testing and future database storage capability

## File Structure

```
├── app/
│   ├── main.py                                          # Complete Streamlit application (440 lines)
│   ├── client.py                                        # OpenRouter client with lazy initialization (71 lines)
│   ├── extract_data.py                                  # Generic financial data extraction functions
│   ├── grab_extraction.py                               # Grab-specific extraction logic (163 lines)
│   ├── sea_group_extraction.py                          # Sea Group-specific extraction logic (177 lines)
│   ├── alibaba_extraction.py                            # Alibaba Group-specific extraction logic (210 lines)
│   ├── company_extractors.py                            # Company extractor registry and configuration
│   ├── public_company_ui.py                             # Public company UI rendering (Grab, Sea Group, Alibaba)
│   ├── authentication.py                                # Firebase authentication (lazy pattern)
│   ├── public_company_extraction.py                     # Public company name extraction
│   ├── database.py                                      # Supabase database operations (push, duplicate check, retrieval)
│   ├── supabase_client.py                               # Supabase client singleton
│   └── ui_components.py                                 # Shared UI components (file uploader, results display, database push)
├── prompt/
│   ├── grab_com_extraction.md                           # Grab extraction prompt (23 metrics)
│   ├── sea_group_extraction.md                          # Sea Group extraction prompt (41 metrics)
│   └── alibaba_group_extraction.md                      # Alibaba Group extraction prompt (36 metrics)
├── .tmp/                                                # Temporary PDF storage (auto-created)
├── .venv/                                               # Python virtual environment
├── .claude/                                             # Claude Code configuration
├── .streamlit/                                          # Streamlit configuration
├── requirements.txt                                     # All dependencies (49 packages)
├── .env                                                 # Environment variables (OPENROUTER_API_KEY, FIREBASE_CREDENTIALS_PATH)
├── public_companies_list.json                           # Company name to slug mapping
├── financial-data-extractor-142aa-firebase-adminsdk-*.json # Firebase service account credentials
├── next_features_to_build.md                           # Comprehensive roadmap for next 4 features
├── mvp_build_order.md                                  # Original development roadmap
├── prompt_step*.md                                     # Step-specific implementation guides
├── README.md                                           # Project description for Tech in Asia team
├── .gitignore                                          # Git ignore patterns
└── CLAUDE.md                                           # This documentation
```

## Configuration

### Environment Variables (.env)
Required configuration in `.env` file:
- `OPENROUTER_API_KEY`: OpenRouter API key for LLM processing
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON file

**Streamlit Cloud Configuration:**
- Set `OPENROUTER_API_KEY` in Streamlit secrets (not environment variables)
- The lazy client initialization pattern ensures secrets are properly loaded after Streamlit starts

### LLM Configuration
- **API Provider**: OpenRouter (OpenAI-compatible API)
- **Client Pattern**: Lazy initialization via `get_client()` function
- Temperature: `0.0` (deterministic output)
- Max tokens: `1024` (structured JSON responses)
- JSON-only output with strict formatting and validation

### User Settings (Application Sidebar)
- Company name hint for result validation (optional)
- Firebase connection testing capability
- Future: Smart PDF page trimming settings

## Critical Implementation Details

### Lazy Client Initialization Pattern

**Problem Solved**: Streamlit Cloud deployment was failing with "The api_key client option must be set" error.

**Root Cause**:
- Previous implementation created the OpenAI client at module import time
- At that moment, Streamlit hadn't started yet, so `st.secrets` was unavailable
- API key couldn't be loaded, resulting in `api_key=None`

**Solution** (implemented in [app/client.py](app/client.py)):
```python
# Global cache for client instance
_client_instance = None

def get_client() -> OpenAI:
    """Get or create the OpenRouter client (lazy initialization)."""
    global _client_instance

    # Return cached instance if already created
    if _client_instance is not None:
        return _client_instance

    # Load API key (NOW st.secrets is available)
    # Priority: Streamlit secrets → Environment variables
    # ... API key loading logic ...

    # Create and cache client
    _client_instance = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    return _client_instance
```

**Usage Pattern**:
All extraction functions now call `get_client()` instead of importing a module-level client:
- [app/extract_data.py](app/extract_data.py): `extract_financial_data_with_llm()`, `extract_public_company_data_with_llm()`
- [app/grab_extraction.py](app/grab_extraction.py): `extract_grab_data_with_llm()`
- [app/sea_group_extraction.py](app/sea_group_extraction.py): `extract_sea_group_data_with_llm()`
- [app/alibaba_extraction.py](app/alibaba_extraction.py): `extract_alibaba_data_with_llm()`

**Benefits**:
- ✅ Works on Streamlit Cloud (secrets available when client created)
- ✅ Works locally (.env fallback)
- ✅ Performance optimized (client cached after first call)
- ✅ Clear error messages if API key missing
- ✅ Matches pattern in [app/authentication.py](app/authentication.py)

### Company-Specific Extraction Modules

**Architecture Pattern**:
Both Grab and Sea Group extraction modules follow an identical architecture:
1. **Prompt Loading**: Load company-specific prompt from `prompt/` directory
2. **JSON Parsing**: Robust parsing with markdown block stripping and bracket-matching fallback
3. **LLM Extraction**: Call OpenRouter API with lazy-initialized client
4. **Validation**: Company slug validation and auto-correction
5. **Error Handling**: Return `{"error": "message"}` on failures

**Sea Group Extraction Module** ([app/sea_group_extraction.py](app/sea_group_extraction.py)):
- **41 metrics** across 4 categories:
  - Group-level: 15 metrics (revenue, profit, expenses, cash positions)
  - Digital Entertainment (Garena): 9 metrics (bookings, revenue, users, ARPU)
  - E-commerce (Shopee): 7 metrics (marketplace revenue, VAS, product revenue)
  - Digital Financial Services (SeaMoney): 3 metrics (revenue, expenses, EBITDA)
- **Prompt**: [prompt/sea_group_extraction.md](prompt/sea_group_extraction.md) (131 lines)
- **Company slug**: `"sea-group-garena"`
- **Status**: Fully implemented with extraction and database push
- **Segments**: Recognizes business unit alternative names (Garena, Shopee, SeaMoney)

**Function Signature** (identical to Grab):
```python
extract_sea_group_data_with_llm(
    pdf_text: str,
    company_hint: str = "Sea Group",
    model_name: str = "deepseek/deepseek-chat-v3.1:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict
```

### Database Operations (Supabase Integration)

**Module**: [app/database.py](app/database.py) - Handles storing extracted financial data to Supabase

**Supported Companies**:
- Grab Holdings (`grab-com`) → Table: `grab_metrics`
- Sea Group Limited (`sea-group-garena`) → Table: `seagroup_metrics`
- Alibaba Group Holding Limited (`alibaba-group`) → Table: `alibaba_metrics`

**Architecture Pattern** (identical for all companies):

1. **Push Functions**: `push_grab_to_supabase()`, `push_sea_group_to_supabase()`, `push_alibaba_to_supabase()`
   - Validate Supabase client configuration
   - Check for extraction errors
   - Validate required fields (company_slug, date)
   - Verify company slug matches expected value
   - Validate date format (YYYY-MM-DD)
   - Remove auto-generated `id` field before INSERT/UPDATE
   - Check for duplicates via company_slug + date
   - UPDATE if record exists, INSERT if new
   - Return success/error response with record ID

2. **Duplicate Detection**: `check_duplicate_grab()`, `check_duplicate_sea_group()`, `check_duplicate_alibaba()`
   - Query Supabase for existing records matching company_slug + date
   - Return existing record if found, None otherwise
   - Graceful degradation if Supabase not configured

3. **Records Retrieval**: `get_all_grab_records()`, `get_all_sea_group_records()`, `get_all_alibaba_records()`
   - Fetch recent records ordered by date (descending)
   - Default limit: 100 records
   - Return empty list if Supabase not configured

**Table Constraints** (both tables):
- `id`: Auto-generated primary key with NOT-NULL constraint (must be explicitly excluded from INSERT/UPDATE)
- `(company_slug, date)`: Unique constraint (one record per company per date)
- `company_slug`: Required field
- `date`: Required field (ISO format: YYYY-MM-DD)

**Critical Fix**: The extraction functions return `"id": null` in the JSON output. The push functions use dictionary comprehension `{k: v for k, v in extracted_data.items() if k != "id"}` to explicitly exclude the `id` field before INSERT/UPDATE operations. This prevents "null value in column 'id' violates not-null constraint" errors.

**UI Integration** ([app/ui_components.py](app/ui_components.py)):
- Dynamic routing based on `company_slug`
- Duplicate warning displayed if data already exists for that date
- "Push to Supabase" button with company-specific key
- Success: Celebration balloons + Flourish integration message
- Error: Clear error message with troubleshooting guidance

**Supabase Client** ([app/supabase_client.py](app/supabase_client.py)):
- Singleton pattern (mirrors OpenRouter client pattern)
- Environment variables: `SUPABASE_URL`, `SUPABSE_SERVICE_ROLE_KEY` (note: intentional misspelling)
- Graceful degradation: `supabase = None` if credentials missing

## What's Working

### Complete Features
1. **File Upload & Validation**: PDF type checking, 25MB size limits, corruption detection
2. **PDF Processing**: Full text extraction, page counting, metadata analysis, preview generation
3. **LLM Integration**: Structured data extraction with evidence tracking and JSON validation via OpenRouter
4. **Lazy Client Initialization**: On-demand OpenAI client creation for Streamlit Cloud compatibility
5. **Company-Specific Extraction**: Grab (23 metrics) and Sea Group (41 metrics) with custom prompts
6. **Database Push**: Supabase integration for Grab and Sea Group with duplicate detection and INSERT/UPDATE logic
7. **Results Display**: Formatted metrics with evidence text and user hint validation
8. **Error Handling**: Comprehensive error management for all failure modes (encrypted, corrupted, missing API keys)
9. **File Management**: Temporary storage with timestamped cleanup and session state management
10. **Firebase Integration**: Connection testing, credential validation, and SDK initialization (also uses lazy pattern)
11. **Environment Management**: `.env` support with secure credential handling and Streamlit secrets priority
12. **Company Registry**: Extensible extractor configuration system for adding new companies

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