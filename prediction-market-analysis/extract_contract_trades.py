import duckdb
import pandas as pd
from pathlib import Path

base_dir = Path("/Users/liu/Desktop/Durf/prediction-market-analysis")
ec = pd.read_csv(base_dir / "election_contracts - election_contracts.csv")
tickers = ec["ticker"].tolist()

# DuckDB 用 IN 列表过滤，一次扫全部 parquet
ticker_list = ", ".join(f"'{t}'" for t in tickers)

con = duckdb.connect()
print(f"正在从 {len(tickers)} 个合约里提取每日交易数据，请稍候...")

daily = con.execute(f"""
    SELECT
        ticker,
        DATE_TRUNC('day', created_time AT TIME ZONE 'UTC') AS trade_date,
        -- 成交量加权平均 yes_price（相当于当日 VWAP）
        SUM(yes_price * count) / SUM(count)  AS vwap_yes_price,
        -- 当日最后一笔成交价（收盘价替代）
        LAST(yes_price ORDER BY created_time)  AS close_yes_price,
        -- 当日第一笔成交价（开盘价替代）
        FIRST(yes_price ORDER BY created_time) AS open_yes_price,
        -- 当日合约数量总和（成交量）
        SUM(count) AS daily_volume,
        -- 成交笔数
        COUNT(*) AS n_trades
    FROM 'data/kalshi/trades/*.parquet'
    WHERE ticker IN ({ticker_list})
    GROUP BY ticker, DATE_TRUNC('day', created_time AT TIME ZONE 'UTC')
    ORDER BY ticker, trade_date
""").df()

print(f"提取完成：{len(daily)} 行，{daily['ticker'].nunique()} 个合约")

# 合并合约元数据（标题、板块）
meta = ec[["ticker", "title", "sector_relevance", "close_time", "volume"]].copy()
daily = daily.merge(meta, on="ticker", how="left")

# 调整列顺序
cols = ["ticker", "title", "sector_relevance", "trade_date",
        "open_yes_price", "close_yes_price", "vwap_yes_price",
        "daily_volume", "n_trades", "close_time", "volume"]
daily = daily[cols]

out_path = base_dir / "contract_daily_prices.csv"
daily.to_csv(out_path, index=False)

size_kb = out_path.stat().st_size / 1024
print(f"已保存到 contract_daily_prices.csv（{size_kb:.0f} KB）")
print(f"\n各合约交易天数分布：")
print(daily.groupby("ticker")["trade_date"].count().describe())
