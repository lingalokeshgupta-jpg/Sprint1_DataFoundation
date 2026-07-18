import pandas as pd
import pytest

from src.etl.normalizer import (
    normalize_year,
    normalize_ticker,
    normalize_text
)

# ----------------------------------------------------
# normalize_year()
# ----------------------------------------------------

def test_normalize_year_integer():
    assert normalize_year(2024) == 2024


def test_normalize_year_string():
    assert normalize_year("2024") == 2024


def test_normalize_year_float():
    assert normalize_year(2024.0) == 2024


def test_normalize_year_none():
    assert normalize_year(None) is None


def test_normalize_year_nan():
    assert normalize_year(float("nan")) is None


def test_normalize_year_invalid():
    assert normalize_year("abcd") is None


# ----------------------------------------------------
# normalize_ticker()
# ----------------------------------------------------

def test_normalize_ticker_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_spaces():
    assert normalize_ticker("  infy  ") == "INFY"


def test_normalize_ticker_already_upper():
    assert normalize_ticker("RELIANCE") == "RELIANCE"


def test_normalize_ticker_none():
    assert normalize_ticker(None) is None


def test_normalize_ticker_nan():
    assert normalize_ticker(pd.NA) is None


# ----------------------------------------------------
# normalize_text()
# ----------------------------------------------------

def test_normalize_text_strip():
    assert normalize_text("  hello world  ") == "hello world"


def test_normalize_text_none():
    assert normalize_text(None) is None


def test_normalize_text_nan():
    assert normalize_text(float("nan")) is None


def test_normalize_text_number():
    assert normalize_text(123) == "123"


def test_normalize_text_empty():
    assert normalize_text("") == ""