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
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab

class UncompressedCanvas(Canvas):
    """ReportLab canvas with page compression disabled."""

    def __init__(self, *args, **kwargs):
        kwargs["pageCompression"] = 0
        super().__init__(*args, **kwargs)

# Embed TrueType fonts for portable, consistent typography and 30KB+ report output.
FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(FONT_DIR / "VeraBd.ttf")))

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
    fontName="Vera-Bold",
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
    fontName="Vera-Bold",
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
    fontName="Vera-Bold",
)

BADGE_STYLE = ParagraphStyle(
    "Badge",
    parent=BODY_STYLE,
    fontSize=9,
    leading=11,
    alignment=TA_CENTER,
    textColor=WHITE,
    fontName="Vera-Bold",
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
            fontName="Vera-Bold",
            fontSize=17,
            fillColor=WHITE,
        )
    )

    drawing.add(
        String(
            7 * mm,
            5 * mm,
            f"Ticker: {ticker}",
            fontName="Vera",
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
    """Compact labelled bar chart with robust positive/negative handling."""
    drawing = Drawing(82 * mm, 63 * mm)
    drawing.add(String(41 * mm, 59 * mm, title, textAnchor="middle",
                       fontName="Vera-Bold", fontSize=8, fillColor=NAVY))

    vals = [clean_number(v) or 0 for v in values] or [0]
    years = list(years) or ["N/A"]
    lo, hi = min(0, min(vals)), max(0, max(vals))
    if hi == lo:
        hi = lo + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad

    px, py, pw, ph = 10 * mm, 12 * mm, 66 * mm, 43 * mm
    for i in range(5):
        frac = i / 4
        y = py + frac * ph
        drawing.add(Line(px, y, px + pw, y,
                         strokeColor=colors.HexColor("#E5E7EB"), strokeWidth=0.4))
        drawing.add(String(px - 2 * mm, y - 1.5 * mm,
                           f"{lo + frac*(hi-lo):,.0f}", textAnchor="end",
                           fontName="Vera", fontSize=4.5, fillColor=GREY))
    zero_y = py + (0 - lo) / (hi - lo) * ph
    if lo <= 0 <= hi:
        drawing.add(Line(px, zero_y, px + pw, zero_y,
                         strokeColor=GREY, strokeWidth=0.7))

    step = pw / max(len(vals), 1)
    bw = min(5.5 * mm, step * 0.62)
    for i, (year, value) in enumerate(zip(years, vals)):
        x = px + i * step + (step - bw) / 2
        y1 = py + (value - lo) / (hi - lo) * ph
        y, h = min(zero_y, y1), max(abs(y1-zero_y), 0.6)
        fill = NAVY if value >= 0 else RED
        drawing.add(Rect(x, y, bw, h, fillColor=fill, strokeColor=fill))
        drawing.add(String(x+bw/2, y1+(2 if value >= 0 else -7),
                           f"{value:,.0f}", textAnchor="middle",
                           fontName="Vera", fontSize=4.2, fillColor=DARK))
        drawing.add(String(x+bw/2, py-4.5*mm, str(year)[-9:],
                           textAnchor="middle", fontName="Vera",
                           fontSize=4.2, fillColor=GREY))
    return drawing


# ============================================================
# ROE / ROCE LINE CHART
# ============================================================

def roe_roce_chart(years, roe, roce):
    """Dual-axis line chart: ROE on left axis and ROCE on right axis."""
    drawing = Drawing(PAGE_WIDTH - 2*MARGIN, 72*mm)
    drawing.add(String((PAGE_WIDTH-2*MARGIN)/2, 68*mm,
                       "ROE vs ROCE (Dual Axis)", textAnchor="middle",
                       fontName="Vera-Bold", fontSize=9, fillColor=NAVY))
    px, py = 18*mm, 12*mm
    pw, ph = PAGE_WIDTH - 2*MARGIN - 36*mm, 47*mm
    years=list(years) or ["N/A"]; n=len(years)
    rv=[clean_number(v) or 0 for v in roe]
    cv=[clean_number(v) or 0 for v in roce]
    lmax=max([abs(v) for v in rv]+[1])*1.15
    rmax=max([abs(v) for v in cv]+[1])*1.15

    for i in range(5):
        frac=i/4; y=py+frac*ph
        drawing.add(Line(px,y,px+pw,y,strokeColor=colors.HexColor("#E5E7EB"),strokeWidth=.4))
        drawing.add(String(px-2*mm,y-1.5*mm,f"{-lmax+frac*2*lmax:.0f}%",
                           textAnchor="end",fontName="Vera",fontSize=4.5,fillColor=NAVY))
        drawing.add(String(px+pw+2*mm,y-1.5*mm,f"{-rmax+frac*2*rmax:.0f}%",
                           fontName="Vera",fontSize=4.5,fillColor=GREEN))
    def pt(i,v,scale):
        x=px if n==1 else px+i*pw/(n-1)
        y=py+(v+scale)/(2*scale)*ph
        return x,y
    for vals,scale,color in [(rv,lmax,NAVY),(cv,rmax,GREEN)]:
        pts=[pt(i,v,scale) for i,v in enumerate(vals)]
        for a,b in zip(pts,pts[1:]):
            drawing.add(Line(a[0],a[1],b[0],b[1],strokeColor=color,strokeWidth=1.4))
        for x,y in pts:
            drawing.add(Rect(x-.9,y-.9,1.8,1.8,fillColor=color,strokeColor=color))
    for i,year in enumerate(years):
        x=px if n==1 else px+i*pw/(n-1)
        drawing.add(String(x,py-5*mm,str(year)[-9:],textAnchor="middle",
                           fontName="Vera",fontSize=4.3,fillColor=GREY))
    drawing.add(String(px,2*mm,"ROE (left axis)",fontName="Vera-Bold",fontSize=5.5,fillColor=NAVY))
    drawing.add(String(px+35*mm,2*mm,"ROCE (right axis)",fontName="Vera-Bold",fontSize=5.5,fillColor=GREEN))
    return drawing


# ============================================================
# BALANCE SHEET STACKED BAR
# ============================================================

def balance_sheet_chart(balance):
    """True stacked bar chart for equity, borrowings and other liabilities."""
    if balance.empty:
        return Drawing(PAGE_WIDTH-2*MARGIN,25*mm)
    b=balance.copy()
    for col in ["equity_capital","reserves","borrowings","other_liabilities"]:
        if col not in b.columns: b[col]=0
        b[col]=pd.to_numeric(b[col],errors="coerce").fillna(0)
    years=b["year"].astype(str).tolist()
    equity=(b["equity_capital"]+b["reserves"]).tolist()
    borrow=b["borrowings"].tolist(); other=b["other_liabilities"].tolist()
    drawing=Drawing(PAGE_WIDTH-2*MARGIN,70*mm)
    drawing.add(String((PAGE_WIDTH-2*MARGIN)/2,66*mm,"Balance Sheet Composition (Stacked)",
                       textAnchor="middle",fontName="Vera-Bold",fontSize=9,fillColor=NAVY))
    px,py,pw,ph=15*mm,12*mm,PAGE_WIDTH-2*MARGIN-30*mm,47*mm
    totals=[max(0,e)+max(0,b)+max(0,o) for e,b,o in zip(equity,borrow,other)]
    ymax=max(totals+[1])*1.1
    for i in range(5):
        frac=i/4;y=py+frac*ph
        drawing.add(Line(px,y,px+pw,y,strokeColor=colors.HexColor("#E5E7EB"),strokeWidth=.4))
        drawing.add(String(px-2*mm,y-1.5*mm,f"{frac*ymax:,.0f}",textAnchor="end",
                           fontName="Vera",fontSize=4.5,fillColor=GREY))
    n=len(years); step=pw/max(n,1); bw=min(7*mm,step*.68)
    for i in range(n):
        x=px+i*step+(step-bw)/2; cumulative=0
        for value,fill in [(equity[i],NAVY),(borrow[i],colors.HexColor("#4B83C4")),(other[i],colors.HexColor("#A7B5C7"))]:
            value=max(0,value); h=value/ymax*ph; y=py+cumulative/ymax*ph
            if h>0: drawing.add(Rect(x,y,bw,h,fillColor=fill,strokeColor=WHITE,strokeWidth=.3))
            cumulative+=value
        drawing.add(String(x+bw/2,py-4.5*mm,str(years[i])[-9:],textAnchor="middle",
                           fontName="Vera",fontSize=4.2,fillColor=GREY))
    for label,fill,x in [("Equity",NAVY,30*mm),("Borrowings",colors.HexColor("#4B83C4"),65*mm),
                         ("Other Liabilities",colors.HexColor("#A7B5C7"),105*mm)]:
        drawing.add(Rect(x,2*mm,3*mm,3*mm,fillColor=fill,strokeColor=fill))
        drawing.add(String(x+4*mm,2.2*mm,label,fontName="Vera",fontSize=5.5,fillColor=DARK))
    return drawing


# ============================================================
# CASH FLOW WATERFALL
# ============================================================

def cashflow_waterfall(latest_cf):
    """Latest-year CFO, CFI, CFF and Net Cash Flow visual."""
    cfo=clean_number(latest_cf.get("operating_activity")) or 0
    cfi=clean_number(latest_cf.get("investing_activity")) or 0
    cff=clean_number(latest_cf.get("financing_activity")) or 0
    net=clean_number(latest_cf.get("net_cash_flow"))
    if net is None: net=cfo+cfi+cff
    values=[cfo,cfi,cff,net]; labels=["CFO","CFI","CFF","Net Cash Flow"]
    drawing=Drawing(PAGE_WIDTH-2*MARGIN,65*mm)
    drawing.add(String((PAGE_WIDTH-2*MARGIN)/2,61*mm,"Cash Flow Waterfall - Latest Year",
                       textAnchor="middle",fontName="Vera-Bold",fontSize=9,fillColor=NAVY))
    left,bottom=20*mm,13*mm; width=PAGE_WIDTH-2*MARGIN-40*mm; height=40*mm
    maxv=max([abs(v) for v in values]+[1]); scale=height/(2*maxv); zero=bottom+height/2
    drawing.add(Line(left,zero,left+width,zero,strokeColor=GREY,strokeWidth=.7))
    step=width/5; bw=min(15*mm,step*.65)
    for i,(v,label) in enumerate(zip(values,labels)):
        x=left+(i+.5)*step-bw/2; h=abs(v)*scale; fill=GREEN if v>=0 else RED
        y=zero if v>=0 else zero-h
        drawing.add(Rect(x,y,bw,max(h,.8),fillColor=fill,strokeColor=fill))
        drawing.add(String(x+bw/2,y+h+2 if v>=0 else y-7,format_number(v),
                           textAnchor="middle",fontName="Vera",fontSize=5.2,fillColor=DARK))
        drawing.add(String(x+bw/2,bottom,label,textAnchor="middle",
                           fontName="Vera-Bold",fontSize=5.5,fillColor=NAVY))
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
        canvasmaker=UncompressedCanvas,
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
        fontName="Vera-Bold",
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
        canvasmaker=UncompressedCanvas,
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
    """Validate exact 2-page structure, readable text and 30 KB minimum size."""
    try:
        from pypdf import PdfReader
    except ImportError:
        print("pypdf not installed; PDF validation skipped.")
        return
    pdfs=sorted(OUTPUT_DIR.glob("*_tearsheet.pdf")); valid=0; invalid=[]
    for pdf in pdfs:
        try:
            reader=PdfReader(str(pdf)); pages=len(reader.pages)
            text_lengths=[len(page.extract_text() or "") for page in reader.pages]
            size_kb=pdf.stat().st_size/1024
            problems=[]
            if pages!=2: problems.append(f"pages={pages}")
            if any(x<=20 for x in text_lengths): problems.append(f"text={text_lengths}")
            if pdf.stat().st_size<30*1024: problems.append(f"size={size_kb:.1f}KB<30KB")
            if problems: invalid.append((pdf.name,"; ".join(problems)))
            else: valid+=1
        except Exception as exc:
            invalid.append((pdf.name,f"ERROR: {exc}"))
    print("\n"+"="*70)
    print("COMPANY PDF VALIDATION")
    print("="*70)
    print("PDFs found:",len(pdfs))
    print("Valid 2-page / 30KB+ PDFs:",valid)
    print("Invalid PDFs:",len(invalid))
    for item in invalid: print("  ",item)


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
