"""Shared UI utilities for PDF extraction workflows."""
import json
import os

import streamlit as st

from config import (
    MAX_FILE_SIZE_MB,
    MODEL_NAME,
    TEMPERATURE,
    MAX_TOKENS,
    UPLOAD_INFO_TEXT,
    UPLOAD_BUTTON_LABEL,
    DOWNLOAD_BUTTON_LABEL,
    UPLOAD_WIDGET_LABEL,
    DOWNLOAD_FILENAME,
)
from pdf_utils import (
    save_temp_file,
    get_pdf_info,
    extract_full_pdf_text,
    format_file_size,
)
from extract_data import extract_financial_data_with_llm, extract_public_company_data_with_llm
from company_extractors import get_extractor_config, get_extraction_function


def check_api_key() -> bool:
    """Verify OpenRouter API key is configured.

    Checks both Streamlit secrets (for Streamlit Cloud) and environment variables
    (for local development) to ensure the API key is available.
    """
    openrouter_api_key = None

    # Try loading from Streamlit secrets first (for Streamlit Cloud)
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            openrouter_api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass

    # Fallback to environment variable (for local development)
    if not openrouter_api_key:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")

    if not openrouter_api_key:
        st.error(
            "System configuration error: OpenRouter API key not found. "
            "Please set it before using the app."
        )
        return False
    return True


def validate_uploaded_file(uploaded_file) -> bool:
    """Validate uploaded file size and type."""
    file_size = uploaded_file.size
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(
            f"File too large: {format_file_size(file_size)}. "
            f"Maximum allowed size is {MAX_FILE_SIZE_MB}MB."
        )
        return False

    if uploaded_file.type != "application/pdf":
        st.error(
            f"Invalid file type: {uploaded_file.type}. "
            "Please upload a PDF file."
        )
        return False

    return True


def process_pdf_file(
    uploaded_file,
    company_hint: str,
    company_slug: str = None,
    button_label: str = None
) -> None:
    """Process uploaded PDF file and extract financial data.

    Args:
        uploaded_file: Streamlit UploadedFile object
        company_hint: Company name for context
        company_slug: Company slug for public companies (optional)
        button_label: Custom button label (optional, defaults to config)
    """
    try:
        # Save temporary file
        temp_path = save_temp_file(uploaded_file)
        pdf_info = get_pdf_info(temp_path)

        if not pdf_info["success"]:
            st.error(f"Unable to read PDF metadata: {pdf_info['error']}")
            return

        # Display page count
        st.caption(
            f"Detected {pdf_info['page_count']} page(s). "
            "Click the button below to extract financial metrics."
        )

        # Use custom button label or default
        btn_label = button_label if button_label else UPLOAD_BUTTON_LABEL

        # Extract button
        if st.button(btn_label, type="primary"):
            # Extract text from PDF
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_full_pdf_text(temp_path)

            if not pdf_text:
                st.error("Failed to extract text from the PDF.")
                return

            # Analyze with LLM - use company-specific extraction if available
            with st.spinner(f"Analyzing with {MODEL_NAME}..."):
                if company_slug:
                    # Try to get company-specific extraction function
                    extraction_func = get_extraction_function(company_slug)
                    config = get_extractor_config(company_slug)

                    if extraction_func:
                        # Use company-specific extraction (e.g., Grab-specific)
                        financial_data = extraction_func(
                            pdf_text=pdf_text,
                            company_hint=company_hint,
                            model_name=MODEL_NAME,
                            temperature=TEMPERATURE,
                            max_tokens=MAX_TOKENS,
                        )
                        # Company slug already injected by company-specific function
                    else:
                        # Fallback to generic public company extraction
                        financial_data = extract_public_company_data_with_llm(
                            pdf_text=pdf_text,
                            company_hint=company_hint,
                            model_name=MODEL_NAME,
                            temperature=TEMPERATURE,
                            max_tokens=MAX_TOKENS,
                        )
                        # Inject company_slug into the response
                        if "error" not in financial_data:
                            financial_data["company_slug"] = company_slug
                else:
                    # Private company: Use 2-year extraction
                    financial_data = extract_financial_data_with_llm(
                        pdf_text=pdf_text,
                        company_hint=company_hint,
                        model_name=MODEL_NAME,
                        temperature=TEMPERATURE,
                        max_tokens=MAX_TOKENS,
                    )
                    config = None

            # Display results
            if "error" in financial_data:
                st.error(f"Extraction failed: {financial_data['error']}")
            else:
                st.session_state.extracted_data = financial_data
                # Use company-specific success message if available
                if config and config.get("success_message"):
                    st.success(config["success_message"])
                else:
                    st.success("Financial data extracted successfully.")

    except Exception as exc:
        st.error(f"Error processing file: {exc}")


def render_file_uploader(
    company_hint: str,
    company_slug: str = None,
    button_label: str = None
) -> None:
    """Render file uploader and handle file processing.

    Args:
        company_hint: Company name for context
        company_slug: Company slug for public companies (optional)
        button_label: Custom button label (optional)
    """
    uploader_help_text = f"Select a PDF file (max {MAX_FILE_SIZE_MB}MB)"
    uploaded_file = st.file_uploader(
        UPLOAD_WIDGET_LABEL,
        type=["pdf"],
        accept_multiple_files=False,
        help=uploader_help_text,
    )

    if uploaded_file is None:
        st.info(UPLOAD_INFO_TEXT)
    else:
        if validate_uploaded_file(uploaded_file):
            process_pdf_file(uploaded_file, company_hint, company_slug, button_label)


def render_results() -> None:
    """Render extracted data results and download button for private companies."""
    extracted_data = st.session_state.get("extracted_data")
    if extracted_data:
        st.subheader("Extracted Financial Data")
        st.json(extracted_data)

        download_payload = json.dumps(extracted_data, indent=2)
        st.download_button(
            label=DOWNLOAD_BUTTON_LABEL,
            data=download_payload,
            file_name=DOWNLOAD_FILENAME,
            mime="application/json",
        )


def render_public_company_results() -> None:
    """Render extracted data results for public companies (no download button).

    This displays the extraction results with company_slug injected.
    Push to database section is rendered separately via render_push_to_database_section().
    """
    extracted_data = st.session_state.get("extracted_data")
    if extracted_data:
        st.subheader("Extracted Financial Data")
        st.json(extracted_data)


def render_push_to_database_section(company_slug: str) -> None:
    """Render database push UI section for public companies.

    Shows duplicate warning if data exists, and "Push to Supabase" button.

    Args:
        company_slug: Company identifier (e.g., "grab-com", "sea-group-garena")
    """
    from supabase_client import supabase

    # Check if extracted data exists
    extracted_data = st.session_state.get("extracted_data")
    if not extracted_data or "error" in extracted_data:
        return

    # Hide push section if Supabase not configured
    if not supabase:
        return

    # Section header with divider
    st.divider()
    st.subheader("Push to Database")

    # Dynamic imports based on company_slug
    if company_slug == "grab-com":
        from database import push_grab_to_supabase, check_duplicate_grab
        push_func = push_grab_to_supabase
        check_func = check_duplicate_grab
    elif company_slug == "sea-group-garena":
        from database import push_sea_group_to_supabase, check_duplicate_sea_group
        push_func = push_sea_group_to_supabase
        check_func = check_duplicate_sea_group
    else:
        # Unknown company - should not reach here
        return

    # Check for existing data (duplicate detection)
    date = extracted_data.get("date")
    if date:
        existing = check_func(company_slug, date)
        if existing:
            st.warning(
                f"⚠️ Data already exists for {company_slug} on {date}. "
                "Pushing will update the existing record."
            )

    # Push button
    # Use unique key per company to prevent Streamlit widget ID conflicts
    if st.button("Push to Supabase", type="primary", key=f"push_to_supabase_btn_{company_slug}"):
        with st.spinner("Pushing data to database..."):
            result = push_func(extracted_data)

        # Display result
        if result["success"]:
            # Celebration animation
            st.balloons()

            # Show success message with celebration emoji
            st.success(f"🎉 {result['message']}")
            st.info(f"Record ID: {result['record_id']}")

            # Store record ID in session state for future reference
            st.session_state.last_pushed_record_id = result["record_id"]
            st.session_state.last_pushed_date = date
        else:
            st.error(f"❌ Push failed: {result['error']}")
            st.info("Data is still available above. Fix the issue and try again.")
