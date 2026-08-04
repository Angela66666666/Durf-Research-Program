"""
leadlag_common.py
================================================================================
这个文件做什么 (What this file does)
  Lead-Lag 流水线的「共享底座」：时区转换、盘内过滤、outlier 清洗、bar/K 选择、
  数据加载、因果取点构造、联合滞后回归引擎、以及标准 Granger 联合因果检验引擎，
  全部集中在这一个模块里。calendar / event / probit / classification / granger 等脚本都 import 它。
  The shared core of the lead-lag pipeline: timezone conversion, market-hours
  filtering, outlier cleaning, bar/K selection, data loading, causal bar
  construction, the joint-lag regression engine, and the standard Granger joint
  causality engine — imported by every script.

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
  causal_bars            重采样成因果右沿 median bar（清 outlier 的核心，全项目统一调这套）
  build_unified_xy       两边同口径因果构造，产出 calendar 网格 + event 活跃序列
  lookup_etf_mid         向后匹配最近 ETF 报价（只取 <= query 的报价，因果无 look-ahead；event 模式用）
  add_fdr                在每个"一次回归"族内做 BH-FDR 多重检验校正
  choose_adl_order       ETF 自滞后阶 BIC 自选（供联合回归与 Granger 共用）
  run_joint_lag_regression  联合滞后回归引擎（逐系数报告口径，两套模式共用）
  run_granger_direction  标准 Granger 单向检验：单向回归 + cause 滞后块联合 Wald（hac-panel SE）
  run_granger_probit     probit 版 Granger（ETF 涨/跌方向，对 forward Δprob 系数做联合 Wald）
"""
from __future__ import annotations
import datetime as _dt
import re
from pathlib import Path
from typing import Optional, Tuple

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm

# ====================== 全局数据口径（统一配置，改这里即全局生效） ======================
HERE          = Path(__file__).parent
# 向上找到含 "1. data" 的目录作为项目根，脚本放在任何深度都能跑
PROJ_ROOT     = HERE
while PROJ_ROOT != PROJ_ROOT.parent and not (PROJ_ROOT / "1. data").is_dir():
    PROJ_ROOT = PROJ_ROOT.parent
DATA_DIR      = PROJ_ROOT / "1. data"
ETF_HF_DIR    = DATA_DIR / "etf_hf"
SIG_PAIRS_CSV = PROJ_ROOT / "3. daily screen" / "significant_pairs.csv"
# 注意：用 trades_*.parquet 精确匹配，排除 macOS 在 exFAT 卷上生成的 ._trades_*.parquet 垃圾文件
TRADES_GLOB   = str((DATA_DIR / "kalshi" / "kalshi" / "trades" / "trades_*.parquet").resolve())

TZ            = "America/New_York"   # 全项目唯一时区
MARKET_OPEN   = _dt.time(9, 30, 0)   # 正规盘开盘 09:30 ET
MARKET_CLOSE  = _dt.time(16, 0, 0)   # 正规盘收盘 16:00 ET（左闭右开）

# outlier 处理：不用任何 σ/绝对阈值或 Hampel 逐点删除；改用 resampling。
# Outliers handled by resampling, not point-deletion — see causal_bars():
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


_MON = {"JAN": "Jan", "FEB": "Feb", "MAR": "Mar", "APR": "Apr", "MAY": "May", "JUN": "Jun",
        "JUL": "Jul", "AUG": "Aug", "SEP": "Sep", "OCT": "Oct", "NOV": "Nov", "DEC": "Dec"}


def short_contract_name(ticker: str) -> str:
    """把 Kalshi ticker 压成人能读的短名，用于图/报告的标签。

    读者看到 'KXECKH276' 毫无信息量；'Harris 276 EV' 一眼就懂。全项目共用这一套映射，
    保证图、表、报告里同一合约叫同一个名字。无法识别的 ticker 原样返回。
    """
    t = str(ticker).strip()
    s = t[2:] if t.startswith("KX") else t          # KX 只是交易所前缀，不携带信息

    m = re.fullmatch(r"ECKH(\d+)", s)
    if m:
        return f"Harris {m.group(1)} EV"
    m = re.fullmatch(r"ECDJT(\d+)", s)
    if m:
        return f"Trump {m.group(1)} EV"
    m = re.fullmatch(r"538APPROVE(MAX|MIN)-\d{2}([A-Z]{3})(\d{2})-T(\d+)", s)
    if m:
        rel = ">" if m.group(1) == "MAX" else "<"
        return f"Approval {rel}{m.group(4)}% by {_MON.get(m.group(2), m.group(2))}{m.group(3)}"
    m = re.fullmatch(r"AAAGASM-\d{2}([A-Z]{3})(\d{2})-US-([\d.]+)", s)
    if m:
        return f"Gas >${m.group(3)} by {_MON.get(m.group(1), m.group(1))}{m.group(2)}"
    m = re.fullmatch(r"RATECUT-(\d{2})([A-Z]{3})\d{2}", s)
    if m:
        # ticker 里的日是 FOMC 会议日，合约标题写的是"before 次日"，标签只到月，避免断言错日期
        return f"Fed cut by {_MON.get(m.group(2), m.group(2))}-{m.group(1)}"
    m = re.fullmatch(r"FEDDECISION-(\d{2})([A-Z]{3})-([CH])(\d+)", s)
    if m:
        act = "cut" if m.group(3) == "C" else "hold"
        return f"Fed {_MON.get(m.group(2), m.group(2))}-{m.group(1)} {act} {m.group(4)}bp"
    return t


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
    # 同一交易日内差分，不跨隔夜（保留每天第一笔：其 prob_change=NaN，但 prob 是真实开盘概率状态，
    # 下游 causal_bars 会重新按 bar 算 dprob，这里不能把第一笔删掉，否则每天第一根 bar 丢首 tick）
    df["prob_change"] = df.groupby("date")["prob"].diff()
    return df.reset_index(drop=True)


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


# ====================== resampling 清 outlier + 因果取点构造（全项目统一调这套，杜绝 look-ahead） ======================
def causal_bars(df: pd.DataFrame, value_col: str, freq: str) -> pd.DataFrame:
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
        mid  = ed.reindex(grid).ffill()   # 只用过去报价 ffill；不 bfill（bfill 会用未来 mid 回填开头，look-ahead）
                                          # 当天首个 ETF 报价之前的网格行 mid=NaN，由下面 dropna 自然删掉
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

    # 活跃事件子序列：同日内相邻事件的 Δprob / ETF log return（向量化，不跨隔夜）
    act = al[al["active"]].sort_values(["date", "ts_et"]).copy()
    act["dprob_e"]  = act.groupby("date")["prob"].diff()
    act["etfret_e"] = np.log(act["mid"]) - np.log(act.groupby("date")["mid"].shift(1))
    act = act.dropna(subset=["dprob_e", "etfret_e"]).copy()
    return al_cal, act


# ============ ETF 向后匹配最近报价（只取 <= query 的报价，因果无 look-ahead；event 模式用） ============
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


# ====================== ADL 自滞后阶选择（BIC） ======================
ADL_PMAX = 6   # ETF 自滞后阶 BIC 自选的上限（再受 K 与自由度约束）


def choose_adl_order(y, lagX, ylagX_full, fe_dummies, pmax):
    """在固定公共样本上，用 BIC 选 ETF 自滞后阶 p∈[0, pmax]。
      - y: 因变量(Series)；lagX: x 滞后设计阵；ylagX_full: ylag_1..pmax；fe_dummies: 日/成员固定效应。
      - 每个候选 p 用普通 OLS 的 BIC（BIC 由 loglik 决定，与是否稳健 cov 无关），取最小 BIC。
      - BIC 惩罚重、是真实阶数的一致估计，且小样本下倾向精简 —— 既省自由度又有依据。
    返回选中的阶数 p*。"""
    best_p, best_bic = 0, np.inf
    for p in range(0, pmax + 1):
        parts = [lagX]
        if p > 0:
            parts.append(ylagX_full.iloc[:, :p])
        if fe_dummies is not None and fe_dummies.shape[1] > 0:
            parts.append(fe_dummies)
        X = sm.add_constant(pd.concat(parts, axis=1).astype(float))
        try:
            m = sm.OLS(y.astype(float), X).fit()
        except Exception:
            continue
        if np.isfinite(m.bic) and m.bic < best_bic:
            best_bic, best_p = m.bic, p
    return best_p


# ====================== 联合滞后回归引擎（两套模式共用） ======================
def run_joint_lag_regression(df_reg: pd.DataFrame, x_col: str, y_col: str,
                             k: int, min_obs: Optional[int] = None,
                             group_by_day: bool = False, y_lags=0
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

    # --- ADL 自滞后阶：y_lags 为 int 则直接用；为 "auto" 则在公共样本上用 BIC 选阶 ---
    if isinstance(y_lags, str) and y_lags.lower() == "auto":
        pmax = max(0, min(k, ADL_PMAX))
        yl_full = {f"ylag_{i}": yshift(i) for i in range(1, pmax + 1)}
        ytmp = pd.DataFrame(yl_full, index=df_reg.index)
        common = df_reg.assign(**{c: ytmp[c] for c in ytmp.columns})
        common = common.dropna(subset=[y_col] + all_lag_cols + list(ytmp.columns))
        if pmax > 0 and len(common) >= min_obs:
            lagX = common[all_lag_cols].astype(float)
            xs0 = common[x_col].std()
            if xs0 > 1e-12:
                lagX = lagX / xs0
            fe = pd.get_dummies(common["date"], prefix="d", drop_first=True, dtype=float) if group_by_day else None
            y_lags = choose_adl_order(common[y_col], lagX, common[list(ytmp.columns)].astype(float), fe, pmax)
        else:
            y_lags = 0

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
            "n_ylags": int(y_lags),
        })
    return pd.DataFrame(rows)


# ====================== 标准 Granger 联合检验（单向回归 + Wald block 检验） ======================
def run_granger_direction(df_reg: pd.DataFrame, cause_col: str, effect_col: str,
                          k: int, group_by_day: bool = False, own_lags="auto",
                          return_coefs: bool = False,
                          min_obs: Optional[int] = None) -> Optional[dict]:
    """标准 Granger 单向因果检验（一个方向 = 一条回归 + 一个联合 Wald，给一个 p 值）：

        effect_t = a + Σ_{i=1..p} φ_i·effect_{t-i}     ← 被解释变量自身的过去(p 由 BIC 选)
                     + Σ_{j=1..k} b_j·cause_{t-j}        ← 只放「解释变量的过去」
                     + 日固定效应 + ε                    ← 按日聚类稳健 SE(单日退化 HC3)
        H0: b_1 = b_2 = … = b_k = 0   ⟺  「cause 不 Granger-导致 effect」

    与项目里「对称大方程数系数」的关键区别（这才是教科书 Granger）：
      - 只放 cause 的**过去**(j≥1)，剔除同期 j=0(瞬时相关,判不了方向)与未来 j<0(那是反方向)；
      - 用一个 **Wald 联合检验**取代逐系数计数——聚类稳健协方差自动带入，因非同方差用 χ² 形式
        而非基于 RSS 的普通 F；
      - 反方向只需把 cause/effect 对调再调用一次(effect 换成 cause 自身也配 BIC 自滞后)。

    返回一行 dict：wald_chi2 / wald_df / p_value / n_ylags(=p) / K / n_obs / n_days / n_active。
    样本不足或估计失败返回 None。"""
    df_reg = df_reg.copy()
    if min_obs is None:
        min_obs = 2 * k + 5

    if group_by_day:
        g = df_reg.groupby("date", group_keys=False)
        cshift = lambda j: g[cause_col].shift(j)
        eshift = lambda i: g[effect_col].shift(i)
    else:
        cshift = lambda j: df_reg[cause_col].shift(j)
        eshift = lambda i: df_reg[effect_col].shift(i)

    # 解释变量的过去 1..k（被联合检验的 block）
    cause_cols = []
    for j in range(1, k + 1):
        col = f"causelag_{j}"
        df_reg[col] = cshift(j)
        cause_cols.append(col)

    # 被解释变量自身过去阶数：BIC 自选("auto")，或指定 int
    pmax = max(0, min(k, ADL_PMAX))
    if isinstance(own_lags, str) and own_lags.lower() == "auto":
        el_full = {f"efflag_{i}": eshift(i) for i in range(1, pmax + 1)}
        etmp = pd.DataFrame(el_full, index=df_reg.index)
        common = df_reg.assign(**{c: etmp[c] for c in etmp.columns})
        common = common.dropna(subset=[effect_col] + cause_cols + list(etmp.columns))
        if pmax > 0 and len(common) >= min_obs:
            causeX = common[cause_cols].astype(float)
            cs0 = common[cause_col].std()
            if cs0 > 1e-12:
                causeX = causeX / cs0
            fe = pd.get_dummies(common["date"], prefix="d", drop_first=True, dtype=float) if group_by_day else None
            p = choose_adl_order(common[effect_col], causeX, common[list(etmp.columns)].astype(float), fe, pmax)
        else:
            p = 0
    else:
        p = int(own_lags)

    eff_cols = []
    for i in range(1, p + 1):
        col = f"efflag_{i}"
        df_reg[col] = eshift(i)
        eff_cols.append(col)

    df_reg = df_reg.dropna(subset=[effect_col] + cause_cols + eff_cols)
    if len(df_reg) < min_obs:
        return None

    # 标准化 cause（不改变联合检验 p，只让单系数可比、条件数更好）
    cs = df_reg[cause_col].std()
    if cs > 1e-12:
        for col in cause_cols:
            df_reg[col] = df_reg[col] / cs

    df_reg = df_reg.sort_values("date", kind="stable")
    day_dummies = pd.get_dummies(df_reg["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df_reg[cause_cols + eff_cols].astype(float), day_dummies], axis=1))
    y = df_reg[effect_col].astype(float)
    # 标准误：panel Newey-West HAC(带宽=k, 按交易日分组)，不用按日聚类。原因(见 GRANGER_TEST.md)：
    #   事件合约常只有 1~几天数据，按日聚类的稳健协方差**秩 ≤ 天数**，联合检验 K 个约束时
    #   当 K≥天数就秩亏 → Wald χ²/p 失效(会算出 p=0、1e-200 之类的假显著)。
    #   hac-panel 满秩(单日/少数天都成立)，且在**每个交易日块内**算 Newey-West、不跨隔夜串扰，
    #   是高频日内 lead-lag 的微观结构标准协方差。日固定效应仍保留；滞后仍按日 shift 不跨隔夜。
    maxlags = max(1, k)
    groups = pd.factorize(df_reg["date"])[0]
    try:
        model = sm.OLS(y, X).fit(cov_type="hac-panel",
                                 cov_kwds={"groups": groups, "maxlags": maxlags})
    except Exception as e:
        print(f"  Granger OLS 失败: {e}")
        return None

    # Wald 联合检验：cause 的 k 个滞后系数同时为 0（用稳健/聚类协方差，χ² 形式）
    names = list(X.columns)
    R = np.zeros((len(cause_cols), len(names)))
    for r, c in enumerate(cause_cols):
        R[r, names.index(c)] = 1.0
    try:
        wt = model.wald_test(R, scalar=True, use_f=False)
        chi2 = float(np.squeeze(wt.statistic))
        pval = float(np.squeeze(wt.pvalue))
    except Exception as e:
        print(f"  Wald 失败: {e}")
        return None

    out = {
        "K": k, "wald_df": len(cause_cols), "n_ylags": p,
        "wald_chi2": chi2, "p_value": pval,
        "n_obs": int(len(df_reg)), "n_days": int(df_reg["date"].nunique()),
        "n_params": int(X.shape[1]),
        "n_active": int((df_reg[cause_col].abs() > 1e-12).sum()),
        "cov_type": "hac-panel",   # linear 无退回：hac-panel 失败直接返回 None，故恒为 hac-panel
    }
    if return_coefs:
        # 被联合检验的 cause 过去滞后系数 + 各自 hac-panel p。
        # coefs: cause 已除以自身 std -> "每 1 SD cause 的 effect 反应"。
        # beta : 再除以 effect 的 std -> 全标准化系数(无量纲)，可跨 pair 比较。
        sy = float(df_reg[effect_col].std())
        out["lags"] = list(range(1, k + 1))
        out["coefs"] = [float(model.params[c]) for c in cause_cols]
        out["beta"] = [float(model.params[c]) / sy if sy > 1e-12 else float("nan") for c in cause_cols]
        out["coef_p"] = [float(model.pvalues[c]) for c in cause_cols]
    return out


def run_granger_probit(df_reg: pd.DataFrame, x_col: str, y_col: str, k: int,
                       group_by_day: bool = False, own_lags="auto",
                       min_obs: Optional[int] = None, return_coefs: bool = False) -> Optional[dict]:
    """probit 版 Granger（方向只做 Kalshi→ETF，被解释变量是「ETF 涨/跌」离散方向）：

        Pr(up_t=1) = Φ( α + Σ_{i=1..p} φ_i·up_{t-i}   ← ETF 自身方向的过去(p 由 probit-BIC 选)
                          + Σ_{j=1..k} b_j·x_{t-j} )    ← 只放「过去的 Δprob」
        H0: b_1 = … = b_k = 0  ——「过去的 Kalshi 变化不 Granger-预测 ETF 方向」。

    这是老师说的「direction-only probit 的联合检验对应版」：对 forward Δprob 那组系数做一个
    联合 Wald(hac-panel 面板 Newey-West，按日分组，满秩)。up=1[y>0]，剔除 y==0 的 bar。
    返回一行 dict：wald_chi2 / wald_df / p_value / n_ylags / K / n_obs / n_days / n_active。"""
    # 最小样本量由模型参数个数推出（与 run_granger_direction 同一套规则），不用主观的固定 30：
    # 需要 k 个 cause 滞后 + 若干自身滞后 + 截距，2k+5 给出足够的剩余自由度。
    if min_obs is None:
        min_obs = 2 * k + 5
    df = df_reg.dropna(subset=[x_col, y_col]).copy()
    df = df[df[y_col] != 0.0]
    if len(df) < min_obs or df[x_col].std() < 1e-12:
        return None
    df["up"] = (df[y_col] > 0).astype(int)

    if group_by_day:
        g = df.groupby("date", group_keys=False)
        xshift = lambda j: g[x_col].shift(j)
        ushift = lambda i: g["up"].shift(i)
    else:
        xshift = lambda j: df[x_col].shift(j)
        ushift = lambda i: df["up"].shift(i)

    xstd = df[x_col].std()
    cause_cols = []
    for j in range(1, k + 1):
        col = f"causelag_{j}"
        df[col] = xshift(j) / xstd
        cause_cols.append(col)

    pmax = max(0, min(k, ADL_PMAX))
    up_full = {f"uplag_{i}": ushift(i) for i in range(1, pmax + 1)}
    utmp = pd.DataFrame(up_full, index=df.index)
    common = df.assign(**{c: utmp[c] for c in utmp.columns})
    common = common.dropna(subset=["up"] + cause_cols + list(utmp.columns))
    if len(common) < min_obs or common["up"].nunique() < 2:
        return None

    # 自身方向滞后阶：probit-BIC 自选（"auto"）或指定 int
    if isinstance(own_lags, str) and own_lags.lower() == "auto":
        best_p, best_bic = 0, np.inf
        for p in range(0, pmax + 1):
            cols = cause_cols + [f"uplag_{i}" for i in range(1, p + 1)]
            Xc = sm.add_constant(common[cols].astype(float))
            try:
                mp = sm.Probit(common["up"].astype(float), Xc).fit(disp=0, maxiter=200)
            except Exception:
                continue
            if np.isfinite(mp.bic) and mp.bic < best_bic:
                best_bic, best_p = mp.bic, p
        p = best_p
    else:
        p = int(own_lags)

    use_cols = cause_cols + [f"uplag_{i}" for i in range(1, p + 1)]
    fit_df = common.dropna(subset=["up"] + use_cols).sort_values("date", kind="stable")
    if len(fit_df) < min_obs or fit_df["up"].nunique() < 2:
        return None
    X = sm.add_constant(fit_df[use_cols].astype(float))
    yv = fit_df["up"].astype(float)
    grp = pd.factorize(fit_df["date"])[0]
    try:
        try:
            model = sm.Probit(yv, X).fit(disp=0, maxiter=200, cov_type="hac-panel",
                                         cov_kwds={"groups": grp, "maxlags": max(1, k)})
            cov_used = "hac-panel"
        except Exception:
            model = sm.Probit(yv, X).fit(disp=0, maxiter=200)
            cov_used = "default"   # hac-panel 失败退回普通标准误，记录下来供事后甄别
    except Exception:
        return None

    names = list(X.columns)
    R = np.zeros((len(cause_cols), len(names)))
    for r, c in enumerate(cause_cols):
        R[r, names.index(c)] = 1.0
    try:
        wt = model.wald_test(R, scalar=True, use_f=False)
        chi2 = float(np.squeeze(wt.statistic))
        pval = float(np.squeeze(wt.pvalue))
    except Exception:
        return None

    out = {
        "K": k, "wald_df": len(cause_cols), "n_ylags": p,
        "wald_chi2": chi2, "p_value": pval,
        "n_obs": int(len(fit_df)), "n_days": int(fit_df["date"].nunique()),
        "n_params": int(X.shape[1]),
        "n_active": int((fit_df[cause_cols[0]].abs() > 1e-12).sum()) if cause_cols else 0,
        "cov_type": cov_used,
    }
    if return_coefs:
        # probit 系数在潜变量(probit-index)尺度、每 1 SD Δprob；跨 pair 在 probit 内部可比。
        out["lags"] = list(range(1, k + 1))
        out["coefs"] = [float(model.params[c]) for c in cause_cols]
        out["beta"] = list(out["coefs"])   # probit 无 y 方差可除，直接用 index-系数
        out["coef_p"] = [float(model.pvalues[c]) for c in cause_cols]
    return out
