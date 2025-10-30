"""Supabase client singleton for database operations.

This module creates a single Supabase client instance configured for the project.
All database operations should import and use this shared instance.

Pattern mirrors client.py (OpenRouter singleton).
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client with project credentials
# Supabase URL: https://{project_id}.supabase.co
# Service Role Key: Found in Supabase Dashboard > Settings > API
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABSE_SERVICE_ROLE_KEY")  # Note: User's variable name spelling

# Create client instance if credentials are available
# If credentials missing, supabase will be None (graceful degradation)
if supabase_url and supabase_key:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(supabase_url, supabase_key)
    except ImportError:
        # Supabase package not installed
        supabase = None
    except Exception:
        # Other initialization errors
        supabase = None
else:
    # Credentials not configured
    supabase = None
