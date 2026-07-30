import sqlite3
import pandas as pd
import re

conn = sqlite3.connect(
    "db/nifty100.db"
)

analysis = pd.read_sql(
    """
    SELECT *
    FROM analysis
    """,
    conn
)

print(analysis.head())

print(analysis.columns.tolist())

pattern = r"(?:(\d+)\s*Years?|1\s*Year|TTM|Last\s*Year):?\s*([-+]?\d*\.?\d+)%"

target_columns = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]

parsed = []

failures = []

print(analysis.columns.tolist())

for _, row in analysis.iterrows():

    company = row["company_id"]

    for metric in target_columns:

        text = str(row[metric])

        match = re.search(pattern, text)

        if match:

            period = match.group(1)

            if period is None:

                if "TTM" in text:
                    period = "TTM"

                elif "Last Year" in text:
                    period = "Last Year"

                elif "1 Year" in text:
                    period = 1

            else:
                period = int(period)

            parsed.append({

                "company_id": company,

                "metric_type": metric,

                "period_years": period,

                "value_pct": float(match.group(2))

            })

        else:

            failures.append({

                "company_id": company,

                "metric_type": metric,

                "original_text": text

            })
parsed_df = pd.DataFrame(parsed)

failure_df = pd.DataFrame(failures)

parsed_df.to_csv(
    "output/analysis_parsed.csv",
    index=False
)

failure_df.to_csv(
    "output/parse_failures.csv",
    index=False
)

print("\n========== NLP Parser ==========")

print("Parsed Records :", len(parsed_df))

print("Failed Records :", len(failure_df))

print("Saved : output/analysis_parsed.csv")

print("Saved : output/parse_failures.csv")

financial_ratios = pd.read_sql(
    """
    SELECT
        company_id,
        revenue_cagr_5yr,
        pat_cagr_5yr,
        return_on_equity_pct
    FROM financial_ratios
    """,
    conn
)

review = []

for _, row in parsed_df.iterrows():

    company = row["company_id"]
    metric = row["metric_type"]
    parsed_value = row["value_pct"]

    ratio = financial_ratios[
        financial_ratios["company_id"] == company
    ]

    if ratio.empty:
        continue

    latest = ratio.iloc[-1]

    if metric == "compounded_sales_growth":
        computed = latest["revenue_cagr_5yr"]

    elif metric == "compounded_profit_growth":
        computed = latest["pat_cagr_5yr"]

    elif metric == "roe":
        computed = latest["return_on_equity_pct"]

    else:
        continue

    if pd.isna(computed):
        continue

    difference = abs(parsed_value - computed)

    if difference > 5:

        review.append({

            "company_id": company,

            "metric": metric,

            "parsed_value": parsed_value,

            "computed_value": computed,

            "difference": difference

        })

review_df = pd.DataFrame(review)

review_df.to_csv(
    "output/manual_review.csv",
    index=False
)

print(
    f"Manual Review Required : {len(review_df)}"
)

print(
    "Saved : output/manual_review.csv"
)