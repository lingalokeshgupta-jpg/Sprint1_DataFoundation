import pandas as pd
from pathlib import Path


RAW_DATA = Path("data/raw")


FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
}


def load_excel(file_name, skip_rows=0):
    """Load an Excel file and return a DataFrame."""

    file_path = RAW_DATA / file_name

    return pd.read_excel(
        file_path,
        skiprows=skip_rows
    )


SKIP_ROWS = {
    "companies": 1,
    "profitandloss": 1,
    "balancesheet": 1,
    "cashflow": 1,
    "analysis": 1,
    "documents": 1,
    "prosandcons": 1,
    "financial_ratios": 0,
    "market_cap": 0,
    "peer_groups": 0,
    "sectors": 0,
    "stock_prices": 0,
}


def load_all_files():

    dataframes = {}

    for key, file in FILES.items():

        # ---------------------------------------------
        # LOAD EXCEL FILE
        # ---------------------------------------------

        df = load_excel(
            file,
            SKIP_ROWS[key]
        )

        # ---------------------------------------------
        # CASHFLOW CLEANING
        # ---------------------------------------------

        if key == "cashflow":

            print("\n========== CASHFLOW CHECK ==========")

            # Check ATGL
            atgl = df[
                df["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
                == "ATGL"
            ]

            print(atgl)
            print("ATGL rows:", len(atgl))

            # -----------------------------------------
            # REMOVE ONLY EXACT DUPLICATES
            # -----------------------------------------

            before = len(df)

            df = df.drop_duplicates(
                subset=[
                    "company_id",
                    "year",
                    "operating_activity",
                    "investing_activity",
                    "financing_activity",
                    "net_cash_flow"
                ],
                keep="first"
            )

            exact_duplicates_removed = (
                before - len(df)
            )

            print(
                "Identical cashflow duplicates removed:",
                exact_duplicates_removed
            )

            # -----------------------------------------
            # REMOVE SECOND ABB SOURCE BLOCK
            # -----------------------------------------
            #
            # The source cashflow.xlsx contains:
            #
            # ABB IDs 61-72 -> original ABB records
            # ABB IDs 73-83 -> duplicate ABB block
            #
            # We keep IDs 61-72 and remove 73-83.
            # -----------------------------------------

            if "id" in df.columns:

                abb_second_block = (
                    (
                        df["company_id"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        == "ABB"
                    )
                    &
                    (df["id"] >= 73)
                    &
                    (df["id"] <= 83)
                )

                removed_abb = int(
                    abb_second_block.sum()
                )

                df = df[
                    ~abb_second_block
                ].copy()

                print(
                    "ABB duplicate block rows removed:",
                    removed_abb
                )

            # -----------------------------------------
            # FINAL CASHFLOW CHECK
            # -----------------------------------------

            print(
                "Cashflow rows after cleaning:",
                len(df)
            )

            remaining_abb = df[
                df["company_id"]
                .astype(str)
                .str.strip()
                .str.upper()
                == "ABB"
            ]

            print(
                "ABB rows after cleaning:",
                len(remaining_abb)
            )

        # ---------------------------------------------
        # STORE DATAFRAME
        # ---------------------------------------------

        dataframes[key] = df

        print(
            f"{key}: {len(df)} rows loaded"
        )

    return dataframes


# --------------------------------------------------
# TEST LOADER
# --------------------------------------------------

if __name__ == "__main__":

    data = load_all_files()

    for name, df in data.items():

        print(
            f"\n{name.upper()} COLUMNS"
        )

        print(
            df.columns.tolist()
        )