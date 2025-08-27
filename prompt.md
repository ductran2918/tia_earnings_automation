# Prompt for Claude Code — Step 1: PDF Upload UI (Streamlit)

## Context you must honor

* **Goal:** Internal Streamlit app for editors to upload financial-statement PDFs and (later) extract only **Revenue** and **Net Profit**.
* **Audience:** Non-technical editors; UX must be simple and forgiving.
* **Timebox:** Implement **only Step 1** now (upload UI + lightweight preview). No LLM, no CSV, no DB.

## Your task (implement only this step)

* Build a **single Streamlit page** that allows uploading **one PDF** and displays:

  * File **name** and **human-readable size**.
  * **Page count** using `pdfplumber` (no OCR, no table parsing).
  * A **text preview**: first **300 characters** of **page 1** (trim whitespace). If no text, show: “No extractable text on page 1.”
  * A **status box** with the **temporary file path** where the uploaded bytes are saved.
* Add basic **validation & resilience**:

  * Accept only `.pdf` and MIME `application/pdf`.
  * Reject files **> 25 MB** with a clear warning.
  * Gracefully handle **encrypted/unsupported PDFs** with `st.warning` (no crash).
  * If the same file is uploaded again, safely overwrite the temp copy.
* Add UX niceties:

  * **“Clear”** button resets the UI to initial state.
  * Minimal use of `st.session_state` to avoid rerun glitches.

## Files to add/modify

* `app/main.py` — implement all UI and logic here.
* (Optional) `.streamlit/config.toml` — minimal clean theme; keep changes small.

## Implementation details

* **Layout**

  * Title: `Financial PDF Loader — Step 1: Upload`
  * Two-column layout: **left** = uploader; **right** = file info & preview.
* **Uploader**

  * `st.file_uploader("Upload a financial PDF", type=["pdf"], accept_multiple_files=False)`
* **Temp file handling**

  * Save uploaded bytes to `.tmp/` with a **timestamped filename**.
  * Ensure `.tmp/` exists; create if missing.
* **Preview & info**

  * File name, human-readable size (KB/MB).
  * `pdfplumber.open(tmp_path)` → page count; catch exceptions.
  * Page 1 text (first 300 chars) if available; else fallback message.
* **Error handling**

  * Wrap open/extract in try/except; use `st.warning` for recoverable issues, `st.error` for hard failures.

## Coding standards

* Keep functions **small** and **typed**:

  * `save_temp_file(upload) -> Path`
  * `get_pdf_info(path: Path) -> dict` (e.g., `{"page_count": int, "has_text": bool}`)
  * `read_page_preview(path: Path, page_idx: int = 0, max_chars: int = 300) -> str`
* No global secrets; no network/LLM calls; no unused imports.

## Acceptance criteria (must pass locally)

* App runs and displays the upload UI.
* Uploading a valid small PDF shows **name**, **size**, **page count**, **page-1 preview** within \~2 seconds.
* Uploading a non-PDF or a **>25 MB** file shows a clear message; **no crash**.
* Encrypted/unsupported PDFs show a **warning**, not a crash.
* **Clear** button resets the UI state fully.

## Deliverable

* A clean, production-ready `app/main.py` implementing the above (no placeholders for future steps).
* If you add `.streamlit/config.toml`, keep it minimal and document any keys you set in code comments.

## Out of scope (do NOT implement now)

* No LLM prompts or API calls.
* No snippet-finding logic.
* No CSV/database/storage beyond saving the temp file.
* No OCR or batch/multi-file upload.

