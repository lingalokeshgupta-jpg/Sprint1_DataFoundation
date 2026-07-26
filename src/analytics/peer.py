import sqlite3
import pandas as pd

conn = sqlite3.connect("db/nifty100.db")

financial_ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

peer_groups = pd.read_sql(
    "SELECT * FROM peer_groups",
    conn
)

merged = financial_ratios.merge(

    peer_groups,

    on="company_id",

    how="left"

)

merged["peer_group_name"] = merged["peer_group_name"].fillna(
    "No peer group assigned"
)

metrics = [

    "return_on_equity_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "pat_cagr_5yr",

    "revenue_cagr_5yr",

    "eps_cagr_5yr",

    "interest_coverage",

    "asset_turnover"

]

ranked_data = []

for metric in metrics:

    temp = merged.copy()

    temp["metric"] = metric

    temp["value"] = temp[metric]

    temp["percentile_rank"] = (
        temp.groupby("peer_group_name")[metric]
        .rank(pct=True)
    )

    # Lower D/E is better
    if metric == "debt_to_equity":
        temp["percentile_rank"] = (
            1 - temp["percentile_rank"]
        )

    ranked_data.append(
        temp[
            [
                "company_id",
                "peer_group_name",
                "year",
                "metric",
                "value",
                "percentile_rank"
            ]
        ]
    )

peer_percentiles = pd.concat(
    ranked_data,
    ignore_index=True
)

print(

    merged["peer_group_name"]

    .value_counts()

)
print(financial_ratios.shape)
print(peer_groups.shape)
print()

print("Merged Shape")

print(merged.shape)

print()

print(merged.head())

print()

print(merged.columns.tolist())
print(financial_ratios.head())

print(peer_groups.head())

print(peer_percentiles.head())

print(peer_percentiles.shape)

peer_percentiles.to_sql(
    "peer_percentiles",
    conn,
    if_exists="replace",
    index=False
)

print("peer_percentiles table created successfully!")

check = pd.read_sql(
    "SELECT * FROM peer_percentiles LIMIT 10",
    conn
)

print(check)

count = pd.read_sql(
    "SELECT COUNT(*) AS total_rows FROM peer_percentiles",
    conn
)

print(count)

conn.close()