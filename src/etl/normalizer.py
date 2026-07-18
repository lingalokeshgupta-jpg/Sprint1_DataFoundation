import pandas as pd
def normalize_year(value):
    """
    Convert year values into integer.
    """

    if pd.isna(value):
        return None

    try:
        return int(value)
    except Exception:
        return None
    
normalize_year("2024")

def normalize_ticker(value):
    """
    Standardize ticker/company symbol.
    """

    if pd.isna(value):
        return None

    return str(value).strip().upper()

normalize_ticker(" tcs ")

def normalize_text(value):

    if pd.isna(value):
        return None

    return str(value).strip()

