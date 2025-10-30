# client.py
"""
Centralized OpenRouter client setup.
This file creates a single OpenAI client instance configured to use OpenRouter.
Other files (like app.py) should import `client` from here.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key with priority: Streamlit secrets → Environment variables
# This ensures the app works on both Streamlit Cloud and local development
openrouter_api_key = None

# Try loading from Streamlit secrets first (for Streamlit Cloud deployment)
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

# Create client with OpenRouter base_url
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key,
)