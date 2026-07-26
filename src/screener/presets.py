import sqlite3
import pandas as pd

from .engine import apply_filters

conn = sqlite3.connect("db/nifty100.db")

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

quality_compounder = {

    "roe_min": 15,

    "debt_to_equity_max": 1,

    "free_cash_flow_min": 0,

    "revenue_cagr_5yr_min": 10
}



value_pick = {

    "debt_to_equity_max": 2

}
# TODO:
# Add P/E
# Add P/B
# Add Dividend Yield

growth_accelerator = {

    "pat_cagr_5yr_min":20,

    "revenue_cagr_5yr_min":15,

    "debt_to_equity_max":2

}


dividend_champion = {

    "free_cash_flow_min":0

}

# TODO:
# dividend_payout_ratio_max
# dividend_yield

debt_free_bluechip = {

    "roe_min":12,

    "debt_to_equity_max":0

}

turnaround_watch = {

    "free_cash_flow_min":0

}

presets = {

    "Quality Compounder":quality_compounder,

    "Value Pick":value_pick,

    "Growth Accelerator":growth_accelerator,

    "Dividend Champion":dividend_champion,

    "Debt-Free Blue Chip":debt_free_bluechip,

    "Turnaround Watch":turnaround_watch

}

if __name__ == "__main__":

    conn = sqlite3.connect("db/nifty100.db")

    financial_ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

for name, preset in presets.items():

    result = apply_filters(financial_ratios,preset)

    print("-"*50)

    print(name)

    print(result.shape)

    print(
    result[
        [
            "company_id",
            "year",
            "return_on_equity_pct",
            "debt_to_equity",
            "free_cash_flow_cr",
            "revenue_cagr_5yr",
            "pat_cagr_5yr",
            "composite_quality_score"
        ]
    ].head()
)

conn.close()

