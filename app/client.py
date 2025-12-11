# client.py
"""
Centralized OpenRouter client setup with lazy initialization.

This file provides a get_client() function that creates an OpenAI client
configured to use OpenRouter. The client is created on-demand (lazy loading)
to ensure Streamlit secrets are available when accessed.

Other files should import get_client from here and call it when needed.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Global variable to cache the client instance
_client_instance = None


def get_client() -> OpenAI:
    """Get or create the OpenRouter client (lazy initialization).

    This function creates the client on first call and caches it for reuse.
    It ensures that Streamlit has started and secrets are available before
    attempting to access them.

    Returns:
        OpenAI: Configured OpenAI client with OpenRouter base URL

    Raises:
        ValueError: If OPENROUTER_API_KEY is not found in secrets or environment
    """
    global _client_instance

    # Return cached instance if already created
    if _client_instance is not None:
        return _client_instance

    # Load API key with priority: Streamlit secrets → Environment variables
    # This ensures the app works on both Streamlit Cloud and local development
    openrouter_api_key = None

    # Try loading from Streamlit secrets first (for Streamlit Cloud deployment)
    # At this point, Streamlit has already started and st.secrets is available
    try:
        import streamlit as st
        if "OPENROUTER_API_KEY" in st.secrets:
            openrouter_api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        # Streamlit not available or secrets not configured
        pass

    # Fallback: Load from .env file or environment variables (for local development)
    if not openrouter_api_key:
        load_dotenv()
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

    # Raise error if API key not found
    if not openrouter_api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found. Please set it in Streamlit secrets "
            "(for cloud deployment) or .env file (for local development)."
        )

    # Create and cache the client
    _client_instance = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )

    return _client_instance
