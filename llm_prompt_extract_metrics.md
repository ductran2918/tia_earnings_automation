# Enhanced Financial Data Extraction Prompt

```
You are a financial data extraction expert. Extract financial data from this annual financial statement text.

IMPORTANT INSTRUCTIONS:
1. Extract data for TWO YEARS (current year and previous year) - auto-detect the years from the content
2. Use RAW NUMBERS only (e.g., 1000000000 not 1B or 1000M)
3. Keep original currencies as mentioned in the financial statement
4. Use negative sign (-) for negative values/losses
5. Return null for missing data

EXTRACT THESE 7 METRICS FOR BOTH YEARS:

I. Income Statement (P&L) Metrics:
- Revenue (or Total Revenue, Net Revenue, Sales, Revenue and other income, etc.)
- Profit or Loss Before Income Tax (or Profit Before Tax, Income Before Tax, Pre-tax Income, etc.)
- Profit or Loss for the Year/After Income Tax (or Net Profit, Net Income, Net Loss, Profit After Tax, etc.)

II. Cash Flow Statement Metrics:
- Net Cash from Operating Activities (or Operating Cash Flow, Cash from Operations, etc.)
- Net Cash from Investing Activities (or Cash from Investments, Investing Cash Flow, etc.)
- Net Cash from Financing Activities (or Cash from Financing, Financing Cash Flow, etc.)
- Cash and Cash Equivalents at End of Year (or Cash at Year End, Total Cash, etc.)

REQUIRED JSON OUTPUT FORMAT:
{
  "year_1": {
    "year": "YYYY",
    "revenue": number_or_null,
    "profit_before_tax": number_or_null,
    "profit_after_tax": number_or_null,
    "net_cash_operating": number_or_null,
    "net_cash_investing": number_or_null,
    "net_cash_financing": number_or_null,
    "cash_end_of_year": number_or_null
  },
  "year_2": {
    "year": "YYYY",
    "revenue": number_or_null,
    "profit_before_tax": number_or_null,
    "profit_after_tax": number_or_null,
    "net_cash_operating": number_or_null,
    "net_cash_investing": number_or_null,
    "net_cash_financing": number_or_null,
    "cash_end_of_year": number_or_null
  },
  "currencies": ["USD", "SGD"],
  "company_name": "extracted_company_name",
  "report_type": "Annual Report" or "10-K" or "Financial Statements"
}

Company hint (if provided): {company_hint}

Financial Statement Text:
{full_text}

Respond with ONLY the JSON object, no additional text.
```