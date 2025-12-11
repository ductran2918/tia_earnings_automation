"""Public company extraction workflow UI components."""
import json
import os

import streamlit as st

from config import (
    PUBLIC_COMPANIES_LIST_FILE,
    PUBLIC_COMPANY_DROPDOWN_LABEL,
    COMING_SOON_MESSAGE_TEMPLATE,
)
from ui_components import render_file_uploader, render_public_company_results, render_push_to_database_section
from navigation import render_back_button
from company_extractors import get_extractor_config, get_company_status


def load_public_companies_list() -> dict:
    """Load public companies list from JSON file.

    Returns:
        Dictionary mapping company names to slugs.
        Empty dict if file not found or parsing fails.
    """
    try:
        json_path = PUBLIC_COMPANIES_LIST_FILE
        if not os.path.exists(json_path):
            st.error(f"Public companies list file not found: {json_path}")
            return {}

        with open(json_path, "r", encoding="utf-8") as f:
            companies_dict = json.load(f)

        return companies_dict

    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON in public companies list: {exc}")
        return {}
    except Exception as exc:
        st.error(f"Failed to load public companies list: {exc}")
        return {}


def render_grab_ui(company_slug: str, company_name: str) -> None:
    """Render Grab-specific extraction UI with database push functionality.

    Args:
        company_slug: Company slug ("grab-com")
        company_name: Company display name ("Grab")
    """
    # Get Grab-specific configuration
    config = get_extractor_config(company_slug)
    if not config:
        st.error(f"Configuration not found for {company_name}")
        return

    # Render PDF uploader with Grab-specific button label
    render_file_uploader(
        company_hint=company_name,
        company_slug=company_slug,
        button_label=config["button_label"]  # "Extract Grab's metrics"
    )

    # Render results (JSON display)
    render_public_company_results()

    # Render database push section (always show if data exists, even with errors)
    extracted_data = st.session_state.get("extracted_data")
    if extracted_data:
        render_push_to_database_section(company_slug)


def render_sea_group_ui(company_slug: str, company_name: str) -> None:
    """Render Sea Group-specific extraction UI with database push functionality.

    Args:
        company_slug: Company slug ("sea-group-garena")
        company_name: Company display name ("Sea Group")
    """
    # Get Sea Group-specific configuration
    config = get_extractor_config(company_slug)
    if not config:
        st.error(f"Configuration not found for {company_name}")
        return

    # Render PDF uploader with Sea Group-specific button label
    render_file_uploader(
        company_hint=company_name,
        company_slug=company_slug,
        button_label=config["button_label"]  # "Extract Sea Group's metrics"
    )

    # Render results (JSON display)
    render_public_company_results()

    # Render database push section (always show if data exists and database push enabled)
    extracted_data = st.session_state.get("extracted_data")
    if extracted_data and config.get("has_database_push"):
        render_push_to_database_section(company_slug)


def render_alibaba_ui(company_slug: str, company_name: str) -> None:
    """Render Alibaba Group-specific extraction UI with database push functionality.

    Args:
        company_slug: Company slug ("alibaba-group")
        company_name: Company display name ("Alibaba Group")
    """
    # Get Alibaba Group-specific configuration
    config = get_extractor_config(company_slug)
    if not config:
        st.error(f"Configuration not found for {company_name}")
        return

    # Render PDF uploader with Alibaba Group-specific button label
    render_file_uploader(
        company_hint=company_name,
        company_slug=company_slug,
        button_label=config["button_label"]  # "Extract Alibaba's metrics"
    )

    # Render results (JSON display)
    render_public_company_results()

    # Render database push section (always show if data exists and database push enabled)
    extracted_data = st.session_state.get("extracted_data")
    if extracted_data and config.get("has_database_push"):
        render_push_to_database_section(company_slug)


def render_coming_soon_ui(company_name: str) -> None:
    """Render placeholder UI for companies not yet implemented.

    Args:
        company_name: Company display name (e.g., "Sea Group")
    """
    st.info(COMING_SOON_MESSAGE_TEMPLATE.format(company=company_name))
    st.write("")
    st.write("**What's coming:**")
    st.write(f"- Custom prompt for {company_name}'s financial structure")
    st.write(f"- {company_name}-specific metrics extraction")
    st.write("- Automated data validation and database upload")


def render_public_company_page() -> None:
    """Render public company extraction page with company dropdown.

    Dispatches to company-specific UI based on implementation status.
    """
    render_back_button()
    st.write("")  # Add spacing

    # Load companies list from JSON file
    companies_dict = load_public_companies_list()

    if not companies_dict:
        st.warning("No public companies available. Please add companies to the list.")
        return

    # Add "Select" as default placeholder option
    dropdown_options = ["Select"] + list(companies_dict.keys())

    # Company dropdown selection
    selected_company = st.selectbox(
        PUBLIC_COMPANY_DROPDOWN_LABEL,
        options=dropdown_options,
        index=0,  # Default to "Select"
    )

    # Dispatch based on selected company
    if selected_company != "Select":
        # Store selected company name and slug in session state
        st.session_state.selected_public_company_name = selected_company
        company_slug = companies_dict[selected_company]
        st.session_state.selected_public_company_slug = company_slug

        # Get company status and dispatch to appropriate UI
        status = get_company_status(company_slug)

        if status == "implemented":
            # Company has full implementation - render company-specific UI
            if company_slug == "grab-com":
                render_grab_ui(company_slug, selected_company)
            elif company_slug == "sea-group-garena":
                render_sea_group_ui(company_slug, selected_company)
            elif company_slug == "alibaba-group":
                render_alibaba_ui(company_slug, selected_company)
            # Add other implemented companies here as elif blocks
        else:
            # Company not yet implemented - show coming soon message
            render_coming_soon_ui(selected_company)
    else:
        # Reset session state when "Select" is chosen
        st.session_state.selected_public_company_name = None
        st.session_state.selected_public_company_slug = None
