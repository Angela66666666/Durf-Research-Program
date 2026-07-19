# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "duckdb>=1.2.0",
#   "pandas>=2.2.0",
# ]
# ///

import duckdb

PRICE_PARQUET_URL = "/Users/liu/Desktop/Durf/etf_data/stock_prices.parquet"

DIVIDEND_PARQUET_URL = "/Users/liu/Desktop/Durf/etf_data/stock_dividend_events.parquet"

# Optional, but useful as a diagnostic. If there are splits, close-price returns need split adjustment too.
SPLIT_PARQUET_URL = "/Users/liu/Desktop/Durf/etf_data/stock_split_events.parquet"

VANGUARD_SECTOR_ETFS = [
    "VOX",  # Communication Services
    "VCR",  # Consumer Discretionary
    "VDC",  # Consumer Staples
    "VDE",  # Energy
    "VFH",  # Financials
    "VHT",  # Health Care
    "VIS",  # Industrials
    "VGT",  # Information Technology
    "VAW",  # Materials
    "VNQ",  # Real Estate
    "VPU",  # Utilities
]

START_DATE = "2024-09-01"
END_DATE = "2024-12-31"
OUTPUT_CSV = "vanguard_sector_etf_total_returns.csv"


def main() -> None:
    con = duckdb.connect()

    con.execute("INSTALL httpfs;")
    con.execute("LOAD httpfs;")

    tickers_sql = ", ".join(f"'{ticker}'" for ticker in VANGUARD_SECTOR_ETFS)

    # Optional sanity check: if non-empty, raw close prices also need split adjustment.
    split_events = con.execute(f"""
        SELECT
            upper(symbol) AS ticker,
            CAST(report_date AS DATE) AS date,
            split_factor
        FROM read_parquet('{SPLIT_PARQUET_URL}')
        WHERE upper(symbol) IN ({tickers_sql})
          AND CAST(report_date AS DATE) BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
        ORDER BY ticker, date
    """).df()

    if not split_events.empty:
        print("WARNING: Split events found. Close-price total returns need split adjustment too.")
        print(split_events)
        print()

    query = f"""
        WITH prices AS (
            SELECT
                upper(symbol) AS ticker,
                CAST(report_date AS DATE) AS date,
                CAST(close AS DOUBLE) AS close
            FROM read_parquet('{PRICE_PARQUET_URL}')
            WHERE upper(symbol) IN ({tickers_sql})
              AND CAST(report_date AS DATE) BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
        ),

        dividends AS (
            SELECT
                upper(symbol) AS ticker,
                CAST(report_date AS DATE) AS date,
                SUM(CAST(amount AS DOUBLE)) AS dividend
            FROM read_parquet('{DIVIDEND_PARQUET_URL}')
            WHERE upper(symbol) IN ({tickers_sql})
              AND CAST(report_date AS DATE) BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
            GROUP BY ticker, date
        ),

        price_dividend AS (
            SELECT
                p.ticker,
                p.date,
                p.close,
                COALESCE(d.dividend, 0.0) AS dividend
            FROM prices AS p
            LEFT JOIN dividends AS d
              ON p.ticker = d.ticker
             AND p.date = d.date
        ),

        returns AS (
            SELECT
                ticker,
                date,
                close,
                dividend,
                LAG(close) OVER (
                    PARTITION BY ticker
                    ORDER BY date
                ) AS lag_close
            FROM price_dividend
        )

        SELECT
            ticker,
            date,
            close,
            dividend,
            lag_close,

            close / lag_close - 1 AS daily_price_return,

            (close + dividend) / lag_close - 1 AS daily_total_return,

            dividend / lag_close AS dividend_return_component
        FROM returns
        WHERE date > DATE '{START_DATE}'
          AND lag_close IS NOT NULL
        ORDER BY ticker, date
    """

    daily_returns = con.execute(query).df()

    print(daily_returns.head(20))
    print()
    print(f"Rows: {len(daily_returns):,}")
    print(f"Tickers: {daily_returns['ticker'].nunique()}")

    dividend_days = daily_returns[daily_returns["dividend"] != 0]
    print(f"Dividend event rows: {len(dividend_days):,}")
    if not dividend_days.empty:
        print()
        print("Dividend rows:")
        print(dividend_days[["ticker", "date", "close", "dividend", "daily_total_return"]])

    daily_returns.to_csv(OUTPUT_CSV, index=False)
    print()
    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()