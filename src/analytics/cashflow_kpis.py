import pandas as pd


# --------------------------------------------------
# Free Cash Flow
# --------------------------------------------------

def free_cash_flow(operating_activity, investing_activity):
    """
    FCF = CFO + Investing Activity
    Negative values are allowed.
    """
    return operating_activity + investing_activity


# --------------------------------------------------
# CFO Quality Score
# --------------------------------------------------

def cfo_quality_score(cfo_values, pat_values):
    """
    Average CFO/PAT ratio over available years.
    """

    ratios = []

    for cfo, pat in zip(cfo_values, pat_values):

        if pat == 0:
            continue

        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return None

    average = sum(ratios) / len(ratios)

    if average > 1:
        return round(average,2),"High Quality"
    
    if average >= 0.5:
        return round(average,2),"Moderate"

    return round(average,2),"Accrual Risk"


# --------------------------------------------------
# CapEx Intensity
# --------------------------------------------------

def capex_intensity(investing_activity, sales):

    if sales == 0:
        return None, None

    value = abs(investing_activity) / sales * 100

    if value < 3:
        label = "Asset Light"

    elif value <= 8:
        label = "Moderate"

    else:
        label = "Capital Intensive"

    return round(value, 2), label


# --------------------------------------------------
# FCF Conversion Rate
# --------------------------------------------------

def fcf_conversion_rate(fcf, operating_profit):

    if operating_profit == 0:
        return None

    return round(
        (fcf / operating_profit) * 100,
        2
    )


# --------------------------------------------------
# Capital Allocation Pattern
# --------------------------------------------------

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=1):

    signs = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-"
    )

    if signs == ("+", "-", "-"):

        if cfo_pat_ratio > 1:
            return "Shareholder Returns"

        return "Reinvestor"

    if signs == ("+", "+", "-"):
        return "Liquidating Assets"

    if signs == ("-", "+", "+"):
        return "Distress Signal"

    if signs == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if signs == ("+", "+", "+"):
        return "Cash Accumulator"

    if signs == ("-", "-", "-"):
        return "Pre-Revenue"

    if signs == ("+", "-", "+"):
        return "Mixed"

    return "Unknown"


# --------------------------------------------------
# Generate CSV
# --------------------------------------------------

def generate_capital_allocation(df, output_path):

    result = pd.DataFrame()

    result["company_id"] = df["company_id"]
    result["year"] = df["year"]

    result["cfo_sign"] = df["operating_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["cfi_sign"] = df["investing_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["cff_sign"] = df["financing_activity"].apply(
        lambda x: "+" if x >= 0 else "-"
    )

    result["pattern_label"] = df.apply(
        lambda row:
        capital_allocation_pattern(
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        ),
        axis=1
    )

    result.to_csv(output_path, index=False)

    return result

import sqlite3

conn = sqlite3.connect("db/nifty100.db")

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

financials = pd.read_sql(
    "SELECT * FROM profitandloss",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

balancesheet = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

capital = pd.read_csv(
    "output/capital_allocation.csv"
)

results = []
distress = []

for company in companies["id"]:

    fin = financials[
        financials["company_id"] == company
    ].sort_values("year")

    cf = cashflow[
        cashflow["company_id"] == company
    ].sort_values("year")

    bs = balancesheet[
        balancesheet["company_id"] == company
    ].sort_values("year")

    sector = sectors[
        sectors["company_id"] == company
    ]

    if fin.empty or cf.empty:
        continue


    quality = cfo_quality_score(
        cf["operating_activity"].tail(5),
        fin["net_profit"].tail(5)
    )

    if quality is None:
        score = None
        label = "Unknown"
    else:
        score, label = quality

    capex_pct, capex_label = capex_intensity(
        cf.iloc[-1]["investing_activity"],
        fin.iloc[-1]["sales"]
    )

    latest_cf = cf.iloc[-1]

    if len(cf) >= 5:

        first_fcf = free_cash_flow(
            cf.iloc[-5]["operating_activity"],
            cf.iloc[-5]["investing_activity"]
        )

        last_fcf = free_cash_flow(
            cf.iloc[-1]["operating_activity"],
            cf.iloc[-1]["investing_activity"]
        )

        if first_fcf > 0 and last_fcf > 0:

            fcf_cagr = (
                ((last_fcf / first_fcf) ** (1 / 4)) - 1
            ) * 100

        else:

            fcf_cagr = None

    else:

        fcf_cagr = None

    distress_flag = (
        latest_cf["operating_activity"] < 0
        and
        latest_cf["financing_activity"] > 0
    )

    deleveraging = False

    if len(bs) >= 2:

        if (
            latest_cf["financing_activity"] < 0
            and
            bs.iloc[-1]["borrowings"]
            <
            bs.iloc[-2]["borrowings"]
        ):

            deleveraging = True

    fcf = free_cash_flow(
        latest_cf["operating_activity"],
        latest_cf["investing_activity"]
    )

    conversion = fcf_conversion_rate(
        fcf,
        fin.iloc[-1]["operating_profit"]
    )

    allocation = capital[
        capital["company_id"] == company
    ]

    if not allocation.empty:

        allocation_label = allocation.iloc[-1]["pattern_label"]

    else:

        allocation_label = None

    if sector.empty:
        sector_name = "Unknown"
    else:
        sector_name = sector.iloc[0]["broad_sector"]

    results.append({

        "company_id": company,


        "sector": sector_name,

        "cfo_quality_score": score,

        "cfo_quality_label": label,

        "capex_intensity_pct": capex_pct,

        "capex_label": capex_label,

        "fcf_cagr_5yr": round(fcf_cagr, 2) if fcf_cagr is not None else None,

        "fcf_conversion_pct": conversion,

        "distress_flag": distress_flag,

        "deleveraging_flag": deleveraging,

        "capital_allocation_label": allocation_label

        })

    if distress_flag:

        distress.append({

            "company_id": company,

            "CFO": latest_cf["operating_activity"],

            "CFF": latest_cf["financing_activity"],

            "latest_net_profit": fin.iloc[-1]["net_profit"]

        })

cashflow_df = pd.DataFrame(results)

cashflow_df.to_excel(
    "output/cashflow_intelligence.xlsx",
    index=False
)
pd.DataFrame(distress).to_csv(
    "output/distress_alerts.csv",
    index=False
)



print("Cash Flow Intelligence Created Successfully!")
print(cashflow_df.shape)

print("=" * 50)
print("Cash Flow Intelligence Module")
print("=" * 50)
print("Companies Processed :", len(cashflow_df))
print("Skipped Companies :", len(companies) - len(cashflow_df))
print("Skipped Company IDs :",
      list(set(companies["id"]) - set(cashflow_df["company_id"])))
print("Distress Alerts :", len(distress))

missing = []

for company in companies["id"]:

    fin = financials[
        financials["company_id"] == company
    ]

    cf = cashflow[
        cashflow["company_id"] == company
    ]

    if fin.empty or cf.empty:
        missing.append(company)

print(missing)
print("Missing:", len(missing))