import json
from pathlib import Path
from typing import Dict, Optional

import streamlit as st

from client import client

PROMPT_PATH = Path(__file__).parent.parent / "prompt" / "extract_data_prompt.md"
PUBLIC_COMPANY_PROMPT_PATH = Path(__file__).parent.parent / "prompt" / "3statement_extraction_prompt.md"
_PROMPT_CACHE: Optional[Dict[str, str]] = None
DEFAULT_SYSTEM_PROMPT = "You are a financial data extraction expert."
DEFAULT_COMPANY_HINT = "Not provided"
INVALID_JSON_ERROR = "Invalid JSON response from LLM"


def _parse_prompt_markdown(markdown_text: str) -> Dict[str, str]:
    """Parse markdown prompt file into named sections."""
    sections: Dict[str, str] = {}
    current_section: Optional[str] = None
    buffer = []

    for line in markdown_text.splitlines():
        if line.startswith("## "):
            if current_section is not None:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = line[3:].strip().lower()
            buffer = []
        elif current_section is not None:
            buffer.append(line)

    if current_section is not None:
        sections[current_section] = "\n".join(buffer).strip()

    return sections


def _reset_prompt_cache_with_error(error_message: str) -> None:
    """Reset prompt cache and display error message."""
    global _PROMPT_CACHE
    st.error(error_message)
    _PROMPT_CACHE = {}


def get_prompt_config() -> Dict[str, str]:
    """Load and cache prompt configuration from markdown file."""
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        try:
            with open(PROMPT_PATH, "r", encoding="utf-8") as file_obj:
                sections = _parse_prompt_markdown(file_obj.read())
            _PROMPT_CACHE = {
                "system": sections.get("system", DEFAULT_SYSTEM_PROMPT),
                "template": sections.get("template", ""),
            }
            if not _PROMPT_CACHE["template"]:
                _reset_prompt_cache_with_error(
                    "Prompt template is missing the 'template' section."
                )
        except FileNotFoundError:
            _reset_prompt_cache_with_error(
                f"Prompt template file not found at: {PROMPT_PATH}"
            )
        except Exception as exc:  # pragma: no cover - defensive UI logging
            _reset_prompt_cache_with_error(
                f"Failed to load prompt template: {exc}"
            )
    return _PROMPT_CACHE


def _strip_markdown_code_blocks(text: str) -> str:
    """Remove markdown code block markers and clean LLM response."""
    # Strip leading/trailing whitespace
    text = text.strip()

    # Handle complete markdown blocks
    if text.startswith('```json') and text.endswith('```'):
        text = text[7:-3].strip()
    elif text.startswith('```') and text.endswith('```'):
        text = text[3:-3].strip()
    # Handle truncated responses (missing closing ```)
    elif text.startswith('```json'):
        text = text[7:].strip()
    elif text.startswith('```'):
        text = text[3:].strip()
    # Handle trailing markdown that wasn't closed
    elif text.endswith('```'):
        text = text[:-3].strip()

    # Remove common prefixes that LLMs add
    prefixes_to_remove = [
        "Here's the JSON:",
        "Here is the JSON:",
        "JSON:",
        "Output:",
        "Result:",
    ]
    for prefix in prefixes_to_remove:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    return text


def _extract_json_block(text: str) -> Optional[str]:
    """Extract the first JSON object from arbitrary text."""
    start_idx = None
    bracket_depth = 0

    for idx, char in enumerate(text):
        if char == '{':
            if start_idx is None:
                start_idx = idx
            bracket_depth += 1
        elif char == '}':
            if bracket_depth > 0:
                bracket_depth -= 1
                if bracket_depth == 0 and start_idx is not None:
                    return text[start_idx : idx + 1]

    return None


def _parse_llm_json_response(json_text: str) -> Dict:
    """Parse JSON from LLM response with multiple fallback strategies."""
    # Remove markdown code blocks if present
    cleaned_text = _strip_markdown_code_blocks(json_text)

    try:
        # Try parsing cleaned text directly
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        # Fallback: Extract embedded JSON block
        json_block = _extract_json_block(cleaned_text)
        if json_block:
            try:
                # Successfully extracted and parsed JSON - no need to show warnings
                return json.loads(json_block)
            except json.JSONDecodeError:
                # JSON block extraction failed, show debug info below
                pass

        # Debug output: Show what we're trying to parse (only if all parsing failed)
        st.warning(f"**Debug Info - JSON Parse Error:**")
        st.text(f"Error: {str(e)}")
        st.text(f"Raw response length: {len(json_text)} characters")
        st.text(f"Cleaned text length: {len(cleaned_text)} characters")

        # Show first and last 500 chars of the response
        st.text("**First 500 chars of raw response:**")
        st.code(json_text[:500], language="text")
        st.text("**Last 500 chars of raw response:**")
        st.code(json_text[-500:], language="text")

        raise


def _load_prompt_from_file(path: Path) -> str:
    """Load prompt text from file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Prompt file not found: {path}")
        return ""
    except Exception as exc:
        st.error(f"Failed to load prompt: {exc}")
        return ""


def extract_financial_data_with_llm(
    pdf_text: str,
    company_hint: str = "",
    model_name: str = "openai/gpt-oss-20b:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict:
    """Extract financial data using LLM via OpenRouter."""
    try:
        # Load prompt configuration
        prompt_config = get_prompt_config()
        prompt_template = prompt_config.get("template", "") if prompt_config else ""
        if not prompt_template:
            return {"error": "Prompt template is missing."}

        # Prepare prompts
        system_prompt = prompt_config.get("system", DEFAULT_SYSTEM_PROMPT)
        company_hint_value = company_hint if company_hint else DEFAULT_COMPANY_HINT
        user_prompt = prompt_template.format(
            company_hint=company_hint_value,
            pdf_text=pdf_text
        )

        # Call LLM API
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
        return _parse_llm_json_response(json_text)

    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse LLM response as JSON: {exc}")
        return {"error": INVALID_JSON_ERROR}
    except Exception as exc:  # pragma: no cover - defensive UI logging
        st.error(f"LLM extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}


def extract_public_company_data_with_llm(
    pdf_text: str,
    company_hint: str = "",
    model_name: str = "deepseek/deepseek-chat-v3.1:free",
    temperature: float = 0.0,
    max_tokens: int = 50000,
) -> Dict:
    """Extract public company financial data using 3-statement prompt.

    Args:
        pdf_text: Extracted text from PDF
        company_hint: Company name for context
        model_name: LLM model to use
        temperature: LLM temperature parameter
        max_tokens: Maximum tokens for LLM response

    Returns:
        Dict containing extracted financial statements with structure:
        {
            "date": "YYYY-MM-DD",
            "profit_or_loss_statement": {...},
            "balance_sheet_statement": {...},
            "cash_flows_statement": {...},
            "_aliases": {...}
        }
    """
    try:
        # Load public company prompt
        prompt_text = _load_prompt_from_file(PUBLIC_COMPANY_PROMPT_PATH)
        if not prompt_text:
            return {"error": "Public company prompt template is missing."}

        # Format prompt with company hint and PDF text
        company_hint_value = company_hint if company_hint else DEFAULT_COMPANY_HINT
        user_prompt = f"""Company: {company_hint_value}

PDF Text:
{pdf_text}

{prompt_text}"""

        # Call LLM API
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a financial data extraction expert specialized in extracting comprehensive financial statements from earnings reports."},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Parse JSON response
        json_text = response.choices[0].message.content.strip()
        return _parse_llm_json_response(json_text)

    except json.JSONDecodeError as exc:
        st.error(f"Failed to parse LLM response as JSON: {exc}")
        return {"error": INVALID_JSON_ERROR}
    except Exception as exc:  # pragma: no cover - defensive UI logging
        st.error(f"LLM extraction failed: {exc}")
        return {"error": f"LLM error: {exc}"}
