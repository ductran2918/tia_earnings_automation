"""Currency detection and conversion utilities."""
from pathlib import Path
from typing import Dict, Optional
import json
import os
import copy
import re

import streamlit as st


SGD_INDICATORS = ["S$", "SGD", "SGD$", "singapore", "singapore dollar"]
SINGAPORE_COMPANY_INDICATORS = ["pte ltd", "pte. ltd.", "singapore", ".sg"]


def detect_sgd_currency(financial_data: Dict) -> bool:
    """Check if the financial data contains SGD currency indicators."""
    currencies = financial_data.get("currencies", [])

    for currency in currencies:
        for indicator in SGD_INDICATORS:
            if indicator.lower() in str(currency).lower():
                return True

    company_name = financial_data.get("company_name", "")
    for indicator in SINGAPORE_COMPANY_INDICATORS:
        if indicator.lower() in company_name.lower():
            return True

    data_str = str(financial_data).lower()
    if any(indicator.lower() in data_str for indicator in ["s$", "sgd", "singapore"]):
        return True

    if not currencies and financial_data.get("revenue") and financial_data.get("year_1"):
        return True

    return False


def convert_sgd_to_usd(json_data: Dict) -> Dict:
    """Convert SGD financial data to USD using exchange rates from JSON file."""
    try:
        json_path = "sgd_usd_rates_json.json"
        if not os.path.exists(json_path):
            return {"error": "Exchange rate JSON file not found"}

        with open(json_path, "r") as f:
            rate_lookup = json.load(f)

        converted_data = copy.deepcopy(json_data)
        exchange_rates_used = {}

        financial_metrics = [
            "revenue",
            "profit_before_tax",
            "profit_after_tax",
            "net_cash_operating",
            "net_cash_investing",
            "net_cash_financing",
            "cash_end_of_year",
        ]

        for year_key in ["year_1", "year_2"]:
            if year_key in converted_data and converted_data[year_key]:
                year_data = converted_data[year_key]
                year = str(year_data.get("year", ""))

                if year in rate_lookup:
                    exchange_rate = rate_lookup[year]
                    exchange_rates_used[year] = exchange_rate

                    for metric in financial_metrics:
                        if metric in year_data and year_data[metric] is not None:
                            try:
                                original_value = float(year_data[metric])
                                converted_value = original_value * exchange_rate
                                year_data[metric] = round(converted_value, 0)
                            except (ValueError, TypeError):
                                continue
                else:
                    return {"error": f"Exchange rate not found for year {year}"}

        converted_data["original_currencies"] = converted_data.get("currencies", [])
        converted_data["currencies"] = ["USD"]
        converted_data["exchange_rates_used"] = exchange_rates_used

        return converted_data

    except Exception as exc:
        return {"error": f"Currency conversion failed: {exc}"}


def format_currency_conversion_info(data: Dict) -> str:
    """Format currency conversion rate information."""
    try:
        exchange_rates = data.get("exchange_rates_used", {})
        original_currencies = data.get("original_currencies", ["SGD"])

        if not exchange_rates:
            return ""

        original_currency = original_currencies[0] if original_currencies else "SGD"
        original_currency_symbol = "S$" if original_currency in ["SGD", "S$"] else original_currency

        rate_parts = []
        for year, rate in sorted(exchange_rates.items()):
            try:
                display_rate = round(1 / rate, 5)
            except ZeroDivisionError:
                continue
            rate_parts.append(f"{original_currency_symbol}{display_rate} for the year {year}")

        if rate_parts:
            rate_text = " and ".join(rate_parts)
            return f"Currency converted from Singapore dollar to US dollar: US$1 = {rate_text}"

        return ""

    except Exception as exc:
        st.error(f"Error formatting conversion info: {exc}")
        return ""


def find_latest_usd_converted_file() -> Optional[str]:
    """Find the most recent USD-converted JSON file in .tmp directory."""
    try:
        tmp_dir = Path(".tmp")
        if not tmp_dir.exists():
            return None

        pattern = re.compile(r"usd_converted_data_(\d{8}_\d{6})\.json")
        files = []

        for file_path in tmp_dir.glob("usd_converted_data_*.json"):
            match = pattern.match(file_path.name)
            if match:
                timestamp_str = match.group(1)
                files.append((file_path, timestamp_str))

        if not files:
            return None

        files.sort(key=lambda x: x[1], reverse=True)
        return str(files[0][0])

    except Exception as exc:
        st.error(f"Error finding USD converted file: {exc}")
        return None
