# Financial Data Extraction App - Next Features Roadmap

## Development Priority Order

Based on our discussion, here are the **4 key features to build next** to complete your financial data extraction system:

---

### 1. **Smart PDF Page Trimming** (Immediate cost savings)
**Priority:** HIGH - Implement first for immediate 80-90% cost reduction

**Objective:** Reduce LLM processing costs by only analyzing relevant pages

**Implementation:**
- Create function to scan each PDF page for financial keywords
- Target keywords: "Revenue", "Net Income", "Balance Sheet", "Cash Flow", "P&L", "Profit and Loss"
- Only process pages containing these financial terms
- Fallback mechanism: Process first 5 pages if no keywords are detected
- Integration with existing `pdfplumber` library

**Expected Outcome:** 
- 80-90% reduction in LLM token usage
- Faster processing times
- Lower API costs per PDF

---

### 2. **Enhanced LLM Prompt** (Complete data extraction)
**Priority:** HIGH - Expand before database integration

**Objective:** Extract all ~20 financial data points instead of current 2 metrics

**Implementation:**
- Expand current prompt from revenue + net profit to comprehensive financial metrics
- Include: total costs, operating profit, EBITDA, assets, liabilities, equity, cash flow metrics
- Maintain structured JSON output format
- Handle missing data gracefully with "not_found" values
- Test with sample PDFs from different companies

**Expected Outcome:**
- Complete financial dataset per company
- Consistent data structure for database storage
- Avoid future schema migrations

---

### 3. **Database Integration** (Centralized storage)
**Priority:** MEDIUM - Foundation for duplicate detection

**Objective:** Store extracted financial data in Firebase Firestore

**Implementation:**
- Install `firebase-admin` Python SDK
- Set up Firebase project and service account credentials
- Design data structure: `company → year → quarter → financial_metrics`
- Add "Save to Database" functionality after successful LLM extraction
- Handle save success/failure scenarios with user feedback
- Environment variable for Firebase configuration

**Expected Outcome:**
- Centralized storage for 300 companies across multiple years
- Foundation for user data retrieval
- Enable duplicate detection system

---

### 4. **Duplicate Detection System** (Resource optimization)
**Priority:** LOW - Build after database integration

**Objective:** Prevent processing duplicate financial statements

**Implementation:**
- Pre-processing check: Query database for existing company + period combinations
- Smart company name matching (handle variations like "Grab Holdings" vs "Grab Ltd")
- User notification: "Company X FY2024 data already exists"
- User options: Skip processing, view existing data, override with new extraction
- Integration point: Check before LLM processing to save costs

**Expected Outcome:**
- Avoid duplicate work across team members
- Resource optimization for 300+ companies
- Better user experience with existing data visibility

---

## Implementation Questions to Address

### General Development:
1. **Timeline:** How much time can you allocate per week for these features?
2. **Testing:** Do you have sample PDFs from different companies for testing?
3. **Team coordination:** Should duplicate detection track which user uploaded what?

### Smart PDF Trimming:
1. **Keyword strategy:** Comprehensive financial terms vs essential keywords only?
2. **Page selection:** Include adjacent pages if keywords found?
3. **Fallback mechanism:** Process first N pages if no keywords detected?

### Enhanced LLM Prompt:
1. **Missing data handling:** How to handle metrics not available in certain reports?
2. **Data consistency:** Same 20 data points for all companies or industry-specific variations?

### Database Integration:
1. **Save trigger:** Automatic save after extraction or manual "Save" button?
2. **Data review:** Should users review/edit extracted data before saving?
3. **Firebase setup:** Need help with Google Cloud configuration?

### Duplicate Detection:
1. **Matching strictness:** Exact company name match or fuzzy matching?
2. **Override permissions:** Should all users be able to override existing data?

---

## Technology Stack
- **Current:** Python, Streamlit, pdfplumber, Google Gemini 1.5 Flash
- **New additions:** Firebase Admin SDK, enhanced keyword detection
- **Database:** Firebase Firestore (managed, cost-effective for gradual growth)

## Cost Optimization Benefits
- **Smart trimming:** 80-90% reduction in LLM token usage
- **Duplicate detection:** Eliminate redundant processing
- **Firebase Firestore:** Free tier covers estimated usage (300 companies × 20 data points × 4 reports/year)
- **Stick with Gemini 1.5 Flash:** Already most cost-effective model at $0.075/1M tokens