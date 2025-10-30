"""Authentication module for user verification.

This module handles simple team authentication using a security question.
Users must answer correctly to access the earnings tracker tool.
"""
import json
import os
from typing import Optional, Tuple

import streamlit as st

from config import AUTH_QUESTION, AUTH_ERROR_MESSAGE, USER_VERIFY_FILE


def load_user_verification_data() -> dict:
    """Load user verification data from JSON file.

    Returns:
        Dictionary mapping answer (food) to user name.
        Example: {"sushi": "Terence", "adobo": "Miguel", "pho": "Duc"}
        Returns empty dict if file not found or parsing fails.
    """
    try:
        # Get path to user verification file in project root
        # Path(__file__) = app/authentication.py
        # parent.parent = project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(project_root, USER_VERIFY_FILE)

        if not os.path.exists(json_path):
            st.error(f"User verification file not found: {json_path}")
            return {}

        with open(json_path, "r", encoding="utf-8") as f:
            user_data = json.load(f)

        return user_data

    except json.JSONDecodeError as exc:
        st.error(f"Invalid JSON in user verification file: {exc}")
        return {}
    except Exception as exc:
        st.error(f"Failed to load user verification data: {exc}")
        return {}


def verify_user_answer(answer: str, user_data: dict) -> Tuple[bool, Optional[str]]:
    """Verify user answer against verification data.

    Processing:
    1. Strip whitespace from answer
    2. Convert to lowercase for case-insensitive comparison
    3. Check if answer exists in user_data keys
    4. Return (True, user_name) if match, (False, None) if no match

    Args:
        answer: Raw user input (e.g., "SUSHI ", "adobo", "Pho")
        user_data: Dictionary mapping answer to user name

    Returns:
        Tuple of (is_valid, user_name)
        - (True, "Terence") if answer is valid
        - (False, None) if answer is invalid

    Examples:
        >>> verify_user_answer("sushi", {"sushi": "Terence"})
        (True, "Terence")
        >>> verify_user_answer("SUSHI ", {"sushi": "Terence"})
        (True, "Terence")
        >>> verify_user_answer("pizza", {"sushi": "Terence"})
        (False, None)
    """
    # Normalize answer: strip whitespace and convert to lowercase
    normalized_answer = answer.strip().lower()

    # Check if normalized answer exists in user_data keys
    if normalized_answer in user_data:
        user_name = user_data[normalized_answer]
        return (True, user_name)
    else:
        return (False, None)


def render_authentication_page() -> None:
    """Render authentication page with security question.

    Workflow:
    1. Display security question
    2. User enters answer in text input
    3. User clicks Submit button
    4. Answer is verified (strip whitespace, case-insensitive)
    5. If valid: Set session state and redirect to welcome page
    6. If invalid: Show error message and stay on authentication page
    """
    # Page title and spacing
    st.title("🔐 Authentication")
    st.write("")

    # Load user verification data
    user_data = load_user_verification_data()

    if not user_data:
        st.error("Unable to load user verification data. Please contact support.")
        return

    # Display security question
    st.subheader(AUTH_QUESTION)

    # Text input for answer
    # Use unique key to avoid widget conflicts
    answer = st.text_input(
        "Your answer:",
        placeholder="Enter your answer",
        key="auth_answer_input",
        help="This is case-insensitive"
    )

    # Submit button
    if st.button("Submit", type="primary", key="auth_submit_btn"):
        if not answer:
            st.warning("Please enter your answer.")
            return

        # Verify answer
        is_valid, user_name = verify_user_answer(answer, user_data)

        if is_valid:
            # Authentication successful
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user_name = user_name
            st.session_state.page = "welcome"

            # Show success message briefly
            st.success(f"Welcome, {user_name}!")

            # Redirect to welcome page
            st.rerun()
        else:
            # Authentication failed
            st.error(AUTH_ERROR_MESSAGE)
