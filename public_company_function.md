# Public Company Data Extraction Workflow

**Document Version:** 1.0
**Last Updated:** 2025-10-29
**Purpose:** Complete workflow documentation for public company financial data extraction feature

---

## Overview

The public company extraction feature enables Tech in Asia's editorial team to extract financial data from PDF earnings reports for pre-configured public companies using a dropdown-based selection interface.

**Key Characteristics:**
- Curated company list from JSON file
- Dropdown selection (not manual text input)
- Company slug storage for database integration
- Conditional UI rendering (PDF uploader only appears after company selection)
- Reuses 100% of PDF processing and LLM extraction pipeline

---

## Complete User Workflow

### Step 1: Application Start
**File:** [app/main.py](app/main.py)

1. User runs: `streamlit run app/main.py`
2. Application initializes session state (5 keys)
3. Routes to welcome page

**Session State Initialized:**
```python
page = "welcome"
company_type = None
extracted_data = None
selected_public_company_name = None
selected_public_company_slug = None
```

---

### Step 2: Welcome Page - Company Type Selection
**File:** [app/navigation.py](app/navigation.py) - `render_welcome_page()`

1. User sees welcome title: "Welcome to Tech in Asia's automated earnings reporting tool"
2. Dropdown shows two options: "Private company" | "Public company"
3. User selects **"Public company"**
4. User clicks **"Next"** button
5. Session state updates:
   - `company_type = "Public company"`
   - `page = "public_company"`
6. Page navigates to public company extraction page

---

### Step 3: Public Company Page - Load Companies
**File:** [app/public_company_ui.py](app/public_company_ui.py) - `render_public_company_page()`

1. Back button renders: "← Back to Selection"
2. System loads companies from [public_companies_list.json](public_companies_list.json)
3. If file not found or invalid JSON:
   - Error message displayed
   - Warning: "No public companies available"
   - Workflow stops

**JSON Structure:**
```json
{
  "Grab": "grab-com",
  "Sea Group": "sea-group-garena",
  "Alibaba Group": "alibaba-group",
  "Bukalapak": "bukalapak",
  "VNG (Vietnam)": "vng-corp"
}
```

---

### Step 4: Company Selection Dropdown
**File:** [app/public_company_ui.py](app/public_company_ui.py) - Lines 53-61

1. Dropdown renders with options:
   - **"Select"** (default)
   - Grab
   - Sea Group
   - Alibaba Group
   - Bukalapak
   - VNG (Vietnam)

2. Question: "Which public company do you need to extract data today?"

3. User selects **"Grab"** from dropdown

**Conditional Logic:**
```python
if selected_company != "Select":
    # Show PDF uploader
    st.session_state.selected_public_company_name = "Grab"
    st.session_state.selected_public_company_slug = "grab-com"
else:
    # Hide PDF uploader
    # Reset session state
```

---

### Step 5: PDF Upload Widget Appears
**File:** [app/ui_components.py](app/ui_components.py) - `render_file_uploader()`

**IMPORTANT:** PDF uploader only appears if company != "Select"

1. File uploader widget renders:
   - Label: "Upload a financial PDF"
   - Accepts: PDF files only
   - Max size: 25MB
   - Help text: "Select a PDF file (max 25MB)"

2. User clicks uploader and selects PDF file

3. File validation checks:
   - **File type:** Must be "application/pdf"
   - **File size:** Must be ≤ 25MB
   - If validation fails: Error message displayed, stop

---

### Step 6: PDF Processing - Save and Metadata
**File:** [app/ui_components.py](app/ui_components.py) - `process_pdf_file()`
**File:** [app/pdf_utils.py](app/pdf_utils.py)

1. **Save PDF to temporary directory:**
   - Creates `.tmp/` folder if not exists
   - Filename: `YYYYMMDD_HHMMSS_original_name.pdf`
   - Example: `.tmp/20251029_143052_grab_earnings.pdf`

2. **Extract PDF metadata:**
   - Opens PDF with `pdfplumber`
   - Counts total pages
   - Checks if text is extractable
   - Returns: `{"page_count": 15, "has_text": True, "success": True}`

3. **Display page count:**
   - Caption: "Detected 15 page(s). Click the button below to extract financial metrics."

4. **Render extraction button:**
   - Button: "Extract Financial Data" (primary type)

---

### Step 7: Text Extraction from PDF
**File:** [app/pdf_utils.py](app/pdf_utils.py) - `extract_full_pdf_text()`

1. User clicks **"Extract Financial Data"** button

2. Spinner appears: "Extracting text from PDF..."

3. Text extraction process:
   - Opens PDF with `pdfplumber`
   - Iterates through all 15 pages
   - Extracts text from each page: `page.extract_text()`
   - Concatenates with double newlines: `page1_text\n\npage2_text\n\n...`

4. Returns full PDF text as single string

5. Validation:
   - If text is empty: Error message, stop
   - If successful: Proceed to LLM extraction

---

### Step 8: LLM Extraction - 3-Statement Prompt Loading
**File:** [app/extract_data.py](app/extract_data.py) - `extract_public_company_data_with_llm()`

1. **Load public company prompt:**
   - Reads [prompt/3statement_extraction_prompt.md](prompt/3statement_extraction_prompt.md)
   - Loads entire prompt text (not parsed into sections)
   - No caching (loads on each request)

2. **Prompt structure:**
   - **System prompt:** "You are a financial data extraction expert specialized in extracting comprehensive financial statements from earnings reports."
   - **User prompt format:**
     ```python
     user_prompt = f"""Company: {company_hint}

     PDF Text:
     {pdf_text}

     {prompt_text}"""
     ```

**Extraction Instructions (from 3-statement prompt):**
- Extract **THREE COMPLETE FINANCIAL STATEMENTS** for ONE quarter
- Normalize all values to **millions** (e.g., $819M → 819, $7.6B → 7600)
- Use negative numbers for losses/decreases
- Use `null` for missing values (not 0, not "N/A")
- Detect quarter from document (e.g., "Q2 2025" → "2025-04-01")

**Statements to Extract:**
1. **Profit or Loss Statement** (Consolidated Statement of Profit/Loss)
   - Revenue metrics (total_revenue, cost_of_revenue, gross_profit)
   - Operating expenses (sales_marketing, research_development, general_admin)
   - Operating income/loss
   - Other income/expenses
   - Net income/loss

2. **Balance Sheet Statement** (Consolidated Statement of Financial Position)
   - Assets (current and non-current)
   - Liabilities (current and non-current)
   - Equity metrics

3. **Cash Flows Statement** (Consolidated Statement of Cash Flows)
   - Operating activities
   - Investing activities
   - Financing activities
   - Net change in cash

---

### Step 9: LLM API Call
**File:** [app/extract_data.py](app/extract_data.py)
**File:** [app/client.py](app/client.py)

1. Spinner appears: "Analyzing with deepseek/deepseek-chat-v3.1:free..."

2. **Call OpenRouter API:**
   ```python
   client.chat.completions.create(
       model="deepseek/deepseek-chat-v3.1:free",
       messages=[
           {"role": "system", "content": system_prompt},
           {"role": "user", "content": user_prompt}
       ],
       temperature=0.0,   # Deterministic responses
       max_tokens=50000   # Increased for comprehensive 3-statement extraction
   )
   ```

3. **API client details:**
   - Base URL: `https://openrouter.ai/api/v1`
   - API Key: From `OPENROUTER_API_KEY` environment variable
   - Singleton instance in [app/client.py](app/client.py)

4. API returns response with JSON text containing 3 complete financial statements

---

### Step 10: JSON Response Parsing
**File:** [app/extract_data.py](app/extract_data.py) - `_parse_llm_json_response()`

1. **Clean LLM response:**
   - Remove markdown code blocks: \`\`\`json ... \`\`\`
   - Remove common prefixes: "Here's the JSON:", "Result:", etc.
   - Handle truncated responses (missing closing \`\`\`)

2. **Parse JSON with fallback strategies:**
   - **Strategy 1:** Try parsing cleaned text directly
   - **Strategy 2:** Extract JSON block using bracket matching
   - **Strategy 3:** Raise JSONDecodeError if both fail

3. **Success rate:** ~99% with fallback strategies

4. **If parsing fails:**
   - Error message: "Failed to parse LLM response as JSON"
   - Returns: `{"error": "Invalid JSON response from LLM"}`

---

### Step 11: Inject Company Slug and Store Results
**File:** [app/ui_components.py](app/ui_components.py) - `process_pdf_file()`

1. **Check for errors:**
   - If `"error"` key in financial_data:
     - Display error message
     - Stop processing

2. **Inject company_slug into extraction results:**
   - If `company_slug` parameter provided (public company workflow):
     ```python
     if "error" not in financial_data:
         financial_data["company_slug"] = "grab-com"
     ```
   - This links extracted data to the company in the database

3. **Store results in session state:**
   ```python
   st.session_state.extracted_data = {
       "company_slug": "grab-com",
       "date": "2025-04-01",
       "profit_or_loss_statement": {
           "total_revenue": 819,
           "cost_of_revenue": 450,
           "gross_profit": 369,
           ...
       },
       "balance_sheet_statement": {
           "total_assets": 5200,
           "total_liabilities": 3100,
           "total_equity": 2100,
           ...
       },
       "cash_flows_statement": {
           "net_cash_operating": 180,
           "net_cash_investing": -50,
           "net_cash_financing": -30,
           ...
       },
       "_aliases": {
           "revenue": "total_revenue",
           "net_income": "net_income_loss"
       }
   }
   ```

4. **Success message:** "Financial data extracted successfully."

5. Streamlit re-renders page with results

---

### Step 12: Display Results (No Download Button)
**File:** [app/ui_components.py](app/ui_components.py) - `render_public_company_results()`

1. **Check for extracted data:**
   - If `st.session_state.extracted_data` exists, proceed
   - If None, show nothing

2. **Display JSON viewer:**
   - Subheader: "Extracted Financial Data"
   - Expandable JSON tree with all 3 financial statements + company_slug

**Example Output:**
```json
{
  "company_slug": "grab-com",
  "date": "2025-04-01",
  "profit_or_loss_statement": {
    "total_revenue": 819,
    "cost_of_revenue": 450,
    "gross_profit": 369,
    "sales_marketing": 120,
    "research_development": 80,
    "general_admin": 60,
    "total_operating_expenses": 260,
    "operating_income_loss": 109,
    "interest_income": 15,
    "interest_expense": -5,
    "other_income_expense": 3,
    "income_before_tax": 122,
    "income_tax_expense": -22,
    "net_income_loss": 100
  },
  "balance_sheet_statement": {
    "cash_equivalents": 800,
    "accounts_receivable": 200,
    "inventory": 50,
    "total_current_assets": 1200,
    "property_equipment": 500,
    "intangible_assets": 3000,
    "total_non_current_assets": 4000,
    "total_assets": 5200,
    "accounts_payable": 300,
    "short_term_debt": 100,
    "total_current_liabilities": 600,
    "long_term_debt": 2000,
    "total_non_current_liabilities": 2500,
    "total_liabilities": 3100,
    "share_capital": 1500,
    "retained_earnings": 600,
    "total_equity": 2100,
    "total_liabilities_equity": 5200
  },
  "cash_flows_statement": {
    "net_income_loss": 100,
    "depreciation_amortization": 80,
    "changes_working_capital": 20,
    "net_cash_operating": 200,
    "capital_expenditures": -50,
    "acquisitions": -100,
    "net_cash_investing": -150,
    "debt_proceeds": 50,
    "debt_repayments": -30,
    "share_issuance": 0,
    "dividends_paid": -20,
    "net_cash_financing": 0,
    "net_change_cash": 50,
    "cash_beginning": 750,
    "cash_ending": 800
  },
  "_aliases": {
    "revenue": "total_revenue",
    "net_income": "net_income_loss",
    "total_cash": "cash_equivalents"
  }
}
```

3. **Info message (instead of download button):**
   - Message: "Data ready for database upload. Download feature coming soon."
   - Explanation: Results will be written to Supabase in a future update
   - No download button rendered (unlike private company workflow)

---

## File Structure and Responsibilities

### Core Application Files

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| [app/main.py](app/main.py) | 71 | Entry point, routing | `initialize_session_state()`, `main()` |
| [app/navigation.py](app/navigation.py) | 44 | Welcome page, back button | `render_welcome_page()`, `render_back_button()` |
| [app/public_company_ui.py](app/public_company_ui.py) | 76 | Public company workflow | `load_public_companies_list()`, `render_public_company_page()` |
| [app/ui_components.py](app/ui_components.py) | 137 | Shared UI utilities | `render_file_uploader()`, `process_pdf_file()`, `render_results()` |

### Utility Modules

| File | Lines | Purpose | Key Functions |
|------|-------|---------|---------------|
| [app/pdf_utils.py](app/pdf_utils.py) | 92 | PDF operations | `save_temp_file()`, `extract_full_pdf_text()`, `get_pdf_info()` |
| [app/extract_data.py](app/extract_data.py) | 183 | LLM extraction | `extract_financial_data_with_llm()`, `get_prompt_config()` |
| [app/client.py](app/client.py) | 19 | OpenRouter client | `client` (singleton instance) |
| [app/config.py](app/config.py) | 36 | Constants | All configuration constants |

### Data Files

| File | Lines | Purpose |
|------|-------|---------|
| [public_companies_list.json](public_companies_list.json) | 7 | Company name → slug mapping |
| [prompt/extract_data_prompt.md](prompt/extract_data_prompt.md) | 36 | LLM prompt template |

---

## Session State Keys

| Key | Type | Default | Purpose | Set By | Used By |
|-----|------|---------|---------|--------|---------|
| `page` | str | "welcome" | Current page routing | navigation, main | main |
| `company_type` | str\|None | None | Selected company type | navigation | navigation, main |
| `extracted_data` | dict\|None | None | LLM extraction results | ui_components | ui_components |
| `selected_public_company_name` | str\|None | None | Company display name | public_company_ui | Future database integration |
| `selected_public_company_slug` | str\|None | None | Company database slug | public_company_ui | Future database integration |

**Session State Lifecycle:**
```
Start → All keys initialized to defaults
Welcome Page → company_type set, page set to "public_company"
Public Page → Company selection → name and slug stored
PDF Upload → Extraction → extracted_data stored
Results Display → Read extracted_data from session state
Back Button → page reset to "welcome", company_type cleared
```

---

## Function Call Graph

```
main()
├── initialize_session_state()
└── [Routing]
    ├── render_welcome_page()
    │   ├── st.selectbox()
    │   └── st.button() → st.rerun()
    │
    └── render_public_company_page()
        ├── render_back_button()
        ├── load_public_companies_list()
        │   └── json.load()
        ├── st.selectbox()
        ├── render_file_uploader()
        │   ├── validate_uploaded_file()
        │   └── process_pdf_file()
        │       ├── save_temp_file()
        │       ├── get_pdf_info()
        │       ├── extract_full_pdf_text()
        │       └── extract_financial_data_with_llm()
        │           ├── get_prompt_config()
        │           ├── client.chat.completions.create()
        │           └── _parse_llm_json_response()
        └── render_results()
            ├── st.json()
            └── st.download_button()
```

---

## Configuration Constants

### LLM Settings
**File:** [app/config.py](app/config.py)

- `MODEL_NAME = "deepseek/deepseek-chat-v3.1:free"` - OpenRouter model ID
- `TEMPERATURE = 0.0` - Deterministic responses (no randomness)
- `MAX_TOKENS = 2000` - Maximum response tokens (sufficient for 2 years)

### File Upload Settings
- `MAX_FILE_SIZE_MB = 25` - Maximum PDF size (in MB)

### UI Text
- `PUBLIC_COMPANY_DROPDOWN_LABEL = "Which public company do you need to extract data today?"`
- `UPLOAD_WIDGET_LABEL = "Upload a financial PDF"`
- `UPLOAD_BUTTON_LABEL = "Extract Financial Data"`
- `DOWNLOAD_BUTTON_LABEL = "Download JSON"`
- `DOWNLOAD_FILENAME = "financial_data.json"`

### Data Files
- `PUBLIC_COMPANIES_LIST_FILE = "public_companies_list.json"`

---

## Error Handling

### 1. Companies List Not Found
**Handler:** `public_company_ui.load_public_companies_list()`

```python
try:
    with open(json_path, "r") as f:
        companies_dict = json.load(f)
except FileNotFoundError:
    st.error("Public companies list file not found: {path}")
    return {}
```

**User sees:** Error message + warning "No public companies available"

---

### 2. Invalid JSON in Companies List
**Handler:** `public_company_ui.load_public_companies_list()`

```python
except json.JSONDecodeError as exc:
    st.error("Invalid JSON in public companies list: {exc}")
    return {}
```

**Recovery:** Fix JSON syntax, restart app

---

### 3. File Too Large (>25MB)
**Handler:** `ui_components.validate_uploaded_file()`

```python
if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
    st.error("File too large: {size}. Maximum allowed size is 25MB.")
    return False
```

**User action:** Upload smaller file or compress PDF

---

### 4. Invalid File Type (Not PDF)
**Handler:** `ui_components.validate_uploaded_file()`

```python
if uploaded_file.type != "application/pdf":
    st.error("Invalid file type: {type}. Please upload a PDF file.")
    return False
```

**User action:** Upload PDF file only

---

### 5. Failed to Extract PDF Text
**Handler:** `pdf_utils.extract_full_pdf_text()`

```python
except Exception as exc:
    st.error(f"Error extracting PDF text: {exc}")
    return ""
```

**Possible causes:** Corrupted PDF, image-based PDF (no text), encrypted PDF

---

### 6. Invalid JSON Response from LLM
**Handler:** `extract_data._parse_llm_json_response()`

**Fallback strategies:**
1. Strip markdown code blocks
2. Remove common prefixes
3. Extract JSON block using bracket matching
4. Raise error if all fail

**User sees:** "Failed to parse LLM response as JSON: {details}"

---

### 7. OpenRouter API Failure
**Handler:** `extract_data.extract_financial_data_with_llm()`

```python
except Exception as exc:
    st.error(f"LLM extraction failed: {exc}")
    return {"error": f"LLM error: {exc}"}
```

**Possible causes:** Invalid API key, network error, rate limit, model unavailable

---

## Key Implementation Details

### 1. Conditional PDF Uploader Rendering

**Logic:**
```python
if selected_company != "Select":
    # Show PDF uploader
    render_file_uploader(company_hint=selected_company)
    render_results()
else:
    # Hide PDF uploader
    # Reset session state
    st.session_state.selected_public_company_name = None
    st.session_state.selected_public_company_slug = None
```

**Why:** Prevents accidental uploads before company selection

---

### 2. Prompt Caching Strategy

**Problem:** Re-reading markdown file on every extraction is inefficient

**Solution:**
```python
_PROMPT_CACHE: Optional[Dict[str, str]] = None

def get_prompt_config():
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        # Load from file (first call only)
        _PROMPT_CACHE = parse_markdown_file()
    return _PROMPT_CACHE
```

**Benefit:** File read only once per Streamlit session

---

### 3. Session State Persistence

**What persists across page re-renders:**
- `extracted_data` - Extraction results (prevents data loss)
- `selected_public_company_name` - Company name
- `selected_public_company_slug` - Company slug

**What doesn't persist:**
- Uploaded file object (Streamlit limitation)
- Temporary PDF file (remains in `.tmp/` until manual cleanup)

---

### 4. JSON Parsing Fallbacks

**Strategy 1:** Strip markdown code blocks
```python
if text.startswith('```json') and text.endswith('```'):
    text = text[7:-3].strip()
```

**Strategy 2:** Remove common prefixes
```python
for prefix in ["Here's the JSON:", "Result:", ...]:
    if text.startswith(prefix):
        text = text[len(prefix):].strip()
```

**Strategy 3:** Extract embedded JSON block
```python
# Find first { and matching }
# Return substring
```

**Success rate:** ~99%

---

## Quick Reference: Modifying Workflow

| Task | File | What to Change |
|------|------|----------------|
| Add new company | [public_companies_list.json](public_companies_list.json) | Add: `"Company Name": "company-slug"` |
| Change dropdown question | [app/config.py](app/config.py):25 | Update `PUBLIC_COMPANY_DROPDOWN_LABEL` |
| Change extraction prompt | [prompt/extract_data_prompt.md](prompt/extract_data_prompt.md) | Edit system or template sections |
| Change LLM model | [app/config.py](app/config.py):7 | Update `MODEL_NAME` |
| Change file size limit | [app/config.py](app/config.py):4 | Update `MAX_FILE_SIZE_MB` |
| Add new session state key | [app/main.py](app/main.py):12-24 | Add in `initialize_session_state()` |
| Modify dropdown UI | [app/public_company_ui.py](app/public_company_ui.py):41-76 | Edit `render_public_company_page()` |
| Change button labels | [app/config.py](app/config.py):33-34 | Update constants |

---

## Future Enhancements

### 1. Database Integration
**Status:** Company slug stored in session state but not used yet

**Implementation:**
- Create `app/database.py` module
- Add Firestore connection
- Write extraction data with company slug as `company_id`
- Add duplicate detection before write

**Files to modify:**
- [app/ui_components.py](app/ui_components.py):100 - Add database write call
- Create [app/database.py](app/database.py) - Database functions

---

### 2. Company Metadata Expansion
**Status:** Simple name→slug mapping

**Enhanced structure:**
```json
{
  "companies": [
    {
      "name": "Grab",
      "slug": "grab-com",
      "ticker": "GRAB",
      "exchange": "NASDAQ",
      "country": "Singapore",
      "sector": "Technology",
      "default_currency": "SGD"
    }
  ]
}
```

**Benefits:** Richer information, auto-currency detection, ticker display

---

### 3. Smart Page Trimming
**Status:** Sends entire PDF to LLM (expensive)

**Enhancement:** Filter pages by financial keywords before LLM

**Implementation:**
- Detect keywords: "revenue", "profit", "cash flow"
- Keep pages with high keyword scores
- Send only relevant pages to LLM

**Benefit:** 80-90% cost reduction

---

### 4. Multi-Year Extraction
**Status:** Fixed to TWO YEARS

**Enhancement:** Dynamic year count based on user input

**Implementation:**
- Add slider: "How many years to extract?" (1-5)
- Update prompt template with `{num_years}` placeholder
- Increase `MAX_TOKENS` accordingly

---

### 5. Batch Processing
**Status:** One PDF at a time

**Enhancement:** Upload multiple PDFs, process in batch

**Implementation:**
- Enable `accept_multiple_files=True`
- Loop through uploaded files
- Display results in tabs
- Download all as ZIP

---

## Testing Checklist

- [ ] JSON file loads without errors
- [ ] Dropdown displays all companies
- [ ] "Select" option resets session state
- [ ] Selecting company updates session state (name + slug)
- [ ] PDF uploader only appears after company selection
- [ ] File validation works (type, size)
- [ ] Page count displays correctly
- [ ] Extraction uses selected company as hint
- [ ] Results display correctly (JSON viewer)
- [ ] Download button works
- [ ] Adding company to JSON updates dropdown
- [ ] Back button returns to welcome page
- [ ] Session state persists across interactions
- [ ] Error messages display for invalid JSON
- [ ] API key check prevents access without key

---

## Document Metadata

**Version:** 1.0
**Created:** 2025-10-29
**Last Updated:** 2025-10-29 10:57 PST
**Branch:** feature/public-company-extraction
**Maintained By:** Tech in Asia Engineering Team

---

**END OF WORKFLOW DOCUMENT**
