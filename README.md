# TIA Earnings Automation

Internal tool for **Tech in Asia's editorial team** to automate earnings reporting from PDFs to charts and articles.

## Overview

This Python-based application extracts financial data from PDF earnings reports using AI (OpenRouter API) and stores it in Supabase for downstream use in Flourish charts and editorial content. It features a Streamlit web interface that allows non-technical users to upload PDFs and get structured financial data in seconds.

### Key Features

- **PDF Processing**: Extracts text from earnings PDFs with comprehensive validation
- **AI-Powered Extraction**: Uses OpenRouter API (OpenAI-compatible) to extract structured financial metrics
- **Company-Specific Modules**: Pre-built extractors for Grab (23 metrics), Sea Group (41 metrics), and Alibaba (36 metrics)
- **Database Integration**: Pushes extracted data to Supabase with duplicate detection
- **User-Friendly UI**: Streamlit interface with file upload, results display, and database push functionality
- **Production-Ready**: Deployed on Streamlit Cloud with lazy client initialization pattern

## Quick Start

### Prerequisites

- Python 3.8+ (tested with Python 3.13)
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- Supabase project with service role key ([Create project](https://supabase.com/))

### Installation

```bash
# Clone the repository
cd tia_earnings_automation

# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
# Required: OpenRouter API key for LLM extraction
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Required: Supabase database credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Optional: Firebase credentials (if using Firebase features)
FIREBASE_CREDENTIALS_PATH=path_to_firebase_service_account.json
```

**Important**:
- For Streamlit Cloud deployment, set these as **Streamlit secrets** instead of environment variables
- The app uses lazy initialization to ensure secrets are loaded after Streamlit starts

### Running the Application

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the Streamlit app
streamlit run app/main.py

# Alternative: Run with specific port
streamlit run app/main.py --server.port 8501
```

The app will open in your browser at `http://localhost:8501`

## Usage Guide

### 1. Select Company
Choose from supported companies:
- **Grab Holdings** (23 metrics: GMV, MTU, segment financials)
- **Sea Group Limited** (41 metrics: Garena, Shopee, SeaMoney segments)
- **Alibaba Group** (36 metrics: consolidated + 7 business segments)

### 2. Upload PDF
- Drag and drop or click to upload earnings PDF
- Supports PDFs up to 25MB
- Automatically validates file type and detects corruption

### 3. Extract Data
- Click the company-specific extraction button
- AI processes the entire PDF and extracts structured metrics
- Results display in JSON format with all financial data points

### 4. Push to Database
- Click "Push to Supabase" to store data
- Automatic duplicate detection (company + date uniqueness)
- Updates existing records or inserts new ones
- Success message includes Flourish integration instructions

## Architecture

### High-Level Overview

```
┌─────────────────┐
│  User (Browser) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         Streamlit Web Interface              │
│  - File upload & validation                  │
│  - Company selection                         │
│  - Results display                           │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│       PDF Processing Layer                   │
│  - Text extraction (pdfplumber)              │
│  - Metadata analysis                         │
│  - Temporary file management                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│      AI Extraction Layer                     │
│  - Company-specific extractors               │
│  - OpenRouter API integration                │
│  - Lazy client initialization                │
│  - JSON parsing & validation                 │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│       Database Layer (Supabase)              │
│  - Duplicate detection                       │
│  - INSERT/UPDATE operations                  │
│  - Data retrieval with a public .csv file
|  - Flourish charts auto  update new
|     data                                    │
└─────────────────────────────────────────────┘
```

### Core Components

#### 1. **UI Framework** (`app/main.py` + `app/ui_components.py`)
- Streamlit-based web interface with responsive dual-column layout
- File upload with comprehensive validation (type, size, corruption)
- Results display with formatted metrics
- Database push functionality with duplicate warnings

#### 2. **PDF Processing** (`pdfplumber` library)
- Text extraction from all pages
- Metadata analysis (page count, text availability)
- Preview generation for validation
- Temporary file management with timestamped storage

#### 3. **AI Extraction Layer**
- **Client Management** (`app/client.py`): Lazy-initialized OpenAI client for OpenRouter API
- **Company Extractors**:
  - `app/grab_extraction.py`: 23 Grab-specific metrics
  - `app/sea_group_extraction.py`: 41 Sea Group metrics
  - `app/alibaba_extraction.py`: 36 Alibaba metrics
- **Prompt Templates** (`prompt/*.md`): Company-specific extraction instructions
- **JSON Parsing**: Robust parsing with NULL→null conversion and bracket-matching fallback

#### 4. **Database Integration** (`app/database.py` + `app/supabase_client.py`)
- Singleton Supabase client with graceful degradation
- Company-specific push functions with 5-step validation:
  1. Client configuration check
  2. Extraction error validation
  3. Required fields check (company_slug, date)
  4. Company slug verification
  5. Date format validation (YYYY-MM-DD)
- Duplicate detection via unique constraint (company_slug + date)
- UPDATE existing records or INSERT new ones

#### 5. **Configuration Management**
- Environment variables via `.env` file (local)
- Streamlit secrets (cloud deployment)
- Lazy initialization pattern for all API clients

### Key Design Patterns

#### Lazy Client Initialization
**Problem**: Streamlit Cloud deployment failed because API clients were created at module import time, before `st.secrets` was available.

**Solution**: Implemented lazy initialization pattern where clients are created on-demand:
```python
_client_instance = None

def get_client() -> OpenAI:
    global _client_instance
    if _client_instance is not None:
        return _client_instance
    # Load API key (NOW st.secrets is available)
    _client_instance = OpenAI(...)
    return _client_instance
```

**Benefits**:
- ✅ Works on Streamlit Cloud (secrets available when client created)
- ✅ Works locally (.env fallback)
- ✅ Performance optimized (client cached after first call)
- ✅ Applied to both OpenRouter and Supabase clients

#### Company Extractor Registry
Extensible configuration system (`app/company_extractors.py`) for adding new companies:
```python
COMPANY_EXTRACTORS = {
    "grab-com": {
        "name": "Grab Holdings",
        "extraction_function": "extract_grab_data_with_llm",
        "database_table": "grab_metrics",
        "has_database_push": True,
        # ... more config
    },
    # Add new companies here
}
```

## Project Structure

```
├── app/
│   ├── main.py                      # Streamlit application entry point
│   ├── client.py                    # OpenRouter client (lazy init)
│   ├── supabase_client.py           # Supabase client (singleton)
│   ├── extract_data.py              # Generic extraction functions
│   ├── grab_extraction.py           # Grab-specific extractor
│   ├── sea_group_extraction.py      # Sea Group extractor
│   ├── alibaba_extraction.py        # Alibaba extractor
│   ├── database.py                  # Supabase operations
│   ├── company_extractors.py        # Extractor registry
│   ├── public_company_ui.py         # Company-specific UI
│   ├── ui_components.py             # Shared UI components
│   ├── public_company_extraction.py # Company name detection
│   └── authentication.py            # Firebase auth (optional)
├── prompt/
│   ├── grab_com_extraction.md       # Grab extraction prompt
│   ├── sea_group_extraction.md      # Sea Group prompt
│   └── alibaba_group_extraction.md  # Alibaba prompt
├── .tmp/                            # Temporary PDF storage
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (local)
├── .gitignore                       # Git ignore patterns
├── README.md                        # This file
└── CLAUDE.md                        # Developer documentation
```

## Supported Companies

### 1. Grab Holdings (`grab-com`)
**Table**: `public.grab_metrics`

**23 metrics extracted**:
- Group financials: Revenue, incentives, net profit, EBITDA, costs
- Deliveries segment: GMV, revenue, EBITDA, costs
- Mobility segment: GMV, revenue, EBITDA, costs
- Financial Services: Revenue, EBITDA, costs
- User metrics: MTU (monthly transacting users)

### 2. Sea Group Limited (`sea-group-garena`)
**Table**: `public.seagroup_metrics`

**41 metrics extracted**:
- Group-level: 15 metrics (revenue, profit, expenses, cash)
- Digital Entertainment/Garena: 9 metrics (bookings, users, ARPU)
- E-commerce/Shopee: 7 metrics (marketplace, VAS, product revenue)
- Digital Financial Services/SeaMoney: 3 metrics (revenue, expenses, EBITDA)

### 3. Alibaba Group Holding Limited (`alibaba-group`)
**Table**: `public.alibaba_metrics`

**36 metrics extracted**:
- Consolidated financials: Revenue, profit, expenses, cash, assets
- 7 business segments (revenue + EBITDA each):
  - Taobao and Tmall Group
  - International Digital Commerce
  - Cainiao Smart Logistics
  - Cloud Intelligence Group
  - Local Services Group
  - Digital Media and Entertainment
  - All Others
- Balance sheet: Cash, assets, liabilities
- Cash flow: Operating, investing, financing
- Employee count

## Dependencies

### Core Dependencies
- `streamlit==1.39.0` - Web UI framework
- `pdfplumber==0.11.7` - PDF text extraction
- `openai` - OpenRouter API client
- `supabase==2.0.0` - Database client
- `pandas==2.3.2` - Data manipulation
- `python-dotenv==1.1.1` - Environment variables

### Supporting Libraries
- `pdfminer.six`, `pillow`, `numpy` - PDF processing
- `pypdf2` - Additional PDF utilities
- `firebase-admin` - Optional Firebase integration

See `requirements.txt` for complete list (49 packages total).

## Development

### Adding a New Company

1. **Create extraction module** (`app/new_company_extraction.py`):
   ```python
   def extract_new_company_data_with_llm(pdf_text: str, ...) -> Dict:
       # Load prompt, call LLM, parse JSON
       pass
   ```

2. **Create prompt template** (`prompt/new_company_extraction.md`):
   - Define JSON schema with all metrics
   - Specify normalization rules
   - Add examples

3. **Register in extractor config** (`app/company_extractors.py`):
   ```python
   "new-company-slug": {
       "name": "New Company",
       "extraction_function": "extract_new_company_data_with_llm",
       "database_table": "new_company_metrics",
       # ... more config
   }
   ```

4. **Create database table** in Supabase:
   - Add all metric columns
   - Set unique constraint on `(company_slug, date)`

5. **Add database functions** (`app/database.py`):
   - `push_new_company_to_supabase()`
   - `check_duplicate_new_company()`
   - `get_all_new_company_records()`

### Testing

```bash
# Local testing
streamlit run app/main.py

# Test with sample PDFs in .tmp/ directory
# Upload PDF → Extract → Verify JSON → Push to DB
```

**Recommended test cases**:
- Valid quarterly/annual reports
- Encrypted PDFs (should show error)
- Oversized PDFs (>25MB, should reject)
- PDFs with missing data (should show null values)
- Duplicate data (should show warning + UPDATE)

## Deployment

### Streamlit Cloud

1. **Push code to GitHub**
2. **Connect Streamlit Cloud** to your repository
3. **Set secrets** in Streamlit Cloud dashboard:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-..."
   SUPABASE_URL = "https://xxx.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY = "eyJhbGci..."
   ```
4. **Deploy** - Streamlit auto-deploys on push to main branch

### Environment Variables

**Local development** (`.env` file):
```env
OPENROUTER_API_KEY=your_key
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
```

**Streamlit Cloud** (secrets):
- Use the **Secrets** section in Streamlit Cloud settings
- Format: TOML key-value pairs
- The lazy initialization pattern ensures secrets load correctly

## Troubleshooting

### "Supabase not configured" error
**Cause**: Missing environment variables or typo in variable names
**Fix**: Verify `.env` has `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (note correct spelling)

### "Push to Supabase" button doesn't appear
**Cause**: Supabase package not installed
**Fix**: Run `pip install supabase==2.0.0`

### "The api_key client option must be set"
**Cause**: OpenRouter API key missing
**Fix**: Set `OPENROUTER_API_KEY` in `.env` or Streamlit secrets

### JSON parsing errors (NULL vs null)
**Cause**: LLM returns uppercase NULL which isn't valid JSON
**Fix**: Already handled by robust JSON parser with NULL→null conversion

### Duplicate records
**Behavior**: Intentional - app UPDATE existing record if same company + date
**Fix**: Change the date in extracted JSON or delete old record in Supabase

## Roadmap

### Planned Features
1. **Smart PDF Page Trimming** - 80-90% cost reduction by processing only relevant pages
2. **Multi-Company Batch Processing** - Upload multiple PDFs at once
3. **Historical Data Visualization** - Charts showing trends over time
4. **Export to Flourish** - One-click export to Flourish chart templates
5. **Automated Report Generation** - Generate editorial summaries from extracted data

See `next_features_to_build.md` for detailed implementation plans.

## Contributing

This is an internal Tech in Asia tool. For questions or improvement suggestions, contact the engineering team.

## License

Internal use only - Tech in Asia

---

**Built with**: Python, Streamlit, OpenRouter AI, Supabase
**Maintained by**: Tech in Asia Engineering Team
