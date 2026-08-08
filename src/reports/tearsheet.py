"""
Day 33 - PDF Company Tearsheet

Generates a 2-page company tearsheet using ReportLab.

Page 1:
- Navy header
- 6 KPI tiles
- 10-year Revenue and Net Profit bar charts
- ROE and ROCE line chart

Page 2:
- Balance Sheet composition stacked bar
- Cash Flow waterfall
- Pros
- Cons
- Capital Allocation badge
"""

import sqlite3
import re
from pathlib import Path

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    LongTable,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.graphics.shapes import (
    Drawing,
    Rect,
    String,
    Line,
)
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = REPORTS_DIR / "tearsheets"
SECTOR_OUTPUT_DIR = REPORTS_DIR / "sector"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SECTOR_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CAPITAL_FILE = (
    PROJECT_ROOT
    / "output"
    / "cashflow_intelligence.xlsx"
)


# ============================================================
# PAGE SETTINGS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN = 12 * mm


# ============================================================
# COLORS
# ============================================================

NAVY = colors.HexColor("#0B1F3A")
LIGHT_NAVY = colors.HexColor("#EAF0F8")

GREEN = colors.HexColor("#198754")
LIGHT_GREEN = colors.HexColor("#EAF7EF")

RED = colors.HexColor("#C62828")
LIGHT_RED = colors.HexColor("#FCECEC")

GREY = colors.HexColor("#6B7280")
LIGHT_GREY = colors.HexColor("#F3F4F6")
DARK = colors.HexColor("#1F2937")
WHITE = colors.white


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TearsheetTitle",
    parent=styles["Normal"],
    fontSize=18,
    leading=21,
    textColor=WHITE,
    alignment=TA_LEFT,
    fontName="Helvetica-Bold",
)

SUBTITLE_STYLE = ParagraphStyle(
    "TearsheetSubtitle",
    parent=styles["Normal"],
    fontSize=9,
    leading=11,
    textColor=colors.HexColor("#D9E2F0"),
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=10,
    leading=12,
    textColor=NAVY,
    fontName="Helvetica-Bold",
    spaceAfter=4,
)

BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontSize=7.5,
    leading=9.5,
    textColor=DARK,
)

BULLET_STYLE = ParagraphStyle(
    "Bullet",
    parent=BODY_STYLE,
    leftIndent=8,
    firstLineIndent=-5,
    spaceAfter=2,
)

SMALL_STYLE = ParagraphStyle(
    "Small",
    parent=BODY_STYLE,
    fontSize=6.5,
    leading=8,
    textColor=GREY,
)

KPI_LABEL_STYLE = ParagraphStyle(
    "KpiLabel",
    parent=BODY_STYLE,
    fontSize=6.5,
    leading=7.5,
    alignment=TA_CENTER,
    textColor=GREY,
)

KPI_VALUE_STYLE = ParagraphStyle(
    "KpiValue",
    parent=BODY_STYLE,
    fontSize=11,
    leading=13,
    alignment=TA_CENTER,
    textColor=NAVY,
    fontName="Helvetica-Bold",
)

BADGE_STYLE = ParagraphStyle(
    "Badge",
    parent=BODY_STYLE,
    fontSize=9,
    leading=11,
    alignment=TA_CENTER,
    textColor=WHITE,
    fontName="Helvetica-Bold",
)


# ============================================================
# DATABASE
# ============================================================

def load_data():
    """Load all required tables from SQLite."""

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        "SELECT * FROM companies",
        conn
    )

    profit_loss = pd.read_sql(
        "SELECT * FROM profitandloss",
        conn
    )

    balance_sheet = pd.read_sql(
        "SELECT * FROM balancesheet",
        conn
    )

    cashflow = pd.read_sql(
        "SELECT * FROM cashflow",
        conn
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
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

    pros_cons = pd.read_sql(
        "SELECT * FROM prosandcons",
        conn
    )

    conn.close()

    return {
        "companies": companies,
        "profit_loss": profit_loss,
        "balance_sheet": balance_sheet,
        "cashflow": cashflow,
        "ratios": ratios,
        "market_cap": market_cap,
        "sectors": sectors,
        "pros_cons": pros_cons,
    }


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def load_capital_allocation():

    if not CAPITAL_FILE.exists():
        return pd.DataFrame()

    try:
        df = pd.read_excel(
            CAPITAL_FILE,
            sheet_name=0
        )
    except Exception:
        return pd.DataFrame()

    return df


def get_capital_allocation(company_id, capital_df):

    if capital_df.empty:
        return "Not Available"

    if "company_id" not in capital_df.columns:
        return "Not Available"

    rows = capital_df[
        capital_df["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ]

    if rows.empty:
        return "Not Available"

    if "capital_allocation_label" in rows.columns:
        value = rows.iloc[-1]["capital_allocation_label"]
    elif "pattern_label" in rows.columns:
        value = rows.iloc[-1]["pattern_label"]
    else:
        return "Not Available"

    if pd.isna(value):
        return "Not Available"

    return str(value)


# ============================================================
# HELPERS
# ============================================================

def clean_number(value):

    if pd.isna(value):
        return None

    try:
        return float(value)
    except Exception:
        return None


def format_number(value):

    value = clean_number(value)

    if value is None:
        return "N/A"

    return f"{value:,.2f}"


def format_percent(value):

    value = clean_number(value)

    if value is None:
        return "N/A"

    return f"{value:.2f}%"


def format_crore(value):

    value = clean_number(value)

    if value is None:
        return "N/A"

    return f"₹{value:,.0f} Cr"


def normalize_year(value):

    value = str(value).strip()

    if value.startswith("Mar-"):

        short_year = value.replace("Mar-", "")

        if len(short_year) == 2:

            year_num = int(short_year)

            if year_num >= 50:
                year_num += 1900
            else:
                year_num += 2000

            return f"Mar {year_num}"

    return value


# ============================================================
# HEADER
# ============================================================

def header_bar(company_name, ticker):

    drawing = Drawing(
        PAGE_WIDTH - 2 * MARGIN,
        23 * mm
    )

    drawing.add(
        Rect(
            0,
            0,
            PAGE_WIDTH - 2 * MARGIN,
            23 * mm,
            fillColor=NAVY,
            strokeColor=NAVY,
        )
    )

    drawing.add(
        String(
            7 * mm,
            12 * mm,
            company_name,
            fontName="Helvetica-Bold",
            fontSize=17,
            fillColor=WHITE,
        )
    )

    drawing.add(
        String(
            7 * mm,
            5 * mm,
            f"Ticker: {ticker}",
            fontName="Helvetica",
            fontSize=8,
            fillColor=colors.HexColor("#D9E2F0"),
        )
    )

    return drawing


# ============================================================
# KPI TILES
# ============================================================

def kpi_tiles(kpis):

    cells = []

    for label, value in kpis:

        cell = Table(
            [
                [
                    Paragraph(
                        label,
                        KPI_LABEL_STYLE
                    )
                ],
                [
                    Paragraph(
                        value,
                        KPI_VALUE_STYLE
                    )
                ],
            ],
            colWidths=[
                (PAGE_WIDTH - 2 * MARGIN - 8 * mm) / 3
            ],
            rowHeights=[
                8 * mm,
                12 * mm
            ],
        )

        cell.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT_GREY
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#D1D5DB")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        3
                    ),
                ]
            )
        )

        cells.append(cell)

    rows = [
        cells[0:3],
        cells[3:6],
    ]

    table = Table(
        rows,
        colWidths=[
            (PAGE_WIDTH - 2 * MARGIN - 8 * mm) / 3
        ] * 3,
        hAlign="CENTER",
        rowHeights=[20 * mm, 20 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
            ]
        )
    )

    return table


# ============================================================
# BAR CHART
# ============================================================

def bar_chart(years, values, title):

    drawing = Drawing(
        82 * mm,
        63 * mm
    )

    drawing.add(
        String(
            41 * mm,
            59 * mm,
            title,
            textAnchor="middle",
            fontName="Helvetica-Bold",
            fontSize=8,
            fillColor=NAVY,
        )
    )

    chart = VerticalBarChart()

    chart.x = 8 * mm
    chart.y = 8 * mm
    chart.width = 68 * mm
    chart.height = 45 * mm

    chart.data = [values]

    chart.categoryAxis.categoryNames = [
        str(y) for y in years
    ]

    chart.categoryAxis.labels.fontSize = 5
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.dy = -4

    chart.valueAxis.labels.fontSize = 5
    chart.valueAxis.valueMin = 0

    chart.bars[0].fillColor = NAVY
    chart.bars[0].strokeColor = NAVY

    chart.valueAxis.gridStrokeColor = colors.HexColor(
        "#E5E7EB"
    )

    drawing.add(chart)

    return drawing


# ============================================================
# ROE / ROCE LINE CHART
# ============================================================

def roe_roce_chart(years, roe, roce):

    drawing = Drawing(
        PAGE_WIDTH - 2 * MARGIN,
        72 * mm
    )

    drawing.add(
        String(
            (PAGE_WIDTH - 2 * MARGIN) / 2,
            68 * mm,
            "ROE vs ROCE",
            textAnchor="middle",
            fontName="Helvetica-Bold",
            fontSize=9,
            fillColor=NAVY,
        )
    )

    chart = HorizontalLineChart()

    chart.x = 15 * mm
    chart.y = 10 * mm
    chart.width = PAGE_WIDTH - 2 * MARGIN - 30 * mm
    chart.height = 50 * mm

    chart.data = [
        roe,
        roce,
    ]

    chart.categoryAxis.categoryNames = [
        str(y) for y in years
    ]

    chart.categoryAxis.labels.fontSize = 5
    chart.categoryAxis.labels.angle = 45

    chart.valueAxis.labels.fontSize = 6

    chart.lines[0].strokeColor = NAVY
    chart.lines[1].strokeColor = GREEN

    chart.lines[0].strokeWidth = 1.5
    chart.lines[1].strokeWidth = 1.5

    chart.valueAxis.gridStrokeColor = colors.HexColor(
        "#E5E7EB"
    )

    drawing.add(chart)

    # Legend
    drawing.add(
        String(
            45 * mm,
            2 * mm,
            "ROE",
            fontName="Helvetica-Bold",
            fontSize=6,
            fillColor=NAVY,
        )
    )

    drawing.add(
        String(
            65 * mm,
            2 * mm,
            "ROCE",
            fontName="Helvetica-Bold",
            fontSize=6,
            fillColor=GREEN,
        )
    )

    return drawing


# ============================================================
# BALANCE SHEET STACKED BAR
# ============================================================

def balance_sheet_chart(balance):

    years = balance["year"].tolist()

    equity = (
        balance["equity_capital"].fillna(0)
        + balance["reserves"].fillna(0)
    ).tolist()

    borrowings = (
        balance["borrowings"]
        .fillna(0)
        .tolist()
    )

    other_liabilities = (
        balance["other_liabilities"]
        .fillna(0)
        .tolist()
    )

    drawing = Drawing(
        PAGE_WIDTH - 2 * MARGIN,
        70 * mm
    )

    drawing.add(
        String(
            (PAGE_WIDTH - 2 * MARGIN) / 2,
            66 * mm,
            "Balance Sheet Composition",
            textAnchor="middle",
            fontName="Helvetica-Bold",
            fontSize=9,
            fillColor=NAVY,
        )
    )

    chart = VerticalBarChart()

    chart.x = 15 * mm
    chart.y = 10 * mm
    chart.width = PAGE_WIDTH - 2 * MARGIN - 30 * mm
    chart.height = 48 * mm

    chart.data = [
        equity,
        borrowings,
        other_liabilities,
    ]

    chart.categoryAxis.categoryNames = [
        str(y) for y in years
    ]

    chart.categoryAxis.labels.fontSize = 5
    chart.categoryAxis.labels.angle = 45

    chart.valueAxis.labels.fontSize = 5

    chart.valueAxis.gridStrokeColor = colors.HexColor(
        "#E5E7EB"
    )

    chart.bars[0].fillColor = NAVY
    chart.bars[1].fillColor = colors.HexColor("#4B83C4")
    chart.bars[2].fillColor = colors.HexColor("#A7B5C7")

    chart.categoryAxis.labels.dy = -4

    # Stack the bars
    chart.barSpacing = 2
    chart.groupSpacing = 5

    drawing.add(chart)

    drawing.add(
        String(
            35 * mm,
            2 * mm,
            "Equity",
            fontSize=6,
            fillColor=NAVY,
        )
    )

    drawing.add(
        String(
            65 * mm,
            2 * mm,
            "Borrowings",
            fontSize=6,
            fillColor=colors.HexColor("#4B83C4"),
        )
    )

    drawing.add(
        String(
            100 * mm,
            2 * mm,
            "Other Liabilities",
            fontSize=6,
            fillColor=colors.HexColor("#6B7280"),
        )
    )

    return drawing


# ============================================================
# CASH FLOW WATERFALL
# ============================================================

def cashflow_waterfall(latest_cf):

    cfo = clean_number(
        latest_cf["operating_activity"]
    ) or 0

    cfi = clean_number(
        latest_cf["investing_activity"]
    ) or 0

    cff = clean_number(
        latest_cf["financing_activity"]
    ) or 0

    net = clean_number(
        latest_cf["net_cash_flow"]
    )

    if net is None:
        net = cfo + cfi + cff

    values = [
        cfo,
        cfi,
        cff,
        net,
    ]

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net Cash Flow",
    ]

    drawing = Drawing(
        PAGE_WIDTH - 2 * MARGIN,
        65 * mm
    )

    drawing.add(
        String(
            (PAGE_WIDTH - 2 * MARGIN) / 2,
            61 * mm,
            "Cash Flow Waterfall - Latest Year",
            textAnchor="middle",
            fontName="Helvetica-Bold",
            fontSize=9,
            fillColor=NAVY,
        )
    )

    chart_left = 20 * mm
    chart_bottom = 13 * mm
    chart_width = PAGE_WIDTH - 2 * MARGIN - 40 * mm
    chart_height = 40 * mm

    max_value = max(
        abs(v) for v in values
    )

    if max_value == 0:
        max_value = 1

    scale = chart_height / (2 * max_value)

    zero_y = chart_bottom + chart_height / 2

    # Zero line
    drawing.add(
        Line(
            chart_left,
            zero_y,
            chart_left + chart_width,
            zero_y,
            strokeColor=GREY,
            strokeWidth=0.6,
        )
    )

    bar_width = chart_width / 6

    x_positions = [
        chart_left + bar_width * 0.8,
        chart_left + bar_width * 2.1,
        chart_left + bar_width * 3.4,
        chart_left + bar_width * 4.7,
    ]

    for x, value, label in zip(
        x_positions,
        values,
        labels
    ):

        height = abs(value) * scale

        if value >= 0:
            y = zero_y
            fill = GREEN
        else:
            y = zero_y - height
            fill = RED

        drawing.add(
            Rect(
                x,
                y,
                bar_width * 0.65,
                height,
                fillColor=fill,
                strokeColor=fill,
            )
        )

        drawing.add(
            String(
                x + bar_width * 0.325,
                y + height + 2,
                format_number(value),
                textAnchor="middle",
                fontSize=5.5,
                fillColor=DARK,
            )
        )

        drawing.add(
            String(
                x + bar_width * 0.325,
                chart_bottom,
                label,
                textAnchor="middle",
                fontSize=6,
                fillColor=NAVY,
            )
        )

    return drawing


# ============================================================
# PROS / CONS
# ============================================================

def parse_bullets(value):

    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    # Handle common separators
    if "|" in text:
        parts = text.split("|")
    elif ";" in text:
        parts = text.split(";")
    else:
        parts = [
            line.strip("-• ")
            for line in text.splitlines()
            if line.strip()
        ]

    return [
        p.strip()
        for p in parts
        if p.strip()
    ]


def bullet_table(items, style, bullet_color):

    if not items:
        items = ["No data available"]

    rows = []

    for item in items[:6]:

        paragraph = Paragraph(
            f"<font color='{bullet_color}'>•</font> "
            f"{item}",
            style
        )

        rows.append([paragraph])

    table = Table(
        rows,
        colWidths=[
            (PAGE_WIDTH - 2 * MARGIN - 8 * mm) / 2
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    2
                ),
            ]
        )
    )

    return table


# ============================================================
# CAPITAL ALLOCATION BADGE
# ============================================================

def capital_badge(label):

    badge = Table(
        [
            [
                Paragraph(
                    label,
                    BADGE_STYLE
                )
            ]
        ],
        colWidths=[55 * mm],
        rowHeights=[12 * mm],
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    NAVY
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
            ]
        )
    )

    return badge


# ============================================================
# GET COMPANY DATA
# ============================================================

def get_company_data(company_id, data):

    companies = data["companies"]

    company = companies[
        companies["id"].astype(str).str.strip()
        == str(company_id).strip()
    ]

    if company.empty:
        raise ValueError(
            f"Company not found: {company_id}"
        )

    company = company.iloc[0]

    pl = data["profit_loss"]

    pl = pl[
        pl["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ].copy()

    pl["year"] = pl["year"].astype(str)

    pl = pl.sort_values("year")

    bs = data["balance_sheet"]

    bs = bs[
        bs["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ].copy()

    bs["year"] = bs["year"].astype(str)

    bs = bs.sort_values("year")

    cf = data["cashflow"]

    cf = cf[
        cf["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ].copy()

    cf["year"] = cf["year"].apply(
        normalize_year
    )

    cf = cf.sort_values("year")

    ratios = data["ratios"]

    ratios = ratios[
        ratios["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ].copy()

    ratios["year"] = ratios["year"].apply(
        normalize_year
    )

    ratios = ratios.sort_values("year")

    market = data["market_cap"]

    market = market[
        market["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ].copy()

    market = market.sort_values("year")

    sector = data["sectors"]

    sector = sector[
        sector["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ]

    pros_cons = data["pros_cons"]

    pros_cons = pros_cons[
        pros_cons["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ]

    return {
        "company": company,
        "profit_loss": pl,
        "balance_sheet": bs,
        "cashflow": cf,
        "ratios": ratios,
        "market": market,
        "sector": sector,
        "pros_cons": pros_cons,
    }


# ============================================================
# BUILD TEARSHEET
# ============================================================

def build_tearsheet(
    company_id,
    data,
    capital_df,
    output_path,
):

    d = get_company_data(
        company_id,
        data
    )

    company = d["company"]
    pl = d["profit_loss"]
    bs = d["balance_sheet"]
    cf = d["cashflow"]
    ratios = d["ratios"]
    market = d["market"]
    sector = d["sector"]
    pros_cons = d["pros_cons"]

    company_name = str(
        company["company_name"]
    )

    ticker = str(company_id)

    sector_name = "Unknown"

    if not sector.empty:
        sector_name = str(
            sector.iloc[0]["broad_sector"]
        )

    # --------------------------------------------------------
    # Latest records
    # --------------------------------------------------------

    latest_pl = (
        pl.iloc[-1]
        if not pl.empty
        else pd.Series()
    )

    latest_ratios = (
        ratios.iloc[-1]
        if not ratios.empty
        else pd.Series()
    )

    latest_market = (
        market.iloc[-1]
        if not market.empty
        else pd.Series()
    )

    latest_cf = (
        cf.iloc[-1]
        if not cf.empty
        else pd.Series()
    )

    # --------------------------------------------------------
    # KPI VALUES
    # --------------------------------------------------------

    revenue = (
        latest_pl.get("sales")
        if not latest_pl.empty
        else None
    )

    net_profit = (
        latest_pl.get("net_profit")
        if not latest_pl.empty
        else None
    )

    roe = (
        latest_ratios.get(
            "return_on_equity_pct"
        )
        if not latest_ratios.empty
        else company.get("roe_percentage")
    )

    roce = company.get("roce_percentage")

    debt_equity = (
        latest_ratios.get("debt_to_equity")
        if not latest_ratios.empty
        else None
    )

    market_cap = (
        latest_market.get(
            "market_cap_crore"
        )
        if not latest_market.empty
        else None
    )

    kpis = [
        ("Revenue", format_crore(revenue)),
        ("Net Profit", format_crore(net_profit)),
        ("ROE", format_percent(roe)),
        ("ROCE", format_percent(roce)),
        ("Debt / Equity", format_number(debt_equity)),
        ("Market Cap", format_crore(market_cap)),
    ]

    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
        title=f"{company_name} ({ticker}) Tearsheet",
        author="Sprint 1 Data Foundation",
    )

    story = []

    # ========================================================
    # PAGE 1
    # ========================================================

    story.append(
        header_bar(
            company_name,
            ticker
        )
    )

    story.append(Spacer(1, 4 * mm))

    story.append(
        Paragraph(
            f"Sector: {sector_name}",
            SMALL_STYLE
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.append(
        kpi_tiles(kpis)
    )

    story.append(Spacer(1, 3 * mm))

    # --------------------------------------------------------
    # 10-year revenue and profit
    # --------------------------------------------------------

    chart_pl = pl.tail(10).copy()

    chart_pl["year"] = (
        chart_pl["year"]
        .astype(str)
    )

    years = chart_pl["year"].tolist()

    revenue_values = (
        chart_pl["sales"]
        .fillna(0)
        .astype(float)
        .tolist()
    )

    profit_values = (
        chart_pl["net_profit"]
        .fillna(0)
        .astype(float)
        .tolist()
    )

    revenue_chart = bar_chart(
        years,
        revenue_values,
        "10-Year Revenue"
    )

    profit_chart = bar_chart(
        years,
        profit_values,
        "10-Year Net Profit"
    )

    chart_table = Table(
        [
            [
                revenue_chart,
                profit_chart
            ]
        ],
        colWidths=[
            (PAGE_WIDTH - 2 * MARGIN) / 2,
            (PAGE_WIDTH - 2 * MARGIN) / 2,
        ],
    )

    chart_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER"
                ),
            ]
        )
    )

    story.append(chart_table)

    # --------------------------------------------------------
    # ROE / ROCE
    # --------------------------------------------------------

    ratio_chart = ratios.tail(10).copy()

    if not ratio_chart.empty:

        ratio_years = ratio_chart[
            "year"
        ].astype(str).tolist()

        roe_values = (
            ratio_chart[
                "return_on_equity_pct"
            ]
            .fillna(0)
            .astype(float)
            .tolist()
        )

        # ROCE isn't in financial_ratios,
        # so use company ROCE as a fallback line.
        roce_value = clean_number(
            company.get("roce_percentage")
        )

        if roce_value is None:
            roce_value = 0

        roce_values = [
            roce_value
            for _ in ratio_years
        ]

        story.append(
            roe_roce_chart(
                ratio_years,
                roe_values,
                roce_values
            )
        )

    story.append(PageBreak())

    # ========================================================
    # PAGE 2
    # ========================================================

    story.append(
        Paragraph(
            "Balance Sheet & Cash Flow Intelligence",
            SECTION_STYLE
        )
    )

    # --------------------------------------------------------
    # Balance sheet
    # --------------------------------------------------------

    bs_chart = bs.tail(10).copy()

    if not bs_chart.empty:

        bs_chart["year"] = (
            bs_chart["year"]
            .astype(str)
        )

        story.append(
            balance_sheet_chart(
                bs_chart
            )
        )

    story.append(Spacer(1, 2 * mm))

    # --------------------------------------------------------
    # Cash flow waterfall
    # --------------------------------------------------------

    if not latest_cf.empty:

        story.append(
            cashflow_waterfall(
                latest_cf
            )
        )

    story.append(Spacer(1, 2 * mm))

    # --------------------------------------------------------
    # Pros / Cons
    # --------------------------------------------------------

    pros = []
    cons = []

    if not pros_cons.empty:

        pros = parse_bullets(
            pros_cons.iloc[-1].get("pros")
        )

        cons = parse_bullets(
            pros_cons.iloc[-1].get("cons")
        )

    pros_flow = [
        Paragraph(
            "Pros",
            ParagraphStyle(
                "ProsHeading",
                parent=SECTION_STYLE,
                textColor=GREEN
            )
        ),
        bullet_table(
            pros,
            BULLET_STYLE,
            "#198754"
        )
    ]

    cons_flow = [
        Paragraph(
            "Cons",
            ParagraphStyle(
                "ConsHeading",
                parent=SECTION_STYLE,
                textColor=RED
            )
        ),
        bullet_table(
            cons,
            BULLET_STYLE,
            "#C62828"
        )
    ]

    pros_table = Table(
        [
            [
                pros_flow,
                cons_flow
            ]
        ],
        colWidths=[
            (PAGE_WIDTH - 2 * MARGIN) / 2,
            (PAGE_WIDTH - 2 * MARGIN) / 2,
        ],
    )

    pros_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4
                ),
            ]
        )
    )

    story.append(pros_table)

    story.append(Spacer(1, 4 * mm))

    # --------------------------------------------------------
    # Capital allocation
    # --------------------------------------------------------

    allocation = get_capital_allocation(
        company_id,
        capital_df
    )

    story.append(
        Paragraph(
            "Capital Allocation",
            SECTION_STYLE
        )
    )

    story.append(
        capital_badge(
            allocation
        )
    )

    story.append(Spacer(1, 2 * mm))

    story.append(
        Paragraph(
            "Source: Nifty 100 financial dataset | "
            "Generated by Sprint 1 Data Foundation",
            SMALL_STYLE
        )
    )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    doc.build(story)

    return output_path


# ============================================================
# GENERATE ONE COMPANY
# ============================================================

def generate_company_tearsheet(
    company_id,
    data=None,
    capital_df=None,
):

    if data is None:
        data = load_data()

    if capital_df is None:
        capital_df = load_capital_allocation()

    output_path = (
        OUTPUT_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    build_tearsheet(
        company_id,
        data,
        capital_df,
        output_path
    )

    print(
        f"Created: {output_path}"
    )

    return output_path


# ============================================================
# TEST 5 COMPANIES
# ============================================================

def test_five_companies():

    test_companies = [
        "TCS",
        "HDFCBANK",
        "RELIANCE",
        "SUNPHARMA",
        "TATASTEEL",
    ]

    data = load_data()

    capital_df = load_capital_allocation()

    print("\n" + "=" * 60)
    print("DAY 33 - TEARSHEET TEST")
    print("=" * 60)

    for company_id in test_companies:

        try:

            generate_company_tearsheet(
                company_id,
                data,
                capital_df
            )

        except Exception as exc:

            print(
                f"ERROR - {company_id}: {exc}"
            )

    print("\nTest completed.")
    print(
        f"Output folder: {OUTPUT_DIR}"
    )



# ============================================================
# DAY 34 - BATCH TEARSHEET GENERATION
# ============================================================

MIN_YEARS = 3

def _company_year_count(company_id, data):
    """Count distinct profit/loss years available for a company."""
    pl = data["profit_loss"]
    rows = pl[
        pl["company_id"].astype(str).str.strip()
        == str(company_id).strip()
    ]
    if rows.empty:
        return 0
    return rows["year"].astype(str).str.strip().nunique()


def _safe_filename(value):
    value = str(value).strip()
    return re.sub(r'[<>:"/\\|?*]', "_", value)[:100] or "UNKNOWN"


def _wrapped_table(rows, widths, header_size=5.2, body_size=5.2):
    """Create a word-wrapped table for Day 34 sector reports."""
    header_style = ParagraphStyle(
        "WrapHeader", parent=SMALL_STYLE, fontSize=header_size,
        leading=header_size + 1, textColor=WHITE,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "WrapBody", parent=BODY_STYLE, fontSize=body_size,
        leading=body_size + 1.2,
    )
    wrapped = []
    for i, row in enumerate(rows):
        style = header_style if i == 0 else body_style
        wrapped.append([
            Paragraph("" if pd.isna(v) else str(v), style)
            for v in row
        ])
    table = LongTable(
        wrapped, colWidths=widths, repeatRows=1,
        splitByRow=1, hAlign="LEFT"
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.35,
         colors.HexColor("#D1D5DB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [WHITE, LIGHT_GREY]),
    ]))
    return table


def generate_batch_tearsheets():
    """Generate all eligible company tearsheets."""
    data = load_data()
    capital_df = load_capital_allocation()

    generated, skipped, errors = [], [], []

    print("\n" + "=" * 70)
    print("DAY 34 - BATCH TEARSHEET GENERATION")
    print("=" * 70)

    for company_id in data["companies"]["id"].astype(str).str.strip():
        years = _company_year_count(company_id, data)

        if years < MIN_YEARS:
            skipped.append({
                "company_id": company_id,
                "years_available": years,
                "reason": f"Fewer than {MIN_YEARS} years of data",
            })
            print(f"SKIPPED {company_id}: {years} years")
            continue

        try:
            generate_company_tearsheet(
                company_id, data, capital_df
            )
            pdf = OUTPUT_DIR / f"{_safe_filename(company_id)}_tearsheet.pdf"
            if pdf.exists():
                generated.append(company_id)
            else:
                errors.append({
                    "company_id": company_id,
                    "error": "PDF was not created",
                })
        except Exception as exc:
            errors.append({
                "company_id": company_id,
                "error": str(exc),
            })
            print(f"ERROR {company_id}: {exc}")

    skipped_path = PROJECT_ROOT / "output" / "skipped_tearsheets.csv"
    skipped_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        skipped,
        columns=["company_id", "years_available", "reason"]
    ).to_csv(skipped_path, index=False)

    if errors:
        pd.DataFrame(errors).to_csv(
            PROJECT_ROOT / "output" / "tearsheet_errors.csv",
            index=False
        )

    print("\nBatch generated:", len(generated))
    print("Skipped:", len(skipped))
    print("Errors:", len(errors))
    print("Saved skipped log:", skipped_path)
    return generated, skipped, errors


# ============================================================
# DAY 34 - SECTOR REPORTS
# ============================================================

SECTOR_METRICS = [
    ("Revenue", "revenue"),
    ("Net Profit", "net_profit"),
    ("ROE", "roe"),
    ("ROCE", "roce"),
    ("Debt / Equity", "debt_equity"),
    ("Market Cap", "market_cap"),
    ("CFO", "cfo"),
    ("Free Cash Flow", "fcf"),
]


def _latest_metrics(company_id, data):
    d = get_company_data(company_id, data)
    company, pl, ratios = d["company"], d["profit_loss"], d["ratios"]
    market, cf = d["market"], d["cashflow"]

    p = pl.iloc[-1] if not pl.empty else pd.Series()
    r = ratios.iloc[-1] if not ratios.empty else pd.Series()
    m = market.iloc[-1] if not market.empty else pd.Series()
    c = cf.iloc[-1] if not cf.empty else pd.Series()

    return {
        "revenue": clean_number(p.get("sales")) if not p.empty else None,
        "net_profit": clean_number(p.get("net_profit")) if not p.empty else None,
        "roe": clean_number(
            r.get("return_on_equity_pct")
            if not r.empty else company.get("roe_percentage")
        ),
        "roce": clean_number(company.get("roce_percentage")),
        "debt_equity": clean_number(
            r.get("debt_to_equity") if not r.empty else None
        ),
        "market_cap": clean_number(
            m.get("market_cap_crore") if not m.empty else None
        ),
        "cfo": clean_number(
            c.get("operating_activity") if not c.empty else None
        ),
        "fcf": clean_number(
            r.get("free_cash_flow_cr") if not r.empty else None
        ),
    }


def _metric_display(key, value):
    if value is None or pd.isna(value):
        return "N/A"
    if key in {"roe", "roce"}:
        return format_percent(value)
    if key == "debt_equity":
        return format_number(value)
    return format_crore(value)


def build_sector_report(sector_name, company_ids, data, output_path):
    rows = []

    for company_id in company_ids:
        try:
            metrics = _latest_metrics(company_id, data)
            match = data["companies"][
                data["companies"]["id"].astype(str).str.strip()
                == str(company_id).strip()
            ]
            name = str(company_id)
            if not match.empty:
                name = str(match.iloc[0]["company_name"])
            rows.append({
                "ticker": str(company_id),
                "company": name,
                **metrics,
            })
        except Exception as exc:
            print(f"ERROR {sector_name}/{company_id}: {exc}")

    doc = SimpleDocTemplate(
        str(output_path), pagesize=A4,
        rightMargin=MARGIN, leftMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title=f"{sector_name} Sector Report",
        author="Sprint 1 Data Foundation",
    )
    story = [
        header_bar(
            f"{sector_name} Sector",
            f"{len(rows)} Companies"
        ),
        Spacer(1, 5 * mm),
        Paragraph("Sector Summary - Median Latest-Year KPIs", SECTION_STYLE),
    ]

    summary = [["Metric", "Median"]]
    for label, key in SECTOR_METRICS:
        vals = [
            r[key] for r in rows
            if r[key] is not None and not pd.isna(r[key])
        ]
        median = float(pd.Series(vals).median()) if vals else None
        summary.append([label, _metric_display(key, median)])

    story.append(_wrapped_table(summary, [75 * mm, 75 * mm], 7, 7))
    story += [
        Spacer(1, 6 * mm),
        Paragraph("All Companies - 8 Metrics", SECTION_STYLE),
    ]

    table = [[
        "Ticker", "Company", "Revenue", "Net Profit", "ROE",
        "ROCE", "Debt / Equity", "Market Cap", "CFO", "FCF"
    ]]
    for r in rows:
        table.append([
            r["ticker"], r["company"],
            _metric_display("revenue", r["revenue"]),
            _metric_display("net_profit", r["net_profit"]),
            _metric_display("roe", r["roe"]),
            _metric_display("roce", r["roce"]),
            _metric_display("debt_equity", r["debt_equity"]),
            _metric_display("market_cap", r["market_cap"]),
            _metric_display("cfo", r["cfo"]),
            _metric_display("fcf", r["fcf"]),
        ])

    widths = [
        15 * mm, 37 * mm, 18 * mm, 20 * mm, 14 * mm,
        14 * mm, 18 * mm, 20 * mm, 18 * mm, 18 * mm
    ]
    story.append(_wrapped_table(table, widths))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "Source: Nifty 100 financial dataset | "
        "Generated by Sprint 1 Data Foundation",
        SMALL_STYLE
    ))
    doc.build(story)
    return output_path


def generate_sector_reports():
    data = load_data()
    sectors = data["sectors"].copy()
    sectors["broad_sector"] = (
        sectors["broad_sector"].fillna("Unknown").astype(str).str.strip()
    )

    groups = (
        sectors.groupby("broad_sector")["company_id"]
        .apply(lambda s: sorted(s.astype(str).str.strip().unique()))
        .to_dict()
    )

    generated = []
    print("\n" + "=" * 70)
    print("DAY 34 - SECTOR REPORT GENERATION")
    print("=" * 70)
    print("Sectors found:", len(groups))

    for sector_name, company_ids in sorted(groups.items()):
        path = SECTOR_OUTPUT_DIR / f"{_safe_filename(sector_name)}_report.pdf"
        try:
            build_sector_report(
                sector_name, company_ids, data, path
            )
            generated.append(path)
            print(f"OK {sector_name}: {len(company_ids)} companies")
        except Exception as exc:
            print(f"ERROR {sector_name}: {exc}")

    print("Sector PDFs generated:", len(generated))
    return generated


def validate_company_pdfs():
    """Check page count and text presence; visual overflow still needs spot-check."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf not installed; PDF validation skipped.")
        return

    pdfs = sorted(OUTPUT_DIR.glob("*_tearsheet.pdf"))
    valid = 0
    invalid = []

    for pdf in pdfs:
        try:
            reader = PdfReader(str(pdf))
            pages = len(reader.pages)
            text_lengths = [
                len(page.extract_text() or "")
                for page in reader.pages
            ]
            if pages == 2 and all(x > 20 for x in text_lengths):
                valid += 1
            else:
                invalid.append((pdf.name, pages, text_lengths))
        except Exception as exc:
            invalid.append((pdf.name, "ERROR", str(exc)))

    print("\n" + "=" * 70)
    print("COMPANY PDF VALIDATION")
    print("=" * 70)
    print("PDFs found:", len(pdfs))
    print("Valid 2-page PDFs:", valid)
    print("Invalid PDFs:", len(invalid))
    for item in invalid:
        print("  ", item)


def print_day34_summary():
    company_pdfs = list(OUTPUT_DIR.glob("*_tearsheet.pdf"))
    sector_pdfs = list(SECTOR_OUTPUT_DIR.glob("*_report.pdf"))
    skipped_path = PROJECT_ROOT / "output" / "skipped_tearsheets.csv"
    skipped = (
        len(pd.read_csv(skipped_path))
        if skipped_path.exists() else 0
    )

    print("\n" + "=" * 70)
    print("DAY 34 FINAL STATUS")
    print("=" * 70)
    print("Company tearsheets:", len(company_pdfs))
    print("Skipped companies:", skipped)
    print("Expected company PDFs:", 92 - skipped)
    print("Sector reports:", len(sector_pdfs))
    print("Company folder:", OUTPUT_DIR)
    print("Sector folder:", SECTOR_OUTPUT_DIR)
    print("Skipped log:", skipped_path)

    print(
        "Company count:",
        "PASS" if len(company_pdfs) == 92 - skipped else "CHECK"
    )
    print(
        "Sector count:",
        "PASS" if len(sector_pdfs) == 11 else "CHECK"
    )


# ============================================================
# MAIN - DAY 34
# ============================================================

if __name__ == "__main__":
    generate_batch_tearsheets()
    generate_sector_reports()
    validate_company_pdfs()
    print_day34_summary()
