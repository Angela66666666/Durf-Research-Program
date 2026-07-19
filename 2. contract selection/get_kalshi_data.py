import requests

# 直接试几个可能的ticker格式
tickers_to_try = [
    "KXPRES-2024-TRUMP",
    "PRES-2024-DT",
    "PRES-2024-DJT",
    "KXPOTUS-2024",
    "KXPOTUS-2024-DJT",
]

for ticker in tickers_to_try:
    response = requests.get(
        "https://api.elections.kalshi.com/trade-api/v2/markets/trades",
        params={
            "ticker": ticker,
            "limit": 1,
        }
    )
    data = response.json()
    trades = data.get("trades", [])
    print(f"{ticker}: 状态码={response.status_code}, 找到trades={len(trades)}")