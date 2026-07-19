# Sprint 2 Retrospective

## Sprint Overview

Sprint 2 focused on building a financial analytics engine capable of calculating key financial ratios, validating results, handling edge cases, and storing the computed metrics in the SQLite database. The sprint also included quality checks, anomaly detection, and documentation to ensure the calculations were accurate and reliable.

---

## Work Completed

### Financial Ratio Calculations
Implemented the following financial KPIs:

- Net Profit Margin
- Operating Profit Margin
- Return on Equity (ROE)
- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Asset Turnover Ratio
- Free Cash Flow (FCF)
- CapEx Intensity
- Earnings Per Share (EPS)
- Book Value Per Share
- Dividend Payout Ratio
- Total Debt
- Cash From Operations

---

### CAGR Engine

Developed a 5-Year CAGR calculation engine for:

- Revenue CAGR
- PAT CAGR
- EPS CAGR

The implementation includes handling multiple edge cases such as:

- Missing historical data
- Zero starting values
- Negative values
- Insufficient years of financial history
- Invalid calculations
- Division-by-zero scenarios

---

### Composite Quality Score

Created a composite quality scoring model based on:

- Return on Equity
- Debt-to-Equity Ratio
- Interest Coverage
- Free Cash Flow
- Net Profit Margin

The score helps identify financially strong companies using multiple performance indicators.

---

### Financial Sector Exception

Implemented a special rule for companies in the Financials sector.

Since banks and financial institutions naturally operate with higher leverage, high debt-to-equity ratios are excluded from leverage warnings for these companies.

---

### Ratio Validation

Validated calculated ROE and ROCE values against the original dataset by comparing:

- Calculated ROE vs Dataset ROE
- Calculated ROCE vs Dataset ROCE

The differences were recorded for further analysis.

---

### Edge Case Logging

Generated `ratio_edge_cases.log` to capture companies with significant differences between calculated and reported ratios.

Each anomaly was categorized into one of the following:

- Version Difference
- Formula Discrepancy
- Data Source Issue

This makes future debugging and validation easier.

---

## Challenges Faced

- Handling missing and inconsistent financial data.
- Aligning financial statements from multiple datasets.
- Managing edge cases in CAGR calculations.
- Implementing different business rules for financial sector companies.
- Validating calculated KPIs against source data.

---

## Key Decisions

- Used reusable Python functions for all KPI calculations.
- Stored computed KPIs in the SQLite `financial_ratios` table.
- Implemented anomaly categorization for easier investigation.
- Used a weighted composite quality score to evaluate company fundamentals.
- Excluded financial companies from debt-related warnings.

---

## Deliverables Completed

- Financial ratio calculation engine
- CAGR calculation engine
- Cash flow KPI module
- Composite Quality Score
- Financial sector carve-out
- ROE and ROCE validation
- Ratio anomaly log
- SQLite `financial_ratios` table
- Unit test implementation
- Sprint documentation

---

## Lessons Learned

This sprint improved my understanding of financial statement analysis, KPI calculations, financial data validation, SQLite integration, and handling real-world data quality issues. I also gained experience in writing modular Python code and documenting analytical workflows for future maintenance.

---

## Conclusion

Sprint 2 was successfully completed by implementing the complete financial analytics pipeline, validating the calculated metrics, documenting anomalies, and storing all computed KPIs in the database. The project is now ready for further analysis, screening, and dashboard development in the next sprint.