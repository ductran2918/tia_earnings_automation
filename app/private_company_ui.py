"""Private company extraction workflow UI components."""
import streamlit as st

from config import (
    COMPANY_HINT_LABEL,
    COMPANY_HINT_PLACEHOLDER,
    COMPANY_HINT_HELP,
)
from ui_components import render_file_uploader, render_results
from navigation import render_back_button


def render_company_hint_input() -> str:
    """Render company hint input in main area."""
    company_hint = st.text_input(
        COMPANY_HINT_LABEL,
        placeholder=COMPANY_HINT_PLACEHOLDER,
        help=COMPANY_HINT_HELP,
    )
    return company_hint


def render_private_company_page() -> None:
    """Render private company extraction page."""
    render_back_button()
    st.write("")  # Add spacing

    # Company hint input (moved to main area)
    company_hint = render_company_hint_input()

    # File upload and processing
    render_file_uploader(company_hint)
    render_results()
