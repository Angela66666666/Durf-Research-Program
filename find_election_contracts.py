import duckdb
from pathlib import Path

base_dir = Path("/Users/liu/Desktop/Durf/prediction-market-analysis")
markets_dir = base_dir / "data" / "kalshi" / "markets"

con = duckdb.connect()

df = con.execute(f"""
    SELECT ticker, title, status, close_time, volume
    FROM '{markets_dir}/*.parquet'
    WHERE (
        title ILIKE '%president%' OR
        title ILIKE '%trump%' OR
        title ILIKE '%harris%' OR
        title ILIKE '%election%'
    )
    AND close_time >= '2024-09-01'
    AND close_time <= '2024-11-30'
    ORDER BY volume DESC NULLS LAST
""").df()

print(f"找到 {len(df)} 个相关合约\n")
print(df.to_string())

df.to_csv("election_contracts.csv", index=False)
print("\n已保存到 election_contracts.csv")