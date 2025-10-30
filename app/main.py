"""Main entry point for the Streamlit earnings automation application."""
import streamlit as st

# Import page rendering functions
from authentication import render_authentication_page
from navigation import render_welcome_page
from private_company_ui import render_private_company_page
from public_company_ui import render_public_company_page


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    # Authentication state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = None

    # Navigation state
    if "page" not in st.session_state:
        st.session_state.page = "authentication"
    if "company_type" not in st.session_state:
        st.session_state.company_type = None

    # Data state (for persistence across page interactions)
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None


def main():
    """Main application entry point with page routing."""
    # Configure Streamlit page settings
    st.set_page_config(
        page_title="TIA Earnings Automation",
        page_icon="📊",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Route to appropriate page based on session state
    if st.session_state.page == "authentication":
        render_authentication_page()
    elif st.session_state.page == "welcome":
        render_welcome_page()
    elif st.session_state.page == "private_company":
        render_private_company_page()
    elif st.session_state.page == "public_company":
        render_public_company_page()
    else:
        # Fallback to authentication if page is unknown
        st.session_state.page = "authentication"
        st.rerun()


if __name__ == "__main__":
    main()
