import pandas as pd
from pathlib import Path

RAW_DATA = Path("data/raw")

FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
}


def load_excel(file_name, skip_rows=0):
    """Load an Excel file and return a DataFrame."""
    file_path = RAW_DATA / file_name
    return pd.read_excel(file_path, skiprows=skip_rows)


SKIP_ROWS = {
    "companies": 1,
    "profitandloss": 1,
    "balancesheet": 1,
    "cashflow": 1,
    "analysis": 1,
    "documents": 1,
    "prosandcons": 1,
    "financial_ratios": 0,
    "market_cap": 0,
    "peer_groups": 0,
    "sectors": 0,
    "stock_prices": 0,
}

def load_all_files():
    dataframes = {}

    for key, file in FILES.items():
        df = load_excel(file, SKIP_ROWS[key])
        dataframes[key] = df
        print(f"{key}: {len(df)} rows loaded")

    return dataframes

if __name__ == "__main__":
    data = load_all_files()

    for name, df in data.items():
        print(f"\n{name.upper()} COLUMNS")
        print(df.columns.tolist())