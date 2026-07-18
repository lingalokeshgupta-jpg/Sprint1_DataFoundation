import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch

from src.etl.loader import (
    load_excel,
    load_all_files,
    FILES,
    SKIP_ROWS
)


# ----------------------------------------------------
# load_excel()
# ----------------------------------------------------

@patch("src.etl.loader.pd.read_excel")
def test_load_excel_calls_read_excel(mock_read):
    mock_read.return_value = pd.DataFrame({"A":[1]})

    load_excel("companies.xlsx",1)

    mock_read.assert_called_once()


@patch("src.etl.loader.pd.read_excel")
def test_load_excel_returns_dataframe(mock_read):
    df = pd.DataFrame({"A":[1,2]})
    mock_read.return_value=df

    result=load_excel("companies.xlsx",1)

    assert isinstance(result,pd.DataFrame)


@patch("src.etl.loader.pd.read_excel")
def test_load_excel_row_count(mock_read):
    df=pd.DataFrame({"A":[1,2,3]})
    mock_read.return_value=df

    result=load_excel("companies.xlsx",1)

    assert len(result)==3


@patch("src.etl.loader.pd.read_excel")
def test_load_excel_empty_dataframe(mock_read):
    mock_read.return_value=pd.DataFrame()

    result=load_excel("companies.xlsx",1)

    assert result.empty


@patch("src.etl.loader.pd.read_excel")
def test_load_excel_skiprows(mock_read):
    mock_read.return_value=pd.DataFrame()

    load_excel("companies.xlsx",2)

    _,kwargs=mock_read.call_args

    assert kwargs["skiprows"]==2


@patch("src.etl.loader.pd.read_excel")
def test_invalid_file(mock_read):

    mock_read.side_effect=FileNotFoundError

    with pytest.raises(FileNotFoundError):
        load_excel("abc.xlsx")


# ----------------------------------------------------
# load_all_files()
# ----------------------------------------------------

@patch("src.etl.loader.load_excel")
def test_load_all_files(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    dfs=load_all_files()

    assert isinstance(dfs,dict)


@patch("src.etl.loader.load_excel")
def test_load_all_files_keys(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    dfs=load_all_files()

    assert set(dfs.keys())==set(FILES.keys())


@patch("src.etl.loader.load_excel")
def test_load_all_files_dataframe(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    dfs=load_all_files()

    for df in dfs.values():
        assert isinstance(df,pd.DataFrame)


@patch("src.etl.loader.load_excel")
def test_load_all_files_called(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    load_all_files()

    assert mock_loader.call_count==len(FILES)


@patch("src.etl.loader.load_excel")
def test_skip_rows_dictionary(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    load_all_files()

    for key in FILES:
        assert key in SKIP_ROWS


@patch("src.etl.loader.load_excel")
def test_each_dataframe_has_rows(mock_loader):

    mock_loader.return_value=pd.DataFrame({"A":[1]})

    dfs=load_all_files()

    for df in dfs.values():
        assert len(df)>=1