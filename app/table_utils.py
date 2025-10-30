"""Transform financial JSON payloads into tabular data."""
from typing import Dict

import pandas as pd


def generate_revenue_profit_table(data: Dict) -> pd.DataFrame:
    """Generate Revenue and Profit table from financial data."""
    rows = []
    year_keys = [key for key in data.keys() if key.startswith("year_")]

    for year_key in year_keys:
        year_data = data.get(year_key, {})
        if year_data:
            rows.append(
                {
                    "Year": year_data.get("year", ""),
                    "Revenue": year_data.get("revenue", ""),
                    "Profit before taxes": year_data.get("profit_before_tax", ""),
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty and "Year" in df.columns:
        df["Year_int"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.sort_values("Year_int").drop("Year_int", axis=1)
        df = df.reset_index(drop=True)

    return df


def generate_cash_flow_table(data: Dict) -> pd.DataFrame:
    """Generate Cash Flow table from financial data."""
    rows = []
    year_keys = [key for key in data.keys() if key.startswith("year_")]

    for year_key in year_keys:
        year_data = data.get(year_key, {})
        if year_data:
            rows.append(
                {
                    "Year": year_data.get("year", ""),
                    "Net cash used in/generated from operating activities": year_data.get("net_cash_operating", ""),
                    "Net cash used in investing activities": year_data.get("net_cash_investing", ""),
                    "Net cash provided by/used in financing activities": year_data.get("net_cash_financing", ""),
                    "Cash and cash equivalents at end of financial year": year_data.get("cash_end_of_year", ""),
                }
            )

    df = pd.DataFrame(rows)
    if not df.empty and "Year" in df.columns:
        df["Year_int"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.sort_values("Year_int").drop("Year_int", axis=1)
        df = df.reset_index(drop=True)

    return df
