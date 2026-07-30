import sqlite3
import pandas as pd

conn = sqlite3.connect(
    "db/nifty100.db"
)

companies = pd.read_sql(
    "SELECT * FROM companies",
    conn
)

ratios = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

balancesheet = pd.read_sql(
    "SELECT * FROM balancesheet",
    conn
)

cashflow = pd.read_sql(
    "SELECT * FROM cashflow",
    conn
)

market_cap = pd.read_sql(
    "SELECT * FROM market_cap",
    conn
)

sectors = pd.read_sql(
    "SELECT * FROM sectors",
    conn
)

results = []

for company in companies["id"]:

    ratio = ratios[
        ratios["company_id"] == company
    ].sort_values("year")

    cash = cashflow[
        cashflow["company_id"] == company
    ].sort_values("year")

    if ratio.empty:
        continue

    latest = ratio.iloc[-1]

    if len(ratio) >= 3:

        last3 = ratio.tail(3)

        if (
            last3["return_on_equity_pct"] > 20
        ).all():

            results.append({

                "company_id": company,

                "type": "Pro",

                "rule_id": "P1",

                "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",

                "confidence_pct": 95

            })
    if len(ratio) >= 5:
    
                last5 = ratio.tail(5)
    
                if (
                    last5["free_cash_flow_cr"] > 0
                ).all():
    
                    results.append({
    
                        "company_id": company,
    
                        "type": "Pro",
    
                        "rule_id": "P2",
    
                        "text": "Strong free cash flow generation over 5 years signals healthy business fundamentals.",
    
                        "confidence_pct": 90
    
                    })

    if latest["debt_to_equity"] == 0:
        
        results.append({
             
            "company_id": company,

            "type": "Pro",
        
            "rule_id": "P3",
        
            "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
        
            "confidence_pct": 100
        
        })
    if latest["revenue_cagr_5yr"] > 15:

        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "P4",
            "text": "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum.",
            "confidence_pct": 88

        })

    if latest["operating_profit_margin_pct"] > 25:

        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "P5",
            "text": "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
            "confidence_pct": 90

        })
    if latest["pat_cagr_5yr"] > 20:

        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "P6",
            "text": "Net profit compounding at above 20% over 5 years creates significant shareholder value.",
            "confidence_pct": 92

        })
    if (
        latest["interest_coverage"] > 10
        or
        latest["debt_to_equity"] == 0
    ):

        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "P7",
            "text": "Very high interest coverage ratio reflects negligible financial stress from debt servicing.",
            "confidence_pct": 90

        })

    market = market_cap[
        market_cap["company_id"] == company
    ]

    if not market.empty:

        latest_market = market.iloc[-1]

        if (
            latest_market["dividend_yield_pct"] > 2
            and
            latest["free_cash_flow_cr"] > 0
        ):

            results.append({

                "company_id": company,
                "type": "Pro",
                "rule_id": "P8",
                "text": "Consistent dividend yield above 2% backed by positive free cash flow.",
                "confidence_pct": 88

            })
    if latest["eps_cagr_5yr"] > 15:
    
        results.append({
    
            "company_id": company,
            "type": "Pro",
            "rule_id": "P9",
            "text": "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding.",
            "confidence_pct": 90
    
        })
    
    if len(ratio) >= 3:
        roe = ratio.tail(3)["return_on_equity_pct"].tolist()
            
        if roe[0] < roe[1] < roe[2]:
            
            results.append({
            
                "company_id": company,
                "type": "Pro",
                "rule_id": "P10",
                "text": "Return on equity improving for 3 consecutive years shows strengthening business quality.",
                "confidence_pct": 85
            
        })
    
    if latest["pat_cagr_5yr"] > latest["revenue_cagr_5yr"]:
    
        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "P11",
            "text": "Revenue growing slower than profits shows improving operating leverage and scale benefits.",
            "confidence_pct": 88
    
        })
    balance = balancesheet[
        balancesheet["company_id"] == company
    ].sort_values("year")
    
    if len(balance) >= 2:
    
        last2 = balance.tail(2)
    
        assets = last2["total_assets"].tolist()
    
        debt = last2["borrowings"].tolist()
    
        if assets[1] > assets[0] and debt[1] < debt[0]:
    
             results.append({

                "company_id": company,
                "type": "Pro",
                "rule_id": "P12",
                "text": "Growing asset base funded by internal accruals reflects self-sustaining growth.",
                "confidence_pct": 87

            })
    
    sector_data = sectors[
        sectors["company_id"] == company
    ]

    if not sector_data.empty:
        sector = sector_data.iloc[0]["broad_sector"]
    else:
        sector = ""
            
    if (
        latest["debt_to_equity"] > 2
        and
        sector != "Financials"
    ):

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C1",
            "text": f"Debt-to-equity ratio of {latest['debt_to_equity']:.2f} is elevated for a non-financial company and warrants monitoring.",
            "confidence_pct": 90

        })
    
    if len(ratio) >= 3:
    
        last3 = ratio.tail(3)
    
        if (last3["free_cash_flow_cr"] < 0).all():
    
            results.append({
    
                "company_id": company,
                "type": "Con",
                "rule_id": "C2",
                "text": "Free cash flow negative for 3 consecutive years raises concern about cash generation quality.",
                "confidence_pct": 92
    
            })
    if len(ratio) >= 3:
    
        opm = ratio.tail(3)[
            "operating_profit_margin_pct"
        ].tolist()
    
        if opm[0] > opm[1] > opm[2]:
    
            results.append({
    
                "company_id": company,
                "type": "Con",
                "rule_id": "C3",
                "text": "Operating margins declining for 3 consecutive years suggest pricing or cost pressure.",
                "confidence_pct": 85
    
            })
    if latest["net_profit_margin_pct"] < 0:
    
        results.append({
    
            "company_id": company,
            "type": "Con",
            "rule_id": "C4",
            "text": "Company reported a net loss in the most recent financial year.",
            "confidence_pct": 95
    
        })
    pros_cons = pd.DataFrame(results)
    
    pros_cons.to_csv(
        "output/pros_cons_generated.csv",
        index=False
    ) 
    if len(ratio) >= 2:

        revenue = ratio.tail(2)["revenue_cagr_5yr"].tolist()

        if revenue[1] < revenue[0]:

            results.append({

                "company_id": company,
                "type": "Con",
                "rule_id": "C5",
                "text": "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss.",
                "confidence_pct": 80

            })
    if latest["interest_coverage"] < 1.5:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C6",
            "text": "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations.",
            "confidence_pct": 95

        })

    if latest["dividend_payout_ratio_pct"] > 100:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C7",
            "text": "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable.",
            "confidence_pct": 90

        })

    if len(ratio) >= 3:

        debt = ratio.tail(3)["debt_to_equity"].tolist()

        if debt[0] < debt[1] < debt[2]:

            results.append({

                "company_id": company,
                "type": "Con",
                "rule_id": "C8",
                "text": "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk.",
                "confidence_pct": 85

            })
    profit_loss = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    pl = profit_loss[
        profit_loss["company_id"] == company
    ].sort_values("year")

    if len(pl) >= 3:

        eps = pl.tail(3)["eps"].tolist()

        if eps[0] > eps[1] > eps[2]:

            results.append({

                "company_id": company,
                "type": "Con",
                "rule_id": "C9",
                "text": "Earnings per share declining for 3 consecutive years reflects deteriorating profitability.",
                "confidence_pct": 90

            })

    if latest["revenue_cagr_5yr"] < 5:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C12",
            "text": "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum.",
            "confidence_pct": 80

        })
    if latest["asset_turnover"] < 0.5:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C10",
            "text": "Low asset turnover suggests inefficient utilisation of company assets.",
            "confidence_pct": 75

        })
    if latest["cash_from_operations_cr"] < 0 and latest["total_debt_cr"] > 0:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "C11",
            "text": "Negative operating cash flow combined with debt may increase financial risk.",
            "confidence_pct": 82

        })
pros_cons = pd.DataFrame(results)
# ----------------------------------------
# Ensure every company has at least
# one Pro and one Con
# ----------------------------------------

temp = pd.DataFrame(results)

for company in companies["id"]:

    company_rows = temp[temp["company_id"] == company]

    has_pro = (company_rows["type"] == "Pro").any()
    has_con = (company_rows["type"] == "Con").any()

    if not has_pro:

        results.append({
            "company_id": company,
            "type": "Pro",
            "rule_id": "PF",
            "text": "Business fundamentals appear stable based on the available financial data.",
            "confidence_pct": 65
        })

    if not has_con:

        results.append({
            "company_id": company,
            "type": "Con",
            "rule_id": "CF",
            "text": "No major financial warning signals were detected, but periodic monitoring is recommended.",
            "confidence_pct": 65
        })
pros_cons = pd.DataFrame(results)

pros_cons.to_csv(
    "output/pros_cons_generated.csv",
    index=False
)
print(pros_cons.shape)
print("Saved : output/pros_cons_generated.csv")

print(pros_cons.head())

print(pros_cons.shape)
print(companies.shape)
print(ratios.shape)
print(balancesheet.shape)
print(cashflow.shape)
print(market_cap.shape)

summary = pros_cons.groupby(
    ["company_id", "type"]
).size().unstack(fill_value=0)

summary["has_pro"] = summary.get("Pro", 0) > 0
summary["has_con"] = summary.get("Con", 0) > 0

missing = summary[
    ~(summary["has_pro"] & summary["has_con"])
]

print("\n========== Verification ==========")
print("Companies Missing Pro/Con :", len(missing))

if not missing.empty:
    print(missing)
else:
    print("✅ Every company has at least one Pro and one Con.")

summary = pros_cons.groupby(["company_id", "type"]).size().unstack(fill_value=0)

for company in companies["id"]:

    if company not in summary.index:
        summary.loc[company] = [0, 0]

    if summary.loc[company].get("Con", 0) == 0:

        results.append({

            "company_id": company,
            "type": "Con",
            "rule_id": "CF",
            "text": "No major financial red flags detected based on the available financial data, but periodic monitoring is recommended.",
            "confidence_pct": 65

        })

    if summary.loc[company].get("Pro", 0) == 0:

        results.append({

            "company_id": company,
            "type": "Pro",
            "rule_id": "PF",
            "text": "The company demonstrates stable operating performance based on the available financial information.",
            "confidence_pct": 65

        })
    pros_cons = pd.DataFrame(results)

pros_cons.to_csv(
    "output/pros_cons_generated.csv",
    index=False
)