import pandas as pd
import pytest

from validator  import (
    validation_errors,
    dq01_pk_uniqueness,
    dq02_fk_integrity,
    dq03_missing_values,
    dq04_duplicate_rows,
    dq05_positive_sales,
    dq06_balance_sheet,
)
# ----------------------------------------------------
# Helper
# ----------------------------------------------------

def reset_errors():
    validation_errors.clear()


# ----------------------------------------------------
# DQ-01 Primary Key
# ----------------------------------------------------

def test_dq01_duplicate_pk():
    reset_errors()

    df = pd.DataFrame({
        "id": [1, 1, 2]
    })

    dq01_pk_uniqueness(df, "id", "companies")

    assert len(validation_errors) == 1
    assert validation_errors[0]["DQ_Rule"] == "DQ-01"


def test_dq01_unique_pk():
    reset_errors()

    df = pd.DataFrame({
        "id": [1, 2, 3]
    })

    dq01_pk_uniqueness(df, "id", "companies")

    assert len(validation_errors) == 0


# ----------------------------------------------------
# DQ-02 Foreign Key
# ----------------------------------------------------

def test_dq02_valid_fk():
    reset_errors()

    parent = pd.DataFrame({
        "id": [1, 2, 3]
    })

    child = pd.DataFrame({
        "company_id": [1, 2]
    })

    dq02_fk_integrity(child, parent, "company_id", "id", "profitandloss")

    assert len(validation_errors) == 0


def test_dq02_invalid_fk():
    reset_errors()

    parent = pd.DataFrame({
        "id": [1]
    })

    child = pd.DataFrame({
        "company_id": [1, 5]
    })

    dq02_fk_integrity(child, parent, "company_id", "id", "profitandloss")

    assert len(validation_errors) == 1
    assert validation_errors[0]["DQ_Rule"] == "DQ-02"


# ----------------------------------------------------
# DQ-03 Missing Values
# ----------------------------------------------------

def test_dq03_missing_values():
    reset_errors()

    df = pd.DataFrame({
        "A": [1, None]
    })

    dq03_missing_values(df, "companies")

    assert len(validation_errors) == 1


def test_dq03_no_missing_values():
    reset_errors()

    df = pd.DataFrame({
        "A": [1, 2]
    })

    dq03_missing_values(df, "companies")

    assert len(validation_errors) == 0


# ----------------------------------------------------
# DQ-04 Duplicate Rows
# ----------------------------------------------------

def test_dq04_duplicate_rows():
    reset_errors()

    df = pd.DataFrame({
        "A": [1, 1]
    })

    dq04_duplicate_rows(df, "companies")

    assert len(validation_errors) == 1


def test_dq04_no_duplicate_rows():
    reset_errors()

    df = pd.DataFrame({
        "A": [1, 2]
    })

    dq04_duplicate_rows(df, "companies")

    assert len(validation_errors) == 0


# ----------------------------------------------------
# DQ-05 Positive Sales
# ----------------------------------------------------

def test_dq05_negative_sales():
    reset_errors()

    df = pd.DataFrame({
        "sales": [-100]
    })

    dq05_positive_sales(df)

    assert len(validation_errors) == 1


def test_dq05_positive_sales():
    reset_errors()

    df = pd.DataFrame({
        "sales": [500]
    })

    dq05_positive_sales(df)

    assert len(validation_errors) == 0


# ----------------------------------------------------
# DQ-06 Balance Sheet
# ----------------------------------------------------

def test_dq06_invalid_balance_sheet():
    reset_errors()

    df = pd.DataFrame({
        "total_assets": [100],
        "total_liabilities": [200]
    })

    dq06_balance_sheet(df)

    assert len(validation_errors) == 1


def test_dq06_valid_balance_sheet():
    reset_errors()

    df = pd.DataFrame({
        "total_assets": [500],
        "total_liabilities": [400]
    })

    dq06_balance_sheet(df)

    assert len(validation_errors) == 0