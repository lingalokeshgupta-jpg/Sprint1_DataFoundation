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