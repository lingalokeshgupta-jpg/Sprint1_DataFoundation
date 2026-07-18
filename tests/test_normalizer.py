from src.etl.normalizer import normalize_year, normalize_ticker

def test_normalize_year():
    assert normalize_year("2024") == 2024

def test_normalize_ticker():
    assert normalize_ticker(" infy ") == "INFY"