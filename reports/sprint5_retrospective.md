# Sprint 5 Retrospective

## Sprint Overview

Sprint 5 focused on transforming the financial analysis outputs into
professional, presentation-ready reports for the NIFTY 100 companies.

## What Went Well

- Completed Cash Flow Intelligence analysis.
- Generated capital allocation patterns for the available companies.
- Created capital allocation distribution and year-over-year pattern change reports.
- Generated 2-page company tearsheets using ReportLab.
- Successfully generated 92 company tearsheets.
- Validated the company PDFs to ensure they contain two pages.
- Generated sector-level reports for all sectors available in the dataset.
- Created a portfolio-level summary report.
- Added trend indicators to make KPI movement easier to understand.
- Organized generated reports into dedicated output directories.

## Challenges

- Identified missing cash-flow data for ATGL.
- Found duplicate company-year records in the original cash-flow data.
- Cleaned duplicate cash-flow records before generating capital allocation reports.
- Handled inconsistent year formats such as `Mar 2024` and `Mar-24`.
- Verified PDF generation and page counts to prevent blank or incomplete reports.

## What Could Be Improved

- Automate more validation checks before report generation.
- Improve handling of companies with incomplete historical data.
- Add stronger visual validation for generated PDFs.
- Add automated tests for report content and layout.
- Improve the portfolio dashboard with additional financial indicators.

## Key Deliverables

- Cash Flow Intelligence Excel report
- Capital Allocation Distribution CSV
- Pattern Changes CSV
- Company Tearsheets
- Sector Reports
- Portfolio Summary PDF
- Skipped Tearsheet Log

## Sprint Outcome

The sprint successfully converted the processed financial data into
company-level, sector-level, and portfolio-level reporting outputs
that can be used for analysis and presentation.
