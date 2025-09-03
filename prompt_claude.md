# Claude Code Prompt: Add Automatic Firestore Data Saving

## Task
Create a function to automatically save validated financial data to Firestore after successful LLM extraction.

## Requirements

### 1. Create Save Function
Add a new function called `save_financial_data_to_firestore(financial_data: Dict, db, uploaded_filename: str) -> bool`:
- Takes the financial data dictionary from LLM extraction
- Takes the Firestore database client and original filename
- Returns True if successful, False if failed
- Handles errors gracefully with try/except

### 2. Data Validation Function
Add a validation function `validate_financial_data(financial_data: Dict) -> bool`:
- Check if company_name is not "not_found"
- Check if either revenue OR net_profit has valid data (not "not_found")
- Return True if data is worth saving, False if mostly empty
- Log validation results for debugging

### 3. Data Structure Design
Structure data in Firestore as:
```
companies/{company_name}/reports/{report_id}
```
Where report_id combines period and timestamp for uniqueness (e.g., "Q2_2024_20250901_143022").

### 4. Document Fields
Save these fields to each document:
- All financial data from LLM (revenue, net_profit, etc.)
- Metadata: upload_timestamp, original_filename, report_period
- Company info: company_name, report_type
- Processing info: model_used="gemini-1.5-flash", extraction_success=True

### 5. Automatic Integration
Modify the existing LLM extraction workflow:
- After successful `extract_financial_data_with_llm()` call
- Automatically validate the extracted data
- If validation passes: initialize Firebase and save data
- Show "✅ Data saved successfully!" message on success
- Show validation/save errors if they occur
- NO manual save button needed - fully automatic

### 6. Error Handling
Handle scenarios gracefully:
- Data validation failures: "⚠️ Extracted data insufficient for saving"
- Database connection failures: "❌ Failed to save to database"
- Invalid data formats or network issues
- Continue showing extraction results even if save fails

## Integration Location
Modify the LLM extraction success section in `main()` function where it currently shows the extracted data results.

## Current Workflow Context
```python
if st.button("📊 Extract Financial Data", type="primary"):
    # ... existing extraction code ...
    if "error" not in financial_data:
        st.success("✅ Financial data extracted successfully!")
        # ADD AUTOMATIC SAVE HERE
        # ... existing display code ...
```

## Expected Outcome
After successful LLM extraction, the app will automatically validate and save the data to Firestore, showing clear success/failure messages to the user without requiring manual intervention.