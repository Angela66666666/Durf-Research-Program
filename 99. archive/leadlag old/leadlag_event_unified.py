"""
事件驱动的教授统一回归（秒级 + 联合估计）。

公式：
    r_{i,t} = α + Σ_{k=-K}^{K} β_k Δς(p_{t-k}) + γ'X_t + ε_{i,t}

本脚本将 t 定义为 Kalshi 交易事件序号（而非日历分钟），解决稀疏性问题：

    ETF_return_i = α + Σ_{k=-K}^{K} β_k * prob_change_{i-k} + day_FE + ε_i

  ETF_return_i     : 第 i 笔交易后 W_SEC 秒内的 ETF 对数收益率（秒级精度）
  prob_change_{i-k}: 第 (i-k) 笔交易的概率变化
  k > 0            : 过去的 Kalshi 交易 → β_k 显著说明 Kalshi 领先 ETF
  k < 0            : 未来的 Kalshi 交易 → β_k 显著说明 ETF 领先 Kalshi
  k = 0            : 同期效应

  优势：每笔 Kalshi 交易都是一条观测，无稀疏性；使用 TAQ 秒级精度定价。

输入：
  leadlag/kalshi_hf_cache.parquet
  leadlag/etf_hf/<ETF>_hf.parquet
  regression/significant_pairs.csv （所有组合，不过滤）

输出：
  leadlag/leadlag_event_unified_results.csv
"""

import duckdb #负责执行SQL，读取parquet文件
import pandas as pd #负责把结果存成表格，做列运算
import numpy as np #负责数学计算
import statsmodels.api as sm #负责跑回归
from pathlib import Path

HERE          = Path(__file__).parent
CACHE_PATH    = HERE / "kalshi_hf_cache.parquet"
ETF_HF_DIR    = HERE / "etf_hf"
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
OUT_CSV       = HERE / "leadlag_event_unified_results.csv"

K       = 10          # 交易序号的前后 K 笔（lag -K 到 +K，共 2K+1 项）
W_SEC   = 300         # ETF 收益率测量窗口上限（秒）
MIN_OBS = 2 * K + 5   # 构建 lag 矩阵后的最小观测数（25）

con = duckdb.connect()
sig = pd.read_csv(SIG_PAIRS_CSV)


def load_kalshi_trades(ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    q = f"""
    SELECT
        (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
        yes_price
    FROM read_parquet('{CACHE_PATH}')
    WHERE ticker       = '{ticker}'
      AND created_time >= TIMESTAMPTZ '{date_start} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{date_end} 23:59:59+00'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"]      = pd.to_datetime(df["ts_utc"])
    df["prob"]        = df["yes_price"] / 100.0
    df["prob_change"] = df["prob"].diff()
    return df.dropna(subset=["prob_change"]).reset_index(drop=True)


def load_etf_ticks(etf: str, date_start: str, date_end: str) -> pd.DataFrame:
    etf_path = str(ETF_HF_DIR / f"{etf}_hf.parquet")
    q = f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM   read_parquet('{etf_path}')
    WHERE  timestamp_utc >= TIMESTAMP '{date_start} 00:00:00'
      AND  timestamp_utc <= TIMESTAMP '{date_end} 23:59:59'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"] = pd.to_datetime(df["ts_utc"])
    return df.dropna(subset=["mid"]).reset_index(drop=True)


def lookup_etf_mid(etf_ns: np.ndarray, etf_mid: np.ndarray,
                   query_ns: np.ndarray, max_gap_ns: int) -> np.ndarray:
    """最近前向插值：返回每个查询时刻之前最近一笔 ETF mid 价格。"""
    idx    = np.searchsorted(etf_ns, query_ns, side="right") - 1
    result = np.full(len(query_ns), np.nan) #创建一个长度为len(query_ns)的列表，且每一个都填上nan
    valid  = idx >= 0
    vi     = np.where(valid)[0]
    gaps   = query_ns[vi] - etf_ns[idx[vi]] #想找的那笔ETF价格和你查询的时刻差了多久
    close  = gaps <= max_gap_ns #如果超过max_gap_ns就认为太旧，就设为NaN，表示没有数据
    result[vi[close]] = etf_mid[idx[vi[close]]]
    return result


# ── 主循环 ─────────────────────────────────────────────────────────────────────
rows = []
MAX_GAP_NS = 120 * 1_000_000_000   # 2 分钟内无 ETF tick 则设为 NaN
W_NS       = W_SEC * 1_000_000_000

for i, pair in sig.iterrows(): #sig来自significant_pairs
    ticker     = pair["contract_ticker"] #对每一行的每一个合约信息，依次取出以下四个信息
    etf        = pair["etf"]
    date_start = str(pair["date_start"])
    date_end   = str(pair["date_end"])

    print(f"[{i+1}/{len(sig)}] {ticker} × {etf}  ({date_start} → {date_end})", end="  ")

    kalshi    = load_kalshi_trades(ticker, date_start, date_end)
    etf_ticks = load_etf_ticks(etf, date_start, date_end)

    if len(kalshi) < MIN_OBS or etf_ticks.empty:
        print(f"skipped ({len(kalshi)} trades)")
        continue

    etf_ns   = etf_ticks["ts_utc"].astype("datetime64[ns]").astype("int64").values
    etf_mid  = etf_ticks["mid"].values
    trade_ns = kalshi["ts_utc"].astype("datetime64[ns]").astype("int64").values
    #把pandas的列转成numpy数组，并且把时间换算成一个数字（eg：从某年某月某日到今天的纳秒数）
    # ETF 参考价格（t 时刻）：要求 2 分钟内有报价
    etf_at_t = lookup_etf_mid(etf_ns, etf_mid, trade_ns, MAX_GAP_NS)

    # 自适应前向时间戳：到下一笔同日 Kalshi 交易为止，最多 W_NS
    # 如果下一笔跨天（隔夜），直接用 W_NS 上限，避免含隔夜跳空
    dates            = kalshi["ts_utc"].dt.date.values
    same_day         = dates[:-1] == dates[1:]
    raw_next_ns      = np.empty_like(trade_ns)
    raw_next_ns[:-1] = np.where(same_day, trade_ns[1:], trade_ns[:-1] + W_NS) #where是一个if-else的逻辑，where（条件，if True，else）
    raw_next_ns[-1]  = trade_ns[-1] + W_NS
    forward_ns       = np.minimum(raw_next_ns, trade_ns + W_NS)
    #如果是同一天，那么窗口到下一笔交易为止，如果不是，则停在300秒之后
    etf_at_fwd = lookup_etf_mid(etf_ns, etf_mid, forward_ns, MAX_GAP_NS)
    etf_logret = np.log(etf_at_fwd / etf_at_t)      # NaN 仅当参考价缺失
    actual_w_ns = (forward_ns - trade_ns).astype(float)  # 每笔实际窗口长度（ns）
#计算这段时间ETF return是多少
    # 构建事件序号 lag 矩阵
    df = pd.DataFrame({
        "etf_logret":   etf_logret,
        "prob_change":  kalshi["prob_change"].values,
        "date":         kalshi["ts_utc"].dt.date.values,
        "actual_w_ns":  actual_w_ns,
    })

    # shift(k): k>0 → 取第 i-k 行的值（k 笔之前的交易）
    #           k<0 → 取第 i+|k| 行的值（|k| 笔之后的交易）
    # 不 fillna：头尾各 K 行边界观测自然截断，避免引入虚假 0 值压缩系数
    lag_cols = {}
    for k in range(-K, K + 1):
        col = f"lag_{k:+d}"
        df[col] = df["prob_change"].shift(k)
        lag_cols[k] = col

    all_lag_cols = list(lag_cols.values())
    df = df.dropna(subset=["etf_logret"] + all_lag_cols)

    # prob_change 标准化：不同合约价格跳动幅度差异大（有的 1–5，有的 40–60）
    # 标准化后系数含义统一为"prob_change 变动 1σ 对应的 ETF 收益变动"，跨合约可比
    # 注意：必须在 dropna 之后用实际进入回归的数据计算 std，且所有 lag 列除以同一个 std
    prob_std = df["prob_change"].std()
    if prob_std > 0:
        for col in all_lag_cols:
            df[col] = df[col] / prob_std

    if len(df) < MIN_OBS:
        print(f"skipped ({len(df)} obs after lags)")
        continue

    mean_w_sec = float(df["actual_w_ns"].mean() / 1e9)
    n_days     = df["date"].nunique()
    print(f"{len(kalshi)} trades → {len(df)} obs  mean_w={mean_w_sec:.0f}s  days={n_days}")
    if n_days == 1:
        print(f"  warning: only 1 day of data, day FE not added")

    # 日期固定效应
    day_dummies = pd.get_dummies(df["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df[all_lag_cols].astype(float), day_dummies], axis=1))
    y = df["etf_logret"].astype(float)

    try:
        # 按日期聚类标准误：同一天内交易存在序列相关，聚类比 HC3 更保守
        groups = df["date"].values
        if len(np.unique(groups)) < 2:
            m = sm.OLS(y, X).fit(cov_type="HC3")
        else:
            m = sm.OLS(y, X).fit(cov_type="cluster",
                                  cov_kwds={"groups": groups})
    except Exception as e:
        print(f"  OLS failed: {e}")
        continue

    for k in range(-K, K + 1):
        col = lag_cols[k]
        if col not in m.params:
            continue
        if k > 0:
            direction = "kalshi_leads_etf"
        elif k < 0:
            direction = "etf_leads_kalshi"
        else:
            direction = "contemp"

        rows.append({
            "contract_ticker":  ticker,
            "etf":              etf,
            "k":                k,
            "direction":        direction,
            "coef":             m.params[col],
            "t_stat":           m.tvalues[col],
            "p_value":          m.pvalues[col],
            "r_squared":        m.rsquared,
            "n_obs":            int(len(df)),
            "n_kalshi_trades":  int(len(kalshi)),
            "w_sec":            W_SEC,
            "mean_w_sec":       mean_w_sec,
            "r2_daily_screen":  pair["r_squared"],
            "contract_title":   pair["contract_title"],
        })

# ── 保存 ───────────────────────────────────────────────────────────────────────
out = pd.DataFrame(rows)
out.to_csv(OUT_CSV, index=False)

print(f"\n共估计系数: {len(out)}")
print(f"已保存 → {OUT_CSV}\n")

# ── 汇总：所有结果，不过滤 ─────────────────────────────────────────────────────
print("所有显著系数（p < 0.05），按 p 值排序：\n")
sig_out = out[out["p_value"] < 0.05].sort_values("p_value")
print(f"显著数: {len(sig_out)} / {len(out)}")

show = ["contract_ticker", "etf", "k", "direction", "coef", "t_stat", "p_value",
        "n_obs", "n_kalshi_trades"]
with pd.option_context("display.width", 220, "display.max_colwidth", 45,
                       "display.float_format", "{:.4f}".format):
    print(sig_out[show].to_string(index=False))

print("\n各 k 值显著系数数量：")
k_summary = (
    out[out["p_value"] < 0.05]
    .groupby(["direction", "k"])
    .size()
    .reset_index(name="n_sig")
    .sort_values(["direction", "k"])
)
print(k_summary.to_string(index=False))
