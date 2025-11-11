"""Sea Group-specific financial data extraction module.

This module contains the extraction function specifically for Sea Group Limited.
It uses a custom prompt tailored to Sea Group's financial reporting structure
with 41 metrics across group-level and three business segments:
- Digital Entertainment (Garena)
- E-commerce (Shopee)
- Digital Financial Services (SeaMoney)
"""
import json
from pathlib import Path
from typing import Dict

import streamlit as st

from client import get_client


# Sea Group-specific prompt path
SEA_GROUP_PROMPT_PATH = Path(__file__).parent.parent / "prompt" / "sea_group_extraction.md"


def _load_sea_group_prompt() -> str:
    """Load Sea Group-specific extraction prompt from file.

    Returns:
        str: Prompt text as string, or empty string if file not found
    """
    try:
        with open(SEA_GROUP_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Sea Group prompt file not found: {SEA_GROUP_PROMPT_PATH}")
        return ""
    except Exception as exc:
        st.error(f"Failed to load Sea Group prompt: {exc}")
        return ""


def _parse_sea_group_json_response(json_text: str) -> Dict:
    """Parse JSON response from LLM for Sea Group extraction.

    Handles common LLM response formatting issues (markdown blocks, extra text, NULL vs null).

    Args:
        json_text: Raw text response from LLM

    Returns:
        dict: Parsed JSON dictionary

    Raises:
        json.JSONDecodeError: If JSON parsing fails after all attempts
    """
    # Strip markdown code blocks and whitespace
    cleaned = json_text.strip()
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:].strip()
    if cleaned.startswith('```'):
        cleaned = cleaned[3:].strip()
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3].strip()

    # Replace uppercase NULL with lowercase null for JSON compatibility
    # Use word boundary replacement to avoid replacing NULL inside strings
    import re
    cleaned = re.sub(r'\bNULL\b', 'null', cleaned)

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


def extract_sea_group_data_with_llm(
    pdf_text: str,
    company_hint: str = "Sea Group",
    model_name: str = "deepseek/deepseek-chat-v3.1:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict:
    """Extract Sea Group-specific financial data from PDF text using LLM.

    This function uses Sea Group's custom extraction prompt which returns a fixed schema
    with 41 metrics specific to Sea Group Limited, including:
    - Group-level metrics (15 fields): revenue, profit, expenses, cash positions
    - Digital Entertainment/Garena (9 fields): bookings, revenue, users, ARPU
    - E-commerce/Shopee (7 fields): marketplace revenue, VAS, product revenue
    - Digital Financial Services/SeaMoney (3 fields): revenue, expenses, EBITDA

    Args:
        pdf_text: Full text extracted from PDF earnings report
        company_hint: Company name hint (default: "Sea Group")
        model_name: LLM model to use via OpenRouter API
        temperature: LLM temperature (0.0 for deterministic output)
        max_tokens: Maximum tokens for LLM response

    Returns:
        dict: Sea Group-specific financial data with schema:
            {
                "id": null,
                "company_slug": "sea-group-garena",
                "date": "YYYY-MM-DD",
                "group_revenue_q_o_q_gain_percent": <number or null>,
                "group_adjusted_ebitda_margin_percent": <number or null>,
                "group_total_revenue": <number or null>,
                ... (38 more Sea Group-specific metrics)
            }

        On error, returns: {"error": "error message"}
    """
    try:
        # Load Sea Group-specific prompt
        prompt_text = _load_sea_group_prompt()
        if not prompt_text:
            return {"error": "Sea Group prompt template is missing."}

        # Format user prompt with PDF text
        user_prompt = f"""Company: {company_hint}

PDF Text:
{pdf_text}

{prompt_text}"""

        # System prompt for Sea Group extraction
        system_prompt = (
            "You are a precise financial data extraction assistant specialized in "
            "extracting Sea Group Limited financial metrics from earnings reports."
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
        financial_data = _parse_sea_group_json_response(json_text)

        # Validate that company_slug is "sea-group-garena"
        if financial_data.get("company_slug") != "sea-group-garena":
            st.warning(
                f"Warning: Extracted company_slug is '{financial_data.get('company_slug')}' "
                f"but expected 'sea-group-garena'. Correcting..."
            )
            financial_data["company_slug"] = "sea-group-garena"

        return financial_data

    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse Sea Group extraction response as JSON: {exc}")
        return {"error": "Invalid JSON response from LLM"}
    except Exception as exc:
        st.error(f"Sea Group extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}
