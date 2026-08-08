import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfbase.pdfmetrics import stringWidth


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

OUTPUT_DIR = PROJECT_ROOT / "reports" / "portfolio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "portfolio_summary.pdf"


# ============================================================
# SETTINGS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

NAVY = colors.HexColor("#142B4A")
LIGHT_BLUE = colors.HexColor("#EAF1F8")
LIGHT_GREY = colors.HexColor("#F4F5F7")
DARK_GREY = colors.HexColor("#444444")

GREEN = colors.HexColor("#16803C")
RED = colors.HexColor("#C62828")
GREY = colors.HexColor("#666666")


# ============================================================
# DATABASE
# ============================================================

def load_data():

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        """
        SELECT
            id,
            company_name
        FROM companies
        """,
        conn
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        conn
    )

    profit_loss = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            net_profit
        FROM profitandloss
        """,
        conn
    )

    cashflow = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        """,
        conn
    )

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            return_on_equity_pct
        FROM financial_ratios
        """,
        conn
    )

    conn.close()

    return (
        companies,
        sectors,
        profit_loss,
        cashflow,
        ratios
    )


# ============================================================
# YEAR NORMALIZATION
# ============================================================

def normalize_year(value):

    if pd.isna(value):
        return None

    text = str(value).strip()

    # Handles:
    # Mar 2024
    # Mar-24
    # Mar-2024
    # Sep 2024

    if "-" in text:

        parts = text.split("-")

        if len(parts) == 2:

            year_part = parts[-1]

            if len(year_part) == 2:
                return int("20" + year_part)

            if len(year_part) == 4:
                return int(year_part)

    parts = text.split()

    for part in reversed(parts):

        if part.isdigit():

            if len(part) == 4:
                return int(part)

            if len(part) == 2:
                return int("20" + part)

    return None


# ============================================================
# CLEAN DATA
# ============================================================

def prepare_data(
    companies,
    sectors,
    profit_loss,
    cashflow,
    ratios
):

    for df in [
        profit_loss,
        cashflow,
        ratios
    ]:

        df["year_num"] = df["year"].apply(
            normalize_year
        )

    # Keep only valid years
    profit_loss = profit_loss[
        profit_loss["year_num"].notna()
    ].copy()

    cashflow = cashflow[
        cashflow["year_num"].notna()
    ].copy()

    ratios = ratios[
        ratios["year_num"].notna()
    ].copy()

    return (
        companies,
        sectors,
        profit_loss,
        cashflow,
        ratios
    )


# ============================================================
# TREND ARROW
# ============================================================

def trend_arrow(current, previous):

    if (
        current is None
        or previous is None
        or pd.isna(current)
        or pd.isna(previous)
    ):
        return "→"

    if previous == 0:

        if current > 0:
            return "↑"

        if current < 0:
            return "↓"

        return "→"

    change = (
        (current - previous)
        / abs(previous)
    ) * 100

    if change > 2:
        return "↑"

    if change < -2:
        return "↓"

    return "→"


# ============================================================
# FORMAT VALUES
# ============================================================

def format_number(value):

    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:,.2f}"


def format_percent(value):

    if value is None or pd.isna(value):
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# GET COMPANY METRICS
# ============================================================

def get_company_metrics(
    company_id,
    profit_loss,
    cashflow,
    ratios
):

    pl = profit_loss[
        profit_loss["company_id"] == company_id
    ].sort_values("year_num")

    cf = cashflow[
        cashflow["company_id"] == company_id
    ].sort_values("year_num")

    roe = ratios[
        ratios["company_id"] == company_id
    ].sort_values("year_num")

    # --------------------------------------------------------
    # Revenue / Profit / Operating Profit
    # --------------------------------------------------------

    pl_latest = None
    pl_previous = None

    if not pl.empty:

        pl_latest = pl.iloc[-1]

        if len(pl) >= 2:
            pl_previous = pl.iloc[-2]

    # --------------------------------------------------------
    # Cash Flow
    # --------------------------------------------------------

    cf_latest = None
    cf_previous = None

    if not cf.empty:

        cf_latest = cf.iloc[-1]

        if len(cf) >= 2:
            cf_previous = cf.iloc[-2]

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    roe_latest = None
    roe_previous = None

    if not roe.empty:

        roe_latest = roe.iloc[-1]

        if len(roe) >= 2:
            roe_previous = roe.iloc[-2]

    # --------------------------------------------------------
    # Values
    # --------------------------------------------------------

    revenue = (
        pl_latest["sales"]
        if pl_latest is not None
        else None
    )

    previous_revenue = (
        pl_previous["sales"]
        if pl_previous is not None
        else None
    )

    operating_profit = (
        pl_latest["operating_profit"]
        if pl_latest is not None
        else None
    )

    previous_operating_profit = (
        pl_previous["operating_profit"]
        if pl_previous is not None
        else None
    )

    net_profit = (
        pl_latest["net_profit"]
        if pl_latest is not None
        else None
    )

    previous_net_profit = (
        pl_previous["net_profit"]
        if pl_previous is not None
        else None
    )

    cfo = (
        cf_latest["operating_activity"]
        if cf_latest is not None
        else None
    )

    previous_cfo = (
        cf_previous["operating_activity"]
        if cf_previous is not None
        else None
    )

    # FCF = CFO + CFI
    fcf = None
    previous_fcf = None

    if cf_latest is not None:

        fcf = (
            cf_latest["operating_activity"]
            +
            cf_latest["investing_activity"]
        )

    if cf_previous is not None:

        previous_fcf = (
            cf_previous["operating_activity"]
            +
            cf_previous["investing_activity"]
        )

    roe_value = (
        roe_latest["return_on_equity_pct"]
        if roe_latest is not None
        else None
    )

    previous_roe = (
        roe_previous["return_on_equity_pct"]
        if roe_previous is not None
        else None
    )

    latest_year = None

    if pl_latest is not None:
        latest_year = pl_latest["year_num"]

    elif cf_latest is not None:
        latest_year = cf_latest["year_num"]

    return {
        "year": latest_year,

        "Revenue": (
            revenue,
            previous_revenue,
            format_number(revenue)
        ),

        "Net Profit": (
            net_profit,
            previous_net_profit,
            format_number(net_profit)
        ),

        "Operating Profit": (
            operating_profit,
            previous_operating_profit,
            format_number(operating_profit)
        ),

        "CFO": (
            cfo,
            previous_cfo,
            format_number(cfo)
        ),

        "Free Cash Flow": (
            fcf,
            previous_fcf,
            format_number(fcf)
        ),

        "ROE": (
            roe_value,
            previous_roe,
            format_percent(roe_value)
        ),
    }


# ============================================================
# KPI TABLE
# ============================================================

def build_kpi_table(metrics):

    rows = [
        [
            "KPI",
            "Latest",
            "Trend"
        ]
    ]

    for name in [
        "Revenue",
        "Net Profit",
        "Operating Profit",
        "CFO",
        "Free Cash Flow",
        "ROE"
    ]:

        current, previous, formatted = metrics[name]

        arrow = trend_arrow(
            current,
            previous
        )

        rows.append([
            name,
            formatted,
            arrow
        ])

    table = Table(
        rows,
        colWidths=[
            65 * mm,
            65 * mm,
            25 * mm
        ],
        repeatRows=1
    )

    table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                NAVY
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "ALIGN",
                (2, 1),
                (2, -1),
                "CENTER"
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.white
            ),

            (
                "FONTNAME",
                (0, 1),
                (0, -1),
                "Helvetica-Bold"
            ),

            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7
            ),
        ])
    )

    return table


# ============================================================
# FOOTER
# ============================================================

def draw_footer(canvas, doc):

    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        7
    )

    canvas.setFillColor(
        DARK_GREY
    )

    canvas.drawString(
        20 * mm,
        10 * mm,
        "NIFTY 100 Portfolio Summary"
    )

    canvas.drawRightString(
        PAGE_WIDTH - 20 * mm,
        10 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()




# ============================================================
# PDF GENERATION
# ============================================================

def generate_pdf():

    (
        companies,
        sectors,
        profit_loss,
        cashflow,
        ratios
    ) = load_data()

    (
        companies,
        sectors,
        profit_loss,
        cashflow,
        ratios
    ) = prepare_data(
        companies,
        sectors,
        profit_loss,
        cashflow,
        ratios
    )

    # --------------------------------------------------------
    # Company + sector lookup
    # --------------------------------------------------------

    sector_lookup = dict(
        zip(
            sectors["company_id"],
            sectors["broad_sector"]
        )
    )

    companies = companies.sort_values(
        "id"
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    story = []

    for index, company in companies.iterrows():

        company_id = str(
            company["id"]
        )

        company_name = str(
            company["company_name"]
        )

        sector = sector_lookup.get(
            company_id,
            "Unknown"
        )

        metrics = get_company_metrics(
            company_id,
            profit_loss,
            cashflow,
            ratios
        )

        # ----------------------------------------------------
        # Header
        # ----------------------------------------------------

        header = Table(
            [
                [
                    Paragraph(
                        f"<b>{company_name}</b>",
                        ParagraphStyle(
                            "HeaderTitle",
                            fontSize=17,
                            textColor=colors.white,
                            fontName="Helvetica-Bold"
                        )
                    )
                ],
                [
                    Paragraph(
                        f"{company_id}  |  {sector}",
                        ParagraphStyle(
                            "HeaderSub",
                            fontSize=9,
                            textColor=colors.white
                        )
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        header.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ])
        )

        story.append(header)

        story.append(
            Spacer(1, 10)
        )

        # ----------------------------------------------------
        # Latest year
        # ----------------------------------------------------

        latest_year = metrics["year"]

        story.append(
            Paragraph(
                f"<b>Latest Financial Year:</b> "
                f"{latest_year if latest_year else 'N/A'}",
                ParagraphStyle(
                    "Year",
                    fontSize=9,
                    textColor=DARK_GREY
                )
            )
        )

        story.append(
            Spacer(1, 8)
        )

        # ----------------------------------------------------
        # KPI TABLE
        # ----------------------------------------------------

        story.append(
            Paragraph(
                "Top 6 KPIs",
                ParagraphStyle(
                    "KPIHeading",
                    fontSize=12,
                    fontName="Helvetica-Bold",
                    textColor=NAVY,
                    spaceAfter=6
                )
            )
        )

        kpi_table = build_kpi_table(
            metrics
        )

        story.append(
            kpi_table
        )

        story.append(
            Spacer(1, 12)
        )

        # ----------------------------------------------------
        # Trend explanation
        # ----------------------------------------------------

        trend_table = Table(
            [
                [
                    Paragraph(
                        "<b>Trend:</b>",
                        ParagraphStyle(
                            "Trend",
                            fontSize=9
                        )
                    ),
                    Paragraph(
                        "↑ Improved",
                        ParagraphStyle(
                            "Up",
                            fontSize=9,
                            textColor=GREEN
                        )
                    ),
                    Paragraph(
                        "↓ Declined",
                        ParagraphStyle(
                            "Down",
                            fontSize=9,
                            textColor=RED
                        )
                    ),
                    Paragraph(
                        "→ Flat (±2%)",
                        ParagraphStyle(
                            "Flat",
                            fontSize=9,
                            textColor=GREY
                        )
                    )
                ]
            ],
            colWidths=[
                35 * mm,
                40 * mm,
                40 * mm,
                55 * mm
            ]
        )

        trend_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BLUE
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.lightgrey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6
                ),
            ])
        )

        story.append(
            trend_table
        )

        # ----------------------------------------------------
        # Page break
        # ----------------------------------------------------

        if index < len(companies) - 1:

            story.append(
                PageBreak()
            )

    doc.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer
    )

    print(
        f"Portfolio summary created: {OUTPUT_FILE}"
    )

    print(
        f"Companies included: {len(companies)}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_pdf()