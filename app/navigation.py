"""Navigation components for the Streamlit application."""
import streamlit as st

from config import (
    WELCOME_TITLE_TEMPLATE,
    COMPANY_TYPE_LABEL,
    COMPANY_TYPE_OPTIONS,
    NEXT_BUTTON_LABEL,
    BACK_BUTTON_LABEL,
)


def render_welcome_page() -> None:
    """Render the welcome/selection page with personalized greeting."""
    # Get authenticated user name from session state
    user_name = st.session_state.get("user_name", "Guest")

    # Format welcome title with user name
    welcome_title = WELCOME_TITLE_TEMPLATE.format(name=user_name)

    # Display personalized welcome title
    st.markdown(f"# {welcome_title}")
    st.write("")  # Add spacing

    # Company type selection
    company_type = st.selectbox(
        COMPANY_TYPE_LABEL,
        options=COMPANY_TYPE_OPTIONS,
        index=0,
    )

    # Show Next button if selection made
    if company_type:
        st.write("")  # Add spacing
        if st.button(NEXT_BUTTON_LABEL, type="primary"):
            # Store selection and navigate
            st.session_state.company_type = company_type
            if company_type == "Private company":
                st.session_state.page = "private_company"
            else:  # Public company
                st.session_state.page = "public_company"
            st.rerun()


def render_back_button() -> None:
    """Render back button to return to welcome page."""
    if st.button(BACK_BUTTON_LABEL):
        st.session_state.page = "welcome"
        st.session_state.company_type = None
        st.rerun()
