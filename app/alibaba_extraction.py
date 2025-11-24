"""Alibaba Group-specific financial data extraction module.

This module contains the extraction function specifically for Alibaba Group Holding Limited.
It uses a custom prompt tailored to Alibaba's financial reporting structure
with 36 metrics across consolidated financials and seven business segments:
- Taobao and Tmall Group
- International Digital Commerce Group
- Cainiao Smart Logistics Network Limited
- Cloud Intelligence Group
- Local Services Group
- Digital Media and Entertainment Group
- All Others

Note: Alibaba reports in RMB but provides USD convenience translation.
The extractor is configured to extract USD values only.
"""
import json
from pathlib import Path
from typing import Dict

import streamlit as st

from client import get_client


# Alibaba Group-specific prompt path
ALIBABA_PROMPT_PATH = Path(__file__).parent.parent / "prompt" / "alibaba_group_extraction.md"


def _load_alibaba_prompt() -> str:
    """Load Alibaba Group-specific extraction prompt from file.

    Returns:
        str: Prompt text as string, or empty string if file not found
    """
    try:
        with open(ALIBABA_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Alibaba Group prompt file not found: {ALIBABA_PROMPT_PATH}")
        return ""
    except Exception as exc:
        st.error(f"Failed to load Alibaba Group prompt: {exc}")
        return ""


def _parse_alibaba_json_response(json_text: str) -> Dict:
    """Parse JSON response from LLM for Alibaba Group extraction.

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


def extract_alibaba_data_with_llm(
    pdf_text: str,
    company_hint: str = "Alibaba Group",
    model_name: str = "deepseek/deepseek-chat-v3.1:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict:
    """Extract Alibaba Group-specific financial data from PDF text using LLM.

    This function uses Alibaba Group's custom extraction prompt which returns a fixed schema
    with 36 metrics specific to Alibaba Group Holding Limited, including:
    - Consolidated financials (9 fields): revenue, profit, expenses, cash, assets
    - Segment revenue (7 fields): Taobao/Tmall, International, Cainiao, Cloud, Local Services, Entertainment, Others
    - Segment adjusted EBITDA (7 fields): Same segments
    - Balance sheet (5 fields): cash, investments, assets, liabilities, equity
    - Cash flow (3 fields): operating, investing, financing
    - Other metrics (5 fields): employees, ratios (all calculated as null per prompt)

    Important: Alibaba reports in RMB with USD convenience translation.
    This extractor is configured to extract USD values only.

    Args:
        pdf_text: Full text extracted from PDF earnings report
        company_hint: Company name hint (default: "Alibaba Group")
        model_name: LLM model to use via OpenRouter API
        temperature: LLM temperature (0.0 for deterministic output)
        max_tokens: Maximum tokens for LLM response

    Returns:
        dict: Alibaba Group-specific financial data with schema:
            {
                "id": null,
                "company_slug": "alibaba-group",
                "date": "YYYY-MM-DD",
                "Revenue": <number or null>,
                "Gross profit": <number or null>,
                ... (34 more Alibaba-specific metrics)
            }

        On error, returns: {"error": "error message"}
    """
    try:
        # Load Alibaba Group-specific prompt
        prompt_text = _load_alibaba_prompt()
        if not prompt_text:
            return {"error": "Alibaba Group prompt template is missing."}

        # Format user prompt with PDF text
        user_prompt = f"""Company: {company_hint}

PDF Text:
{pdf_text}

{prompt_text}"""

        # System prompt for Alibaba Group extraction
        system_prompt = (
            "You are a precise financial data extraction assistant specialized in "
            "extracting Alibaba Group Holding Limited financial metrics from earnings reports. "
            "Remember to extract USD values only, not RMB values."
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
        financial_data = _parse_alibaba_json_response(json_text)

        # Validate that company_slug is "alibaba-group"
        if financial_data.get("company_slug") != "alibaba-group":
            st.warning(
                f"Warning: Extracted company_slug is '{financial_data.get('company_slug')}' "
                f"but expected 'alibaba-group'. Correcting..."
            )
            financial_data["company_slug"] = "alibaba-group"

        return financial_data

    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse Alibaba Group extraction response as JSON: {exc}")
        return {"error": "Invalid JSON response from LLM"}
    except Exception as exc:
        st.error(f"Alibaba Group extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}
