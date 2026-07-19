from src.analytics.ratios import *

print(net_profit_margin(250,1000))
print(operating_profit_margin(150,1000))
print(check_opm_difference(20,18))
print(roe(300,500,700))
print(roce(350,500,700,200))
print(roa(250,5000))
print(financial_sector_roce_check(18,"Industrials"))

from src.analytics.ratios import *

print(debt_to_equity(1000,500,500))
print(debt_to_equity(0,500,500))

print(high_leverage_flag(6,"Industrials"))
print(high_leverage_flag(6,"Financials"))

print(interest_coverage_ratio(400,100,50))
print(icr_label(None))
print(icr_warning(1.2))

print(net_debt(500,100))

print(asset_turnover(1000,5000))


from src.analytics.cagr import *

print(revenue_cagr(100,200,5))
print(revenue_cagr(100,-50,5))
print(revenue_cagr(-50,100,5))
print(revenue_cagr(-50,-20,5))
print(revenue_cagr(0,200,5))
print(revenue_cagr(None,200,5))



from src.analytics.cashflow_kpis import *

print(free_cash_flow(500, -200))

print(cfo_quality_score(
    [100,120,140],
    [80,100,120]
))

print(capex_intensity(-50,1000))

print(fcf_conversion_rate(300,500))

print(capital_allocation_pattern(
    100,
    -50,
    -20,
    1.2
))