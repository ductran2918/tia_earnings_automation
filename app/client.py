# client.py
"""
Centralized OpenRouter client setup.
This file creates a single OpenAI client instance configured to use OpenRouter.
Other files (like app.py) should import `client` from here.
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create client with OpenRouter base_url
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),  # your OpenRouter key
)