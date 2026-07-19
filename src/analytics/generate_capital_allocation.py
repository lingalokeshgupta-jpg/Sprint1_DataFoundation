import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Make src and src/etl importable
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "etl"))

from loader import load_all_files
from src.analytics.cashflow_kpis import generate_capital_allocation

# Load datasets
dataframes = load_all_files()

cashflow_df = dataframes["cashflow"]

generate_capital_allocation(
    cashflow_df,
    "output/capital_allocation.csv"
)

print("capital_allocation.csv created successfully.")