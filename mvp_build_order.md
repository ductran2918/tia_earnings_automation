# Step-by-Step Build Order Plan for Financial Data Extraction MVP

## 0. Project setup
- Create repo skeleton (`app/`, `extractors/`, `data/`, `samples/`).
- Add two sample PDFs.
- Add `.env` and requirements.

## 1. Streamlit shell
- Minimal page with title + `st.file_uploader`.
- On upload, show file name/size.  
**Test:** upload both PDFs; no errors.

## 2. Save temp file
- Write uploaded bytes to a temp path.
- Echo path.  
**Test:** confirm file is created and cleaned on rerun.

`## 3. Page text extraction
- Implement extractor (per page).
- Render first 300 chars per page in an expander.  
**Test:** text appears for both PDFs.

## 4. Snippet finder
- Regex lines for `Revenue` and `Profit for the period|Net profit|Net income`.
- Include ±2 lines context + page index.  
**Test:** see 1–3 short snippets for each metric.`

## 5. Config panel
- Inputs for API key, model, temperature=0, max_tokens=256.
- Validate key present.  
**Test:** blocks LLM call if key missing.

## 6. LLM call (snippets only)
- Send compact prompt + snippets.
- Expect strict JSON; parse & validate schema.  
**Test:** valid JSON for both PDFs; handle “null” when missing.

## 7. Result UI
- Show normalized numbers, unit/scale, page no, evidence text.
- Color-code if missing.  
**Test:** values readable; evidence matches snippet.

## 8. CSV persistence
- Append a row with file_hash, company (free text), period (free text), metrics, evidence, page.  
**Test:** CSV created and row appended once per file.

## 9. Caching
- If file_hash already processed and settings unchanged, reuse prior JSON.
- Add “Re-run extraction” button.  
**Test:** second run avoids API call.

## 10. Errors & logging
- Surface JSON errors, empty snippets, API failures.
- Write a simple log line per run.  
**Test:** simulate API failure; app stays responsive.

## 11. (Optional) Period detector
- Regex common “ended” patterns; prefill period field.  
**Test:** auto-filled for Grab PR; editable by user.

## 12. (Optional) History tab
- Read CSV → filter by company/period → download button.  
**Test:** shows prior rows; export opens in Sheets/Excel.

---

### Acceptance heuristics
- Each step adds ≤ ~30–60 lines and is **demoable**.
- You can **roll back** by discarding the last commit without touching previous working features.
- After Step 8, you already have a usable MVP; Steps 9–12 are quality/cost/usability boosts.

### Working style with Claude Code
- Drive **one step at a time**; ask it to *only* add/modify files for that step.
- After each change, **run locally and verify** the acceptance test before proceeding.
- When something breaks, ask Claude Code to **diff and explain** its changes, then fix *only* the failing part.
