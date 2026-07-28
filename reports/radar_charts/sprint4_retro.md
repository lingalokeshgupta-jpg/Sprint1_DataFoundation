# Sprint 4 Retrospective

## What Went Well

- Successfully developed an 8-page Streamlit dashboard.
- Integrated SQLite database with cached queries.
- Built interactive charts using Plotly.
- Implemented company screener and valuation module.
- Generated Excel and CSV outputs automatically.

## Challenges

- Handling missing financial values.
- Resolving merge conflicts between multiple tables.
- Fixing Plotly chart configuration issues.
- Managing Streamlit cache behaviour.

## UX Decisions

- Used sidebar navigation for easier page switching.
- Displayed KPIs using metric cards.
- Added dropdowns for company and sector selection.
- Used interactive Plotly visualizations.

## Performance

- Cached database queries using `@st.cache_data`.
- Reduced repeated database access.
- Company Profile loads within the target response time.

## Improvements for Future

- Add authentication.
- Deploy dashboard to the cloud.
- Add advanced valuation models.
- Introduce portfolio analysis features.