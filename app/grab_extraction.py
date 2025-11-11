"""Grab Holdings-specific financial data extraction module.

This module contains the extraction function specifically for Grab Holdings Limited.
It uses a custom prompt tailored to Grab's financial reporting structure.
"""
import json
from pathlib import Path
from typing import Dict

import streamlit as st

from client import get_client


# Grab-specific prompt path
GRAB_PROMPT_PATH = Path(__file__).parent.parent / "prompt" / "grab_com_extraction.md"


def _load_grab_prompt() -> str:
    """Load Grab-specific extraction prompt from file.

    Returns:
        Prompt text as string, or empty string if file not found
    """
    try:
        with open(GRAB_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Grab prompt file not found: {GRAB_PROMPT_PATH}")
        return ""
    except Exception as exc:
        st.error(f"Failed to load Grab prompt: {exc}")
        return ""


def _parse_grab_json_response(json_text: str) -> Dict:
    """Parse JSON response from LLM for Grab extraction.

    Handles common LLM response formatting issues (markdown blocks, extra text, NULL vs null).

    Args:
        json_text: Raw text response from LLM

    Returns:
        Parsed JSON dict, or error dict if parsing fails
    """
    # Strip markdown code blocks and whitespace
    cleaned = json_text.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:].strip()
    if cleaned.startswith('```'):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3].strip()

    # Fix common LLM JSON formatting issues
    import re

    # Replace uppercase NULL with lowercase null for JSON compatibility
    cleaned = re.sub(r'\bNULL\b', 'null', cleaned)

    # Add missing commas between key-value pairs
    # Pattern: "value"\n"key" should become "value",\n"key"
    # This handles both null and numeric values followed by newline and next key
    cleaned = re.sub(r'(null|true|false|"[^"]*"|\d+\.?\d*)\s*\n\s*"', r'\1,\n"', cleaned)

    try:
        # Try parsing directly
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: Extract JSON object using bracket matching
        start_idx = cleaned.find('{')
        if start_idx == -1:
            raise

        bracket_depth = 0
        for idx in range(start_idx, len(cleaned)):
            char = cleaned[idx]
            if char == '{':
                bracket_depth += 1
            elif char == '}':
                bracket_depth -= 1
                if bracket_depth == 0:
                    json_block = cleaned[start_idx:idx + 1]
                    return json.loads(json_block)
        raise


def extract_grab_data_with_llm(
    pdf_text: str,
    company_hint: str = "Grab",
    model_name: str = "deepseek/deepseek-chat-v3.1:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict:
    """Extract Grab-specific financial data from PDF text using LLM.

    This function uses Grab's custom extraction prompt which returns a fixed schema
    with 23 metrics specific to Grab Holdings Limited (group metrics, segment metrics,
    cash flow metrics, etc.).

    Args:
        pdf_text: Full text extracted from PDF
        company_hint: Company name hint (default: "Grab")
        model_name: LLM model to use via OpenRouter
        temperature: LLM temperature (0.0 for deterministic)
        max_tokens: Maximum tokens for LLM response

    Returns:
        Dict with Grab-specific schema:
        {
            "id": null,
            "company_slug": "grab-com",
            "date": "YYYY-MM-DD",
            "group_revenue": <number or null>,
            "group_adjusted_ebitda": <number or null>,
            ... (20 more Grab-specific metrics)
        }

        On error, returns: {"error": "error message"}
    """
    try:
        # Load Grab-specific prompt
        prompt_text = _load_grab_prompt()
        if not prompt_text:
            return {"error": "Grab prompt template is missing."}

        # Format user prompt with PDF text
        user_prompt = f"""Company: {company_hint}

PDF Text:
{pdf_text}

{prompt_text}"""

        # System prompt for Grab extraction
        system_prompt = (
            "You are a precise financial data extraction assistant specialized in "
            "extracting Grab Holdings Limited financial metrics from earnings reports."
        )

        # Get client and call OpenRouter API
        client = get_client()
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parse JSON response
        json_text = response.choices[0].message.content.strip()
        financial_data = _parse_grab_json_response(json_text)

        # Validate that company_slug is "grab-com"
        if financial_data.get("company_slug") != "grab-com":
            st.warning(
                f"Warning: Extracted company_slug is '{financial_data.get('company_slug')}' "
                f"but expected 'grab-com'. Correcting..."
            )
            financial_data["company_slug"] = "grab-com"

        return financial_data

    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse Grab extraction response as JSON: {exc}")
        return {"error": "Invalid JSON response from LLM"}
    except Exception as exc:
        st.error(f"Grab extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}
