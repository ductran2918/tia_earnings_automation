# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python-based earnings automation tool for **Tech in Asia's editorial team** to automate earnings reporting from PDFs. The application extracts comprehensive financial data from PDF reports using LLM (OpenRouter API with DeepSeek model), with Streamlit for the web interface.

## Current Implementation Status

### ✅ Implemented Features

**Three-Page Navigation Flow ([app/main.py](app/main.py))**
1. **Welcome page**: Company type selection (Private/Public)
2. **Private company page**: Full PDF extraction workflow with table conversion
3. **Public company page**: Placeholder (coming soon)

**Core Data Pipeline**
- PDF upload with validation (type check, 25MB limit)
- PDF text extraction using `pdfplumber`
- LLM-based financial data extraction via OpenRouter
- SGD-to-USD currency conversion with historical exchange rates
- Multi-year financial table generation (Revenue/Profit, Cash Flow)
- JSON download and table display

**Modular Architecture ([app/](app/))**

The codebase follows a functional module structure with clear separation of concerns:

- **[config.py](app/config.py)**: Centralized constants (model settings, UI strings, limits) - no dependencies on other app modules
- **[client.py](app/client.py)**: OpenRouter API client singleton - depends only on `openai` and `python-dotenv`
- **[pdf_utils.py](app/pdf_utils.py)**: PDF file operations (save, metadata, text extraction) - depends on `pdfplumber` only
- **[extract_data.py](app/extract_data.py)**: LLM prompt loading and financial data extraction - imports `client.py`
- **[convert_currency.py](app/convert_currency.py)**: SGD currency detection and USD conversion - standalone function
- **[table_utils.py](app/table_utils.py)**: DataFrame generation for financial tables - depends on `pandas` only
- **[ui_components.py](app/ui_components.py)**: Page rendering logic - orchestrates all above modules
- **[main.py](app/main.py)**: Entry point and page router - imports `ui_components` and `config`

**Import hierarchy**: `main.py` → `ui_components.py` → `{pdf_utils, extract_data, convert_currency, table_utils}` → `{client, config}`

**Data Extraction Capabilities**
- Multi-year financial data (3 years minimum from prompt configuration)
- Revenue, profit before tax, cash flow metrics per year
- Company name, currency detection
- Evidence text with source quotes from PDF
- SGD-to-USD conversion with quarter-year exchange rate lookup

## Development Setup

### Prerequisites
- Python 3.8+ (currently running Python 3.13)
- OpenRouter API key
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
```

### Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application (default port 8501)
streamlit run app/main.py

# Run with custom port
streamlit run app/main.py --server.port 8502

# View Streamlit logs for debugging
streamlit run app/main.py --logger.level=debug
```

### Key Dependencies

- **openai** (1.51.0): Used with OpenRouter base URL for LLM API calls
- **streamlit** (1.39.0): Web interface framework
- **pdfplumber** (0.11.7): PDF text extraction (layout-aware)
- **pandas** (2.3.2): DataFrame operations for financial tables
- **python-dotenv** (1.1.1): Environment variable management

## Architecture

### Data Flow Pipeline
The application follows this processing flow:
1. **Upload**: User uploads PDF via Streamlit file uploader
2. **Storage**: PDF saved to `.tmp/` with timestamp prefix
3. **Extraction**: `pdfplumber` extracts raw text from all pages
4. **LLM Processing**: Text sent to OpenRouter API (DeepSeek model) with structured prompt
5. **Parsing**: JSON response cleaned and parsed (handles markdown code blocks, prefixes)
6. **Currency Conversion**: Optional SGD→USD conversion if detected
7. **Table Generation**: DataFrames created for Revenue/Profit and Cash Flow tables
8. **Output**: JSON download + table display in Streamlit

### Multi-Page Navigation System
The application uses Streamlit session state for page routing ([app/main.py](app/main.py)):

```python
# Session state manages current page and company type
st.session_state.page = "welcome" | "private_company" | "public_company"
st.session_state.company_type = "Private company" | "Public company" | None
```

**Page flow**: Welcome → Company type selection → Company-specific extraction page

### OpenRouter API Client Singleton ([app/client.py](app/client.py))
The `client` object is a module-level singleton that wraps the OpenAI SDK with OpenRouter's base URL:
```python
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
```
**Important**: All LLM calls should import and use this shared `client` instance. Do not create new OpenAI client instances elsewhere.

### LLM Prompt Management ([app/extract_data.py](app/extract_data.py))
Prompts are stored as markdown files in [prompt/](prompt/) directory with section headers:
- `## system`: System instructions for LLM (role definition)
- `## template`: User message template with `{company_hint}` and `{pdf_text}` placeholders

**Critical implementation detail**: `get_prompt_config()` uses module-level cache (`_PROMPT_CACHE`) to avoid re-reading markdown files on every extraction. Prompts are parsed once and reused across sessions.

**Prompt structure in [prompt/extract_data_prompt.md](prompt/extract_data_prompt.md)**:
- Instructs LLM to extract **TWO YEARS** of data (year_1, year_2)
- Enforces raw numbers (not "1B" or "1000M")
- Returns 7 metrics per year: revenue, profit_before_tax, profit_after_tax, net_cash_operating, net_cash_investing, net_cash_financing, cash_end_of_year
- Uses `null` for missing values (not 0 or "N/A")
- Returns JSON with `year_1`, `year_2`, `currencies`, `company_name`, `report_type` keys

### Currency Conversion Pipeline ([app/convert_currency.py](app/convert_currency.py))
1. **Detection**: Check for SGD indicators (S$, SGD, company name with "Pte Ltd", "Singapore")
2. **Lookup**: Load `sgd_usd_rates_json.json` for historical exchange rates by quarter-year
3. **Conversion**: Multiply numerical financial values by matched exchange rate
4. **Transformation**: Update `currencies` field to reflect USD and preserve original structure

**Exchange rate file format**:
```json
{
  "Q1 2023": 0.75,
  "Q2 2023": 0.74
}
```

### Table Generation ([app/table_utils.py](app/table_utils.py))
Two table types generated from extracted JSON:
1. **Revenue/Profit table**: Iterates over `year_*` keys to build rows with `year`, `revenue`, `profit_before_tax`
2. **Cash Flow table**: Extracts `net_cash_operating`, `net_cash_investing`, `net_cash_financing`, `cash_end_of_year`

Both tables auto-sort by year (ascending) using temporary `Year_int` column for numeric comparison.

### Temporary File Management
Uploaded PDFs saved to `.tmp/` with timestamp prefix: `YYYYMMDD_HHMMSS_{original_filename}.pdf`
- Created on-demand via `Path(".tmp").mkdir(exist_ok=True)`
- No automatic cleanup (manual deletion required)

## Configuration

### Environment Variables

Required in `.env` file:

- `OPENROUTER_API_KEY`: OpenRouter API key for LLM processing

### LLM Settings

Configured in [app/config.py](app/config.py):

- **Model**: `deepseek/deepseek-chat-v3.1:free` (OpenRouter free tier)
- **Temperature**: `0.0` (deterministic responses for financial data)
- **Max tokens**: `2000` (sufficient for TWO YEARS of financial data)

To change the model, update `MODEL_NAME` in [app/config.py](app/config.py:7). Ensure the model is available via OpenRouter.

### Exchange Rate Data

File `sgd_usd_rates_json.json` must exist in project root with quarterly exchange rates in this format:

```json
{
  "Q1 2023": 0.7450,
  "Q2 2023": 0.7425,
  "Q3 2023": 0.7392,
  "Q4 2023": 0.7520
}
```

Exchange rates are used only when SGD currency is detected. The system matches the year from extracted data to find the appropriate quarter.

## Key Implementation Details

### Error Handling Strategy

**LLM JSON parsing** ([app/extract_data.py](app/extract_data.py)):

- Strips markdown code blocks (\`\`\`json, \`\`\`) from LLM responses
- Handles truncated responses (missing closing \`\`\`)
- Removes common LLM prefixes ("Here's the JSON:", "Result:", etc.)
- Falls back to raw text on JSON parse errors with user notification

**PDF validation** ([app/ui_components.py](app/ui_components.py)):

- File type check: `uploaded_file.type == "application/pdf"`
- Size limit: `MAX_FILE_SIZE_MB * 1024 * 1024` (25MB default)
- PDF corruption check via `pdfplumber.open()` exception handling

### Session State Management

Critical session state keys in [app/main.py](app/main.py):

```python
st.session_state.page          # "welcome" | "private_company" | "public_company"
st.session_state.company_type  # "Private company" | "Public company" | None
st.session_state.extracted_data # Stores LLM extraction results
```

**Important**: `extracted_data` persists across button clicks to prevent data loss during UI interactions (e.g., currency conversion buttons).

## Debugging and Testing

### Testing LLM Extraction Locally
To test prompt changes without running the full Streamlit app:

```python
# In a Python REPL or test script
from app.extract_data import extract_financial_data_with_llm
from app.pdf_utils import extract_full_pdf_text

# Extract text from PDF
pdf_text = extract_full_pdf_text("path/to/test.pdf")

# Test extraction
result = extract_financial_data_with_llm(
    pdf_text=pdf_text,
    company_hint="Company Name",
    model_name="deepseek/deepseek-chat-v3.1:free",
    temperature=0.0,
    max_tokens=2000
)

print(json.dumps(result, indent=2))
```

### Common Issues and Solutions

**Issue**: JSON parsing fails with "Invalid JSON response from LLM"
- **Cause**: LLM returns non-JSON text or malformed JSON
- **Solution**: Check `_strip_markdown_code_blocks()` logic in [app/extract_data.py](app/extract_data.py:70-101); may need to add new prefix patterns to remove

**Issue**: Currency conversion not detecting SGD
- **Cause**: Detection logic in [app/convert_currency.py](app/convert_currency.py) doesn't match document format
- **Solution**: Add new SGD indicators to the detection function

**Issue**: Tables showing incorrect years or missing data
- **Cause**: LLM extracted data with unexpected `year_*` keys or null values
- **Solution**: Inspect `st.session_state.extracted_data` in Streamlit debugger; verify prompt instructions in [prompt/extract_data_prompt.md](prompt/extract_data_prompt.md)

**Issue**: PDF text extraction returns empty or garbled text
- **Cause**: PDF is image-based (scanned) or uses complex layouts
- **Solution**: `pdfplumber` doesn't support OCR; consider adding OCR preprocessing or manual text input option

### Viewing Session State
Add this to any page to debug session state:
```python
st.write("Debug Session State:", st.session_state)
```

## Next Development Priorities

See [next_features_to_build.md](next_features_to_build.md) for detailed roadmap. Summary:

1. **Smart PDF Page Trimming** (HIGH): Reduce LLM costs by 80-90% via keyword-based page filtering
2. **Enhanced LLM Prompt** (HIGH): Extract 20+ financial metrics instead of current subset
3. **Database Integration** (MEDIUM): Firebase Firestore for centralized storage
4. **Duplicate Detection** (LOW): Prevent reprocessing existing company/period combinations
