"""
leadlag_common.py
================================================================================
这个文件做什么 (What this file does)
  Lead-Lag 流水线的「共享底座」：时区转换、盘内过滤、outlier 清洗、bar/K 选择、
  数据加载、因果取点构造、联合滞后回归引擎，全部集中在这一个模块里。
  calendar / event / probit / classification 等脚本都 import 它。
  The shared core of the lead-lag pipeline: timezone conversion, market-hours
  filtering, outlier cleaning, bar/K selection, data loading, causal bar
  construction, and the joint-lag regression engine — imported by every script.

为什么这么做 (Why)
  口径只在一处定义，全项目唯一。这样 calendar 与 event 两套结果**唯一的差别**
  就是「时间轴怎么定义」本身，不会因为各脚本各写一套而引入不可比的差异。
  Define every convention exactly once so the only difference between the two
  time-axes is the axis definition itself, not incidental implementation drift.

思路 / 关键口径 (Approach / conventions — 改这里即全局生效)
  - 时区：一律 America/New_York (ET)；DST 由 duckdb ICU 自动处理；落到 pandas 是 ET 墙钟 naive
  - 盘内：只保留 09:30:00 <= t < 16:00:00 ET（盘前盘后结构不同、不可比，剔除）
  - ETF：用对数收益 log return（mid 非平稳、跨时不可加；mid 只作算 return 的原料）
  - Kalshi：prob = yes_price/100；prob_change = 同一交易日内相邻差分（不跨隔夜）
  - outlier：用 **重采样 + bar 内取 median** 吸收瞬时尖峰（如 5->28->5 的来回是 sub-bar 噪声，
            取中位数后少数尖峰对代表值无影响，自然消失；真实持续变动留得住，无需逐点删除/阈值裁量）

输出 (Outputs)
  本文件不直接产出文件；它是被 import 的函数库，产物由各调用脚本写出。
  No files written here; this is a function library used by the other scripts.

函数总览 (Functions)
  median_intertrade_sec  合约盘内同日成交间隔中位数（刻画交易节奏）
  choose_bar_sec         按成交节奏选 bar 大小
  choose_k               按活跃度选滞后阶数 K（活跃→大，稀疏→小）
  make_con               建 duckdb 连接（会话时区固定 UTC）
  load_kalshi            读单合约成交、转 ET、过滤盘内、算 prob / prob_change
  load_etf               读单 ETF 高频 mid、转 ET、过滤盘内
  bar_median_series      重采样成因果右沿 median bar（清 outlier 的核心）
  causal_bars            同上（语义命名版，供 build_unified_xy 调用）
  build_unified_xy       两边同口径因果构造，产出 calendar 网格 + event 活跃序列
  lookup_etf_mid         按时间就近匹配 ETF 报价（event 模式用）
  run_joint_lag_regression  联合滞后回归引擎（两套模式共用）
"""
from __future__ import annotations
import datetime as _dt
from pathlib import Path
from typing import Optional, Tuple

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ====================== 全局数据口径（统一配置，改这里即全局生效） ======================
HERE          = Path(__file__).parent          # leadlag/pipeline/
LEADLAG_DIR   = HERE.parent                     # leadlag/
PROJ_ROOT     = LEADLAG_DIR.parent              # Durf/  项目根
ETF_HF_DIR    = LEADLAG_DIR / "etf_hf"          # etf_hf 仍在 leadlag/ 下（770MB，不随脚本移动）
SIG_PAIRS_CSV = PROJ_ROOT / "regression" / "significant_pairs.csv"
# 注意：用 trades_*.parquet 精确匹配，排除 macOS 在 exFAT 卷上生成的 ._trades_*.parquet 垃圾文件
TRADES_GLOB   = str((PROJ_ROOT / "prediction-market-analysis" / "data" / "kalshi" / "trades" / "trades_*.parquet").resolve())

TZ            = "America/New_York"   # 全项目唯一时区
MARKET_OPEN   = _dt.time(9, 30, 0)   # 正规盘开盘 09:30 ET
MARKET_CLOSE  = _dt.time(16, 0, 0)   # 正规盘收盘 16:00 ET（左闭右开）

# outlier 处理：不用任何 σ/绝对阈值或 Hampel 逐点删除；改用 resampling。
# Outliers handled by resampling, not point-deletion — see bar_median_series():
# bar 内取 median，瞬时尖峰被稳健吸收。

# 回归设定
W_SEC         = 300       # event 模式：ETF 前向收益最大观测窗口(秒)
MAX_GAP_SEC   = 120       # ETF 报价就近匹配允许的最大缺口(秒)

# calendar 模式：bar 大小按合约自身活跃度一合约一选（不固定 1 分钟）。
# 候选网格全部会跑一遍作 robustness，其中"按活跃度选中"的那个标为主 bar。
BAR_GRID_SEC  = [30, 60, 120, 300, 600]          # 30s / 1m / 2m / 5m / 10m
BAR_LABEL     = {30: "30s", 60: "1min", 120: "2min", 300: "5min", 600: "10min"}


def median_intertrade_sec(df, tcol: str = "ts_et", datecol: str = "date") -> float:
    """合约盘内、同日内成交间隔中位数（秒），刻画其交易节奏。无足够样本返回 inf。"""
    if df.empty:
        return float("inf")
    gaps = (df.sort_values(tcol)
              .groupby(datecol)[tcol].diff().dt.total_seconds())
    gaps = gaps[gaps > 0]
    return float(gaps.median()) if len(gaps) else float("inf")


def choose_bar_sec(median_gap_sec: float) -> int:
    """按活跃度选 bar：取候选网格里第一个 >= 成交间隔中位数的 bar（典型 bar 约含一笔成交）。
    非有限值(inf/nan，成交太少算不出间隔)统一回退到 60s，与 probit 口径一致。"""
    if not np.isfinite(median_gap_sec):
        return 60
    for s in BAR_GRID_SEC:
        if s >= median_gap_sec:
            return s
    return BAR_GRID_SEC[-1]

# K 按合约活跃度选（活跃→大，稀疏→小）。门槛透明列在这里，便于审查/调整。
K_TIERS = [
    (500, 10),   # n_active >= 500  -> K=10
    (200, 8),    # 200-499          -> K=8
    (100, 6),    # 100-199          -> K=6
    (40,  5),    # 40-99            -> K=5
    (15,  4),    # 15-39            -> K=4
    (0,   3),    # <15              -> K=3
]


def choose_k(n_active: int) -> int:
    """按活跃度（有效观测数）选 K：活跃合约 K 大(最高10)，稀疏合约 K 小(最低3)。"""
    for thresh, k in K_TIERS:
        if n_active >= thresh:
            return k
    return 3


# ====================== 数据加载（统一转 ET + 盘内过滤） ======================
def make_con() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("SET TimeZone='UTC'")  # 固定会话时区，避免本机时区干扰 tz-aware 列的解释
    return con


def _filter_market_hours(df: pd.DataFrame, tcol: str = "ts_et") -> pd.DataFrame:
    """只保留 09:30<=t<16:00 ET 的正规盘内数据。"""
    if df.empty:
        return df
    t = df[tcol].dt.time
    return df[(t >= MARKET_OPEN) & (t < MARKET_CLOSE)].reset_index(drop=True)


def load_kalshi(con, ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    """加载单合约 Kalshi 成交，时间转 ET 墙钟，过滤盘内，计算 prob / prob_change（同日内差分）。"""
    q = f"""
    SELECT (created_time AT TIME ZONE '{TZ}') AS ts_et, yes_price
    FROM   read_parquet('{TRADES_GLOB}')
    WHERE  ticker = '{ticker}'
      AND  (created_time AT TIME ZONE '{TZ}')::DATE >= DATE '{date_start}'
      AND  (created_time AT TIME ZONE '{TZ}')::DATE <= DATE '{date_end}'
    ORDER BY 1
    """
    df = con.execute(q).df()
    if df.empty:
        return df
    df["ts_et"] = pd.to_datetime(df["ts_et"])
    df = _filter_market_hours(df)
    if df.empty:
        return df
    df["date"] = df["ts_et"].dt.date
    df["prob"] = df["yes_price"] / 100.0
    # 同一交易日内差分，不跨隔夜
    df["prob_change"] = df.groupby("date")["prob"].diff()
    return df.dropna(subset=["prob_change"]).reset_index(drop=True)


def load_etf(con, etf: str, date_start: str, date_end: str) -> pd.DataFrame:
    """加载单 ETF 高频 mid，时间转 ET 墙钟，过滤盘内。mid 仅作后续算 return 的原始输入。"""
    etf_path = str((ETF_HF_DIR / f"{etf}_hf.parquet").resolve())
    q = f"""
    SELECT (timestamp_utc AT TIME ZONE 'UTC' AT TIME ZONE '{TZ}') AS ts_et, mid
    FROM   read_parquet('{etf_path}')
    WHERE  (timestamp_utc AT TIME ZONE 'UTC' AT TIME ZONE '{TZ}')::DATE >= DATE '{date_start}'
      AND  (timestamp_utc AT TIME ZONE 'UTC' AT TIME ZONE '{TZ}')::DATE <= DATE '{date_end}'
    ORDER BY 1
    """
    df = con.execute(q).df()
    if df.empty:
        return df
    df["ts_et"] = pd.to_datetime(df["ts_et"])
    df = _filter_market_hours(df)
    if df.empty:
        return df
    df["date"] = df["ts_et"].dt.date
    # 防御：剔除非正/非有限的 mid（脏 tick 会让 log 价变 -inf/nan，污染回归或静默丢样本）
    df = df.dropna(subset=["mid"])
    df = df[np.isfinite(df["mid"]) & (df["mid"] > 0)]
    return df.reset_index(drop=True)


# ====================== resampling 清 outlier ======================
def bar_median_series(df: pd.DataFrame, value_col: str, freq: str) -> pd.DataFrame:
    """重采样成因果右沿 median bar，清掉瞬时尖峰。Resample into causal median bars.

    重采样到 freq 日历 bar，每个 bar 取 **median** 稳健吸收 bar 内瞬时尖峰；只保留有数据的
    bar，逐交易日分组、不跨隔夜。返回 [ts_et, date, <value_col>]。
    为什么用 median：单点不抗噪，取中位数能洗掉"突然跳一下又回来"的假尖峰，真实持续变动留得住。

    因果取点 (label='right', closed='right')：bar 标签 t 代表窗口 (t-bar, t] 的中位数，只用
    <= t 的数据 -> 不含未来，相邻 bar 算出的 return 也不含未来（避免 look-ahead 制造假显著）。
    Right-edge, right-closed bars: label t summarizes (t-bar, t], using only data <= t (causal).
    """
    cols = ["ts_et", "date", value_col]
    if df.empty:
        return pd.DataFrame(columns=cols)
    pieces = []
    for d, g in df.groupby("date"):
        s = (g.set_index("ts_et")[value_col]
               .resample(freq, label="right", closed="right").median().dropna())
        if len(s) == 0:
            continue
        piece = pd.DataFrame({"ts_et": s.index, value_col: s.values})
        piece["date"] = d
        pieces.append(piece[cols])
    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=cols)


# ====================== 因果取点构造（event/calendar 统一调这套，杜绝 look-ahead） ======================
def causal_bars(df: pd.DataFrame, value_col: str, freq: str) -> pd.DataFrame:
    """
    右边沿、闭右 的 median bar：bar 标签 t = 窗口 (t-bar, t] 的右端，代表值 = 该窗口中位数。
    => 代表值只用 ≤ t 的数据，因果、无"偷看未来"（修掉旧 event 模式 median 含 bar 内未来的问题）。
    只保留有数据的 bar，逐交易日分组、不跨隔夜。返回 [ts_et, date, value_col]。
    """
    cols = ["ts_et", "date", value_col]
    if df.empty:
        return pd.DataFrame(columns=cols)
    pieces = []
    for d, g in df.groupby("date"):
        s = (g.set_index("ts_et")[value_col]
               .resample(freq, label="right", closed="right").median().dropna())
        if len(s) == 0:
            continue
        piece = pd.DataFrame({"ts_et": s.index, value_col: s.values})
        piece["date"] = d
        pieces.append(piece[cols])
    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=cols)


def build_unified_xy(kalshi: pd.DataFrame, etf_tk: pd.DataFrame, freq: str):
    """
    统一因果构造（全项目 event/calendar 共用，保证两套唯一差别只剩"滞后怎么数"）：
      - 两边都用 causal_bars(右边沿 median)，同一 bar 大小，median-to-median 变化量；
      - x = Δprob，y = ETF log return，均为相邻 bar 相减、同日内、因果无 look-ahead。
    返回：
      al_cal : 完整钟表网格（平静 bar ffill 使 Δprob=0），列 dprob/etfret，用于 calendar(钟表滞后)
      act    : 只含 Kalshi 有成交的 bar（事件），相邻事件间变化 dprob_e/etfret_e，用于 event(事件滞后)
    """
    kb = causal_bars(kalshi, "prob", freq)
    eb = causal_bars(etf_tk, "mid", freq)
    if kb.empty or eb.empty:
        return None, None
    frames = []
    for d in sorted(set(kb["date"]).union(set(eb["date"]))):
        kd = kb[kb["date"] == d].set_index("ts_et")["prob"]
        ed = eb[eb["date"] == d].set_index("ts_et")["mid"]
        if kd.empty or ed.empty:
            continue
        start = min(kd.index.min(), ed.index.min())
        end   = max(kd.index.max(), ed.index.max())
        grid = pd.date_range(start, end, freq=freq)
        prob = kd.reindex(grid).ffill()
        mid  = ed.reindex(grid).ffill().bfill()
        active = kd.reindex(grid).notna().values
        df = pd.DataFrame({"ts_et": grid, "prob": prob.values, "mid": mid.values,
                           "active": active, "date": d}).dropna(subset=["prob", "mid"])
        if len(df) < 3:
            continue
        df["dprob"]  = df["prob"].diff()
        df["etfret"] = np.log(df["mid"]).diff()
        frames.append(df)
    if not frames:
        return None, None
    al = pd.concat(frames, ignore_index=True)
    al_cal = al.dropna(subset=["dprob", "etfret"]).copy()

    def per_day(g):
        g = g.sort_values("ts_et")
        g["dprob_e"]  = g["prob"].diff()
        g["etfret_e"] = np.log(g["mid"]).diff()
        return g
    act = (al[al["active"]].groupby("date", group_keys=False).apply(per_day)
             .dropna(subset=["dprob_e", "etfret_e"]).copy())
    return al_cal, act


# ====================== ETF 就近报价匹配（event 模式用） ======================
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


# ====================== 多重检验校正（BH-FDR，第④点） ======================
def add_fdr(df: pd.DataFrame, group_cols, pcol: str = "p_value", outcol: str = "p_fdr") -> pd.DataFrame:
    """对每个"一次回归"族（group_cols 标识，如同一 pair×bar 的所有滞后阶）做 Benjamini-Hochberg FDR 校正。
    Within each regression family (one pair×bar's lags), BH-FDR correct the p-values -> outcol.
    为什么：每个 pair×mode×lag 都检验一次，几百个检验里光靠运气就有一批 p<0.05；不校正会高估显著。"""
    from statsmodels.stats.multitest import multipletests
    df = df.copy()
    df[outcol] = np.nan
    for _, idx in df.groupby(list(group_cols)).groups.items():
        p = df.loc[idx, pcol].to_numpy(dtype=float)
        mask = np.isfinite(p)
        if mask.sum() == 0:
            continue
        corr = np.full(len(p), np.nan)
        corr[mask] = multipletests(p[mask], method="fdr_bh")[1]
        df.loc[idx, outcol] = corr
    return df


# ====================== 联合滞后回归引擎（两套模式共用） ======================
def run_joint_lag_regression(df_reg: pd.DataFrame, x_col: str, y_col: str,
                             k: int, min_obs: Optional[int] = None,
                             group_by_day: bool = False, y_lags: int = 0
                             ) -> Optional[pd.DataFrame]:
    """
    联合滞后回归：y_t = a + Σ_{j=-k..k} b_j·x_{t-j} [+ Σ_{i=1..p} φ_i·y_{t-i}] + 日固定效应 + ε

    - group_by_day=True：滞后用 groupby("date").shift，**不跨隔夜**（修 calendar 跨日 shift 污染）。
    - y_lags=p>0：把 y 自己的过去 p 期 y_{t-i} 放进来做控制（ADL/自相关控制，第8点）——
      这样 β_j 是**净掉 ETF 自身动量后**的领先，避免把"ETF 自相关"误算成"Kalshi 领先"。
    - 标准化 x（除以 std），系数可比；日固定效应 + 按日聚类标准误（单日退化 HC3）。
    - 额外返回 n_params（实际估计的参数个数，供算残差自由度）与 n_active（x≠0 的有效观测/事件数）。
    """
    df_reg = df_reg.copy()
    if min_obs is None:
        min_obs = 2 * k + 5

    if group_by_day:
        g = df_reg.groupby("date", group_keys=False)
        xshift = lambda j: g[x_col].shift(j)
        yshift = lambda i: g[y_col].shift(i)
    else:
        xshift = lambda j: df_reg[x_col].shift(j)
        yshift = lambda i: df_reg[y_col].shift(i)

    lag_cols = {}
    for j in range(-k, k + 1):
        col = f"lag_{j:+d}"
        df_reg[col] = xshift(j)
        lag_cols[j] = col
    all_lag_cols = list(lag_cols.values())

    ylag_cols = []
    for i in range(1, y_lags + 1):
        col = f"ylag_{i}"
        df_reg[col] = yshift(i)
        ylag_cols.append(col)

    df_reg = df_reg.dropna(subset=[y_col] + all_lag_cols + ylag_cols)
    if len(df_reg) < min_obs:
        return None

    x_std = df_reg[x_col].std()
    if x_std > 1e-12:
        for col in all_lag_cols:
            df_reg[col] = df_reg[col] / x_std

    day_dummies = pd.get_dummies(df_reg["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df_reg[all_lag_cols + ylag_cols].astype(float), day_dummies], axis=1))
    y = df_reg[y_col].astype(float)

    groups = df_reg["date"].values
    try:
        if len(np.unique(groups)) >= 2:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        else:
            model = sm.OLS(y, X).fit(cov_type="HC3")
    except Exception as e:
        print(f"  OLS 估计失败: {e}")
        return None

    rows = []
    n_obs_final = len(df_reg)
    n_days = df_reg["date"].nunique()
    n_params = int(X.shape[1])
    n_active = int((df_reg[x_col].abs() > 1e-12).sum())   # x≠0 的有效信息量（Kalshi 事件 bar 数）
    for j, col in lag_cols.items():
        if col not in model.params.index:
            continue
        direction = "kalshi_leads_etf" if j > 0 else ("etf_leads_kalshi" if j < 0 else "contemp")
        rows.append({
            "k_lag": j,
            "direction": direction,
            "coef": model.params[col],
            "t_stat": model.tvalues[col],
            "p_value": model.pvalues[col],
            "r_squared": model.rsquared,
            "n_obs": n_obs_final,
            "n_days": n_days,
            "n_params": n_params,
            "n_active": n_active,
        })
    return pd.DataFrame(rows)
