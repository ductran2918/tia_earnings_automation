"""Main entry point for the Financial Data Extractor application."""
import streamlit as st
from dotenv import load_dotenv

from config import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT, UPLOAD_SUBHEADER
from ui_components import check_api_key
from authentication import render_authentication_page
from navigation import render_welcome_page
from public_company_ui import render_public_company_page
from private_company_ui import render_private_company_page


def initialize_session_state():
    """Initialize session state variables."""
    # Authentication state (new)
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    # Page routing
    if "page" not in st.session_state:
        st.session_state.page = "authentication"  # Changed from "welcome"

    # Company and extraction data
    if "company_type" not in st.session_state:
        st.session_state.company_type = None
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None
    if "selected_public_company_name" not in st.session_state:
        st.session_state.selected_public_company_name = None
    if "selected_public_company_slug" not in st.session_state:
        st.session_state.selected_public_company_slug = None


def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()

    # Configure page
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
    )

    # Initialize session state
    initialize_session_state()

    # Route to appropriate page
    if st.session_state.page == "authentication":
        render_authentication_page()

    elif st.session_state.page == "welcome":
        render_welcome_page()

    elif st.session_state.page == "private_company":
        # Check API key for private company page
        if not check_api_key():
            st.stop()

        # Display page title
        st.title(PAGE_TITLE)

        # Render private company page
        st.subheader(UPLOAD_SUBHEADER)
        render_private_company_page()

    elif st.session_state.page == "public_company":
        # Check API key for public company page
        if not check_api_key():
            st.stop()

        # Display page title
        st.title(PAGE_TITLE)

        # Render public company page
        render_public_company_page()


if __name__ == "__main__":
    main()
