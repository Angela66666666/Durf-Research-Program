import yfinance as yf
import pandas as pd

VANGUARD_SECTOR_ETFS = [
    "VOX", "VCR", "VDC", "VDE", "VFH",
    "VHT", "VIS", "VGT", "VAW", "VNQ", "VPU",
]

START_DATE = "2024-09-01"
END_DATE = "2024-12-31"
OUTPUT_CSV = "/Users/liu/Desktop/Durf/etf_data/vanguard_sector_etf_total_returns.csv"


def main():
    all_rows = []

    for ticker in VANGUARD_SECTOR_ETFS:
        print(f"Downloading {ticker}...")
        tk = yf.Ticker(ticker)

        prices = tk.history(start=START_DATE, end=END_DATE, auto_adjust=False)
        prices.index = prices.index.tz_localize(None)
        prices = prices[["Close", "Dividends"]].copy()
        prices.columns = ["close", "dividend"]
        prices["ticker"] = ticker
        prices["date"] = prices.index.date
        prices = prices.reset_index(drop=True)[["ticker", "date", "close", "dividend"]]

        prices["lag_close"] = prices["close"].shift(1)
        prices = prices.dropna(subset=["lag_close"])

        prices["daily_price_return"] = prices["close"] / prices["lag_close"] - 1
        prices["daily_total_return"] = (prices["close"] + prices["dividend"]) / prices["lag_close"] - 1
        prices["dividend_return_component"] = prices["dividend"] / prices["lag_close"]

        all_rows.append(prices)

    df = pd.concat(all_rows, ignore_index=True).sort_values(["ticker", "date"])

    print(df.head(20))
    print()
    print(f"Rows: {len(df):,}")
    print(f"Tickers: {df['ticker'].nunique()}")

    dividend_days = df[df["dividend"] != 0]
    print(f"Dividend event rows: {len(dividend_days):,}")
    if not dividend_days.empty:
        print("\nDividend rows:")
        print(dividend_days[["ticker", "date", "close", "dividend", "daily_total_return"]])

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
