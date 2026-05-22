import duckdb
from pathlib import Path

base_dir = Path("/Users/liu/Desktop/Durf/prediction-market-analysis")
markets_dir = base_dir / "data" / "kalshi" / "markets"

con = duckdb.connect()

# Keywords grouped by ETF sector relevance
SECTOR_KEYWORDS = {
    "VFH_VNQ_VPU (Rate-sensitive: Financials / Real Estate / Utilities)": [
        "federal reserve", "rate cut", "rate hike", "fed ", "bps", "interest rate",
    ],
    "VDE (Energy)": [
        "oil", "gas", "energy", "drill", "pipeline", "opec", "lng",
    ],
    "VHT (Health Care)": [
        "health", "pharma", "drug", "medicare", "medicaid", "aca", "obamacare", "fda",
    ],
    "VIS_VAW (Industrials / Materials)": [
        "tariff", "trade", "infrastructure", "defense", "military", "steel", "china",
    ],
    "VGT (Information Technology)": [
        "antitrust", "tech regulation", "ai regulation", "tiktok",
    ],
    "Election outcome (all sectors)": [
        "president", "trump", "harris", "election", "electoral",
    ],
}

all_keywords = [kw for keywords in SECTOR_KEYWORDS.values() for kw in keywords]
conditions = " OR ".join(f"title ILIKE '%{kw}%'" for kw in all_keywords)

df = con.execute(f"""
    SELECT ticker, title, status, close_time, volume
    FROM '{markets_dir}/*.parquet'
    WHERE ({conditions})
    AND close_time >= '2024-09-01'
    AND close_time <= '2024-12-31'
    AND volume > 1000
    ORDER BY volume DESC NULLS LAST
""").df()

# Tag each contract with its sector group
def tag_sector(title):
    title_lower = title.lower()
    tags = []
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(kw in title_lower for kw in keywords):
            tags.append(sector)
    return " | ".join(tags)

df["sector_relevance"] = df["title"].apply(tag_sector)

print(f"找到 {len(df)} 个相关合约\n")
for sector in SECTOR_KEYWORDS:
    subset = df[df["sector_relevance"].str.contains(sector.split()[0], na=False)]
    print(f"\n{'='*60}")
    print(f"{sector}: {len(subset)} 个合约")
    print(subset[["ticker", "title", "volume"]].head(10).to_string())

df.to_csv("election_contracts.csv", index=False)
print(f"\n\n全部已保存到 election_contracts.csv")