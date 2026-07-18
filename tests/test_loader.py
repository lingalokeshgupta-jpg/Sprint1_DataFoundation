from src.etl.loader import load_all_files

def test_load_all_files():
    data = load_all_files()
    assert len(data) == 12