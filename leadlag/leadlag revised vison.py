import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Tuple, Optional
from pathlib import Path

# ====================== 全局可配置超参数（一键修改稳健性检验） ======================
HERE          = Path(__file__).parent
# CACHE_PATH不再使用，保留定义不影响运行
CACHE_PATH    = HERE / "kalshi_hf_cache.parquet"
ETF_HF_DIR    = HERE / "etf_hf"
SIG_PAIRS_CSV = HERE / ".." / "regression" / "significant_pairs.csv"
TRADES_DIR    = HERE / ".." / "prediction-market-analysis" / "data" / "kalshi" / "trades"
# Model B / C 的真实配对表（如不存在则自动跳过对应模型）
PAIR_CONTRACT_CSV = HERE / "pair_contract.csv"  # 字段: ticker_x, ticker_y, date_start, date_end
PAIR_ETF_CSV      = HERE / "pair_etf.csv"       # 字段: etf_x, etf_y, date_start, date_end


# 路径校验（保留，确认无误后可删除）
print("SIG_PAIRS_CSV 完整路径：", SIG_PAIRS_CSV.resolve())
print("文件是否存在：", SIG_PAIRS_CSV.exists())
print("ETF文件夹路径：", ETF_HF_DIR.resolve(), "存在？", ETF_HF_DIR.exists())

# 输出三套结果分开存储
OUT_KALSHI_ETF     = HERE / "leadlag_event_unified_kalshi_etf.csv"
OUT_CONTRACT_CONTR = HERE / "leadlag_event_unified_contract_contract.csv"
OUT_ETF_ETF        = HERE / "leadlag_event_unified_etf_etf.csv"

# 回归设定
K               = 10          # 前后K笔交易滞后阶数
W_SEC           = 300         # ETF收益最大观测窗口(秒)
MAX_GAP_SEC     = 120         # 允许最大ETF报价缺失间隔(秒)
MIN_OBS         = 2 * K + 5   # 滞后构造后最小样本量
RUN_MODEL_A     = True        # 主模型：Kalshi ↔ ETF
RUN_MODEL_B     = True        # 跨合约 benchmark（需要 pair_contract.csv）
RUN_MODEL_C     = True        # 跨 ETF benchmark（需要 pair_etf.csv）
ETF_BAR_FREQ    = "1s"        # Model C：ETF tick 降采样到 1 秒 bar（避免原始 tick 数百万行回归卡死）

MAX_GAP_NS = MAX_GAP_SEC * 1_000_000_000
W_NS       = W_SEC * 1_000_000_000

# 数据库连接
con = duckdb.connect()
sig_pairs = pd.read_csv(SIG_PAIRS_CSV)

# ====================== 共用工具函数（三套模型完全复用） ======================
def load_kalshi_trades(ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    raw_parquet_glob = str(TRADES_DIR / "*.parquet")
    q = f"""
    SELECT
        (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
        yes_price
    FROM read_parquet('{raw_parquet_glob}')
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
    idx    = np.searchsorted(etf_ns, query_ns, side="right") - 1
    result = np.full(len(query_ns), np.nan)
    valid  = idx >= 0
    vi     = np.where(valid)[0]
    gaps   = query_ns[vi] - etf_ns[idx[vi]]
    close  = gaps <= max_gap_ns
    result[vi[close]] = etf_mid[idx[vi[close]]]
    return result


def run_unified_regression(
        df_reg: pd.DataFrame,
        x_col: str,
        y_col: str,
        k_range: Tuple[int, int] = (-K, K)
) -> Optional[pd.DataFrame]:
    """
    通用联合滞后回归执行函数
    :param df_reg: 回归数据集
    :param x_col: 解释变量列名
    :param y_col: 被解释变量列名
    :param k_range: 滞后起止区间
    :return: 单组配对回归结果表
    """
    df_reg = df_reg.copy()  # 避免污染传入的 DataFrame
    lag_start, lag_end = k_range
    lag_cols = {}
    for k in range(lag_start, lag_end + 1):
        col = f"lag_{k:+d}"
        df_reg[col] = df_reg[x_col].shift(k)
        lag_cols[k] = col
    all_lag_cols = list(lag_cols.values())

    # 删除滞后构造缺失值
    df_reg = df_reg.dropna(subset=[y_col] + all_lag_cols)
    if len(df_reg) < MIN_OBS:
        return None

    # 标准化解释变量
    x_std = df_reg[x_col].std()
    if x_std > 1e-12:
        for col in all_lag_cols:
            df_reg[col] = df_reg[col] / x_std

    # 日固定效应
    day_dummies = pd.get_dummies(df_reg["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df_reg[all_lag_cols].astype(float), day_dummies], axis=1))
    y = df_reg[y_col].astype(float)

    # 聚类标准误 / HC3兜底
    groups = df_reg["date"].values
    try:
        if len(np.unique(groups)) >= 2:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        else:
            model = sm.OLS(y, X).fit(cov_type="HC3")
    except Exception as e:
        print(f"OLS估计失败: {str(e)}")
        return None

    # 提取系数结果
    res_rows = []
    n_obs_final = len(df_reg)
    unique_days = df_reg["date"].nunique()
    mean_w_sec = df_reg["actual_w_ns"].mean() / 1e9 if "actual_w_ns" in df_reg.columns else np.nan

    for k, col in lag_cols.items():
        if col not in model.params.index:
            continue
        if k > 0:
            direction = "x_leads_y"
        elif k < 0:
            direction = "y_leads_x"
        else:
            direction = "contemporaneous"

        res_rows.append({
            "k": k,
            "direction": direction,
            "coef": model.params[col],
            "t_stat": model.tvalues[col],
            "p_value": model.pvalues[col],
            "r_squared": model.rsquared,
            "n_obs": n_obs_final,
            "n_days": unique_days,
            "mean_window_sec": mean_w_sec
        })
    return pd.DataFrame(res_rows)

# ====================== Model A：原主模型 Kalshi Contract → ETF（老师原版公式） ======================
if RUN_MODEL_A:
    print("="*60)
    print("开始运行 Model A: Kalshi ↔ ETF 基准联合滞后回归")
    print("="*60)
    out_a = []
    for idx, pair in sig_pairs.iterrows():
        ticker_x = pair["contract_ticker"]
        etf_y = pair["etf"]
        ds = str(pair["date_start"])
        de = str(pair["date_end"])
        print(f"\n[{idx+1}/{len(sig_pairs)}] X:{ticker_x}  Y:{etf_y}")

        kalshi_x = load_kalshi_trades(ticker_x, ds, de)
        etf_y_ticks = load_etf_ticks(etf_y, ds, de)
        if len(kalshi_x) < MIN_OBS or etf_y_ticks.empty:
            print("跳过：样本量不足")
            continue

        # ETF价格匹配
        etf_ns = etf_y_ticks["ts_utc"].astype("datetime64[ns]").astype("int64").values
        etf_mid_arr = etf_y_ticks["mid"].values
        trade_ns = kalshi_x["ts_utc"].astype("datetime64[ns]").astype("int64").values

        etf_at_t = lookup_etf_mid(etf_ns, etf_mid_arr, trade_ns, MAX_GAP_NS)

        # 自适应截断收益窗口（不跨下一笔交易、不隔夜）
        dates_arr = kalshi_x["ts_utc"].dt.date.values
        same_day = dates_arr[:-1] == dates_arr[1:]
        raw_next_ns = np.empty_like(trade_ns)
        raw_next_ns[:-1] = np.where(same_day, trade_ns[1:], trade_ns[:-1] + W_NS)
        raw_next_ns[-1] = trade_ns[-1] + W_NS
        forward_ns = np.minimum(raw_next_ns, trade_ns + W_NS)

        etf_fwd = lookup_etf_mid(etf_ns, etf_mid_arr, forward_ns, MAX_GAP_NS)
        y_logret = np.log(etf_fwd / etf_at_t)
        actual_w_ns = forward_ns - trade_ns

        df_a = pd.DataFrame({
            "y_ret": y_logret,
            "x_prob_chg": kalshi_x["prob_change"].values,
            "date": kalshi_x["ts_utc"].dt.date,
            "actual_w_ns": actual_w_ns
        })

        res_df = run_unified_regression(df_a, x_col="x_prob_chg", y_col="y_ret")
        if res_df is None or res_df.empty:
            continue
        res_df["x_ticker"] = ticker_x
        res_df["y_etf"] = etf_y
        res_df["contract_title"] = pair.get("contract_title", "")
        res_df["r2_daily_screen"] = pair.get("r_squared", np.nan)
        res_df["n_kalshi_trades"] = len(kalshi_x)
        res_df["w_sec"] = W_SEC
        out_a.append(res_df)

    if out_a:
        df_out_a = pd.concat(out_a, ignore_index=True)
        # 输出 schema 与原版 leadlag_event_unified_results.csv 完全一致
        df_out_a = df_out_a.rename(columns={
            "x_ticker": "contract_ticker",
            "y_etf": "etf",
            "mean_window_sec": "mean_w_sec",
        })
        df_out_a["direction"] = df_out_a["direction"].map({
            "x_leads_y": "kalshi_leads_etf",
            "y_leads_x": "etf_leads_kalshi",
            "contemporaneous": "contemp",
        })
        df_out_a = df_out_a.drop(columns=["n_days"], errors="ignore")
        df_out_a = df_out_a[[
            "contract_ticker", "etf", "k", "direction", "coef", "t_stat", "p_value", "r_squared",
            "n_obs", "n_kalshi_trades", "w_sec", "mean_w_sec", "r2_daily_screen", "contract_title"
        ]]
        df_out_a.to_csv(OUT_KALSHI_ETF, index=False)
        print(f"\nModel A 完成，结果保存至: {OUT_KALSHI_ETF}")
        sig_a = df_out_a[df_out_a["p_value"] < 0.05]
        print(f"显著系数数量(p<0.05): {len(sig_a)} / {len(df_out_a)}")

# ====================== Model B：拓展1 Contract ↔ Contract ======================
if RUN_MODEL_B:
    print("\n" + "="*60)
    print("开始运行 Model B: Kalshi合约A ↔ Kalshi合约B 跨合约滞后检验")
    print("="*60)
    out_b = []
    # 需要提供合约两两配对表 pair_contract.csv，字段: ticker_x,ticker_y,date_start,date_end
    if not PAIR_CONTRACT_CSV.exists():
        print(f"跳过 Model B：未找到 {PAIR_CONTRACT_CSV}")
        print("请提供 pair_contract.csv，字段: ticker_x, ticker_y, date_start, date_end")
        pair_contr = pd.DataFrame()
    else:
        pair_contr = pd.read_csv(PAIR_CONTRACT_CSV)

    for idx, pair in pair_contr.iterrows():
        ticker_x = pair["ticker_x"]
        ticker_y = pair["ticker_y"]
        ds = str(pair["date_start"])
        de = str(pair["date_end"])
        if ticker_x == ticker_y:
            print(f"\n[{idx+1}/{len(pair_contr)}] 跳过自配对：{ticker_x}")
            continue
        print(f"\n[{idx+1}/{len(pair_contr)}] X:{ticker_x}  Y:{ticker_y}")

        kalshi_x = load_kalshi_trades(ticker_x, ds, de)
        kalshi_y = load_kalshi_trades(ticker_y, ds, de)
        if len(kalshi_x) < MIN_OBS or len(kalshi_y) < MIN_OBS:
            print("跳过：样本不足")
            continue

        # 按交易时间对齐（就近匹配）
        kalshi_x = kalshi_x.sort_values("ts_utc").reset_index(drop=True)
        kalshi_y = kalshi_y.sort_values("ts_utc").reset_index(drop=True)
        # 简单内连接时间就近对齐，也可以用lookup时序匹配
        df_b = pd.merge_asof(
            kalshi_x, kalshi_y, left_on="ts_utc", right_on="ts_utc",
            direction="nearest", tolerance=pd.Timedelta(f"{MAX_GAP_SEC}s")
        )
        df_b = df_b.dropna(subset=["prob_change_x", "prob_change_y"])
        df_b["date"] = df_b["ts_utc"].dt.date
        df_b["actual_w_ns"] = np.nan

        res_df = run_unified_regression(df_b, x_col="prob_change_x", y_col="prob_change_y")
        if res_df is None or res_df.empty:
            continue
        res_df["x_ticker"] = ticker_x
        res_df["y_ticker"] = ticker_y
        out_b.append(res_df)

    if out_b:
        df_out_b = pd.concat(out_b, ignore_index=True)
        df_out_b.to_csv(OUT_CONTRACT_CONTR, index=False)
        print(f"\nModel B 完成，结果保存至: {OUT_CONTRACT_CONTR}")

# ====================== Model C：拓展2 ETF ↔ ETF ======================
if RUN_MODEL_C:
    print("\n" + "="*60)
    print("开始运行 Model C: ETF1 ↔ ETF2 跨ETF领先滞后检验")
    print("="*60)
    out_c = []
    # 需要提供ETF两两配对表 pair_etf.csv，字段: etf_x,etf_y,date_start,date_end
    if not PAIR_ETF_CSV.exists():
        print(f"跳过 Model C：未找到 {PAIR_ETF_CSV}")
        print("请提供 pair_etf.csv，字段: etf_x, etf_y, date_start, date_end")
        pair_etf = pd.DataFrame()
    else:
        pair_etf = pd.read_csv(PAIR_ETF_CSV)

    for idx, pair in pair_etf.iterrows():
        etf_x = pair["etf_x"]
        etf_y = pair["etf_y"]
        ds = str(pair["date_start"])
        de = str(pair["date_end"])
        if etf_x == etf_y:
            print(f"\n[{idx+1}/{len(pair_etf)}] 跳过自配对：{etf_x}")
            continue
        print(f"\n[{idx+1}/{len(pair_etf)}] X:{etf_x}  Y:{etf_y}")

        etf_x_ticks = load_etf_ticks(etf_x, ds, de)
        etf_y_ticks = load_etf_ticks(etf_y, ds, de)
        if etf_x_ticks.empty or etf_y_ticks.empty:
            print("跳过：无ETF数据")
            continue

        # 降采样到 ETF_BAR_FREQ（默认 1 秒）bar，每个 bar 取末价
        # 原始 tick 太密（VGT 单 ETF 4 个月有 2700 万 tick），直接喂回归会卡死
        def to_bars(df, ret_col, freq):
            bars = (df.set_index("ts_utc")["mid"]
                      .resample(freq).last().dropna().to_frame())
            bars[ret_col] = np.log(bars["mid"]).diff()
            return bars[[ret_col]].dropna().reset_index()

        etf_x_bars = to_bars(etf_x_ticks, "ret_x", ETF_BAR_FREQ)
        etf_y_bars = to_bars(etf_y_ticks, "ret_y", ETF_BAR_FREQ)
        print(f"  降采样后: X={len(etf_x_bars):,} bars, Y={len(etf_y_bars):,} bars")

        df_c = pd.merge_asof(
            etf_x_bars, etf_y_bars, on="ts_utc",
            direction="nearest", tolerance=pd.Timedelta(f"{MAX_GAP_SEC}s")
        )
        df_c = df_c.dropna(subset=["ret_x", "ret_y"])
        df_c["date"] = df_c["ts_utc"].dt.date
        df_c["actual_w_ns"] = np.nan

        res_df = run_unified_regression(df_c, x_col="ret_x", y_col="ret_y")
        if res_df is None or res_df.empty:
            continue
        res_df["x_etf"] = etf_x
        res_df["y_etf"] = etf_y
        out_c.append(res_df)

    if out_c:
        df_out_c = pd.concat(out_c, ignore_index=True)
        df_out_c.to_csv(OUT_ETF_ETF, index=False)
        print(f"\nModel C 完成，结果保存至: {OUT_ETF_ETF}")

print("\n全部选定模型运行结束！")