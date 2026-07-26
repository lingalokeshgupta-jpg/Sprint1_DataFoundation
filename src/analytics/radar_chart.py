import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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

merged["peer_group_name"] = merged[
    "peer_group_name"
].fillna("No peer group assigned")

metrics = [

    "return_on_equity_pct",

    "net_profit_margin_pct",

    "debt_to_equity",

    "free_cash_flow_cr",

    "pat_cagr_5yr",

    "revenue_cagr_5yr",

    "composite_quality_score"

]

peer_average = (

    merged

    .groupby("peer_group_name")[metrics]

    .mean()

)

print(peer_average.head())

company = merged[
    merged["company_id"] == "TCS"
].iloc[0]

peer_group = company["peer_group_name"]

print(peer_group)

company_values = company[metrics].fillna(0).tolist()

print(company_values)

peer_values = peer_average.loc[
    peer_group,
    metrics
].fillna(0).tolist()

print(peer_values)

labels = metrics

angles = np.linspace(
    0,
    2 * np.pi,
    len(labels),
    endpoint=False
)

company_values += [company_values[0]]
peer_values += [peer_values[0]]

angles = np.concatenate(
    (angles, [angles[0]])
)

fig = plt.figure(figsize=(8, 8))

ax = plt.subplot(
    111,
    polar=True
)

ax.plot(
    angles,
    company_values,
    linewidth=2,
    label="Company"
)

ax.fill(
    angles,
    company_values,
    alpha=0.25
)

ax.plot(
    angles,
    peer_values,
    linestyle="--",
    linewidth=2,
    label="Peer Average"
)

ax.set_xticks(
    angles[:-1]
)

ax.set_xticklabels(labels)

ax.set_title(
    company["company_id"],
    fontsize=14
)

ax.legend(
    loc="upper right"
)

output_folder = Path(
    "reports/radar_charts"
)

output_folder.mkdir(
    parents=True,
    exist_ok=True
)

plt.savefig(

    output_folder /

    f"{company['company_id']}_radar.png",

    dpi=300,

    bbox_inches="tight"

)

plt.close()

print("Radar chart created successfully!")