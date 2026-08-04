"""
leadlag_reliability.py
================================================================================
这个文件做什么 (What this file does)
  用「统计量本身」判定每对的可靠性，取代之前拍脑袋的"成交<50笔=稀疏"阈值。
  对每对算：有效观测数、残差自由度、系数中位标准误，并据此分四档。
  Judge each pair's reliability from statistics (effective N, residual degrees of
  freedom, median coefficient SE) instead of an arbitrary trade-count cutoff.

为什么这么做 (Why)
  "数据少到多少才有统计问题"没有一个固定笔数答案；真正的临界是**观测数逼近参数个数
  （自由度→0）**：此时要么回归估不出来，要么标准误爆炸、置信区间极宽，推断不可信。
  低自由度时甚至可能蹦出**虚假的小 p**（过拟合 + SE 本身估不准），所以判据用自由度/标准误，
  不能只看 p。
  There is no magic trade count; the real threshold is when N approaches the number
  of parameters (df→0): the regression either cannot run or has exploding SEs. Very
  low df can even produce spurious small p-values, so we判 by df/SE, not p alone.

思路 (Approach)
  完整盘内网格后 n_obs 很大、df 失真，所以**按 n_active = x≠0 的有效观测(Kalshi 事件 bar 数)**
  定档——那才是真正能识别 β 的样本量。同时报告 df / medSE 供参考。
  取 calendar 与 event 中 n_active 更高者定档：
    无法估计 / 极低(<15) / 偏少(15-40) / 充足(>=40)。显著性 sig 用 BH-FDR 校正后的 p_fdr。

输出 (Outputs)
  - leadlag_reliability.csv     每对一行的可靠性明细
  存放位置：leadlag/pipeline/ 下
  - 另导出 get_reliability(ticker, etf) 供 make_pair_text 在文字页嵌入「数据可靠性」与「图的问题」

函数 (Functions)
  _one_mode_stats   从某模式的系数行算 (n_obs,n_days,K,nparam,df,medSE,ran,n_sig)
  classify          按更高自由度定四档（中英标签）
  figure_caveats    据档位/天数生成"图会有什么问题"的逐条说明
  get_reliability   返回某对的可靠性 dict（被 make_pair_text import）
  build_table/main  为 48 对生成可靠性表并落盘
"""
import numpy as np
import pandas as pd

import leadlag_common as C

OUT_CSV = C.HERE / "leadlag_reliability.csv"
_SIG = pd.read_csv(C.SIG_PAIRS_CSV)
_CAL = pd.read_csv(C.HERE / "leadlag_calendar_kalshi_etf.csv")
_CAL = _CAL[_CAL["is_primary_bar"]]
_EV  = pd.read_csv(C.HERE / "leadlag_event_kalshi_etf.csv")

# 分档门槛：按 n_active = x≠0 的有效观测数（= Kalshi 事件 bar 数）。
# 为什么不用 df：calendar 改完整盘内网格后 n_obs 很大、df 也大，但真正能识别 β 的信息量
# 只有"非平静"的那几个 bar；所以用 n_active 当有效样本量更诚实。
ACT_VERYLOW = 15    # < 15：有效事件太少，推断不可信
ACT_LOW     = 40    # 15-39：偏少；>=40：充足

TIER_CANNOT  = "Cannot-estimate"
TIER_VERYLOW = "Very-low-info"
TIER_LOW     = "Low-info"
TIER_OK      = "Adequate"


def _one_mode_stats(df):
    """从某模式（calendar 主bar 或 event）的系数行算可靠性统计。
    Compute reliability stats from one mode's coefficient rows. None=该模式没跑出来。"""
    if df is None or df.empty:
        return None
    n_obs  = int(df["n_obs"].iloc[0])
    n_days = int(df["n_days"].iloc[0])
    K      = int((len(df) - 1) // 2)                      # 滞后阶数（行数 = 2K+1）
    nparam = int(df["n_params"].iloc[0]) if "n_params" in df.columns else (2 * K + 1) + (n_days - 1) + 1
    # n_active = x≠0 的有效观测（Kalshi 事件 bar 数）——真正的识别样本量
    n_active = int(df["n_active"].iloc[0]) if "n_active" in df.columns else n_obs
    rdf    = n_obs - nparam
    se     = (df["coef"].abs() / df["t_stat"].abs().replace(0, np.nan))
    pcol   = "p_fdr" if "p_fdr" in df.columns else "p_value"   # ④ 显著性用 FDR 校正后
    n_sig  = int((df[pcol] < 0.05).sum())
    return {"n_obs": n_obs, "n_days": n_days, "K": K, "nparam": nparam, "n_active": n_active,
            "df": int(rdf), "medSE": float(se.median()), "n_sig": n_sig}


def classify(cal, ev):
    """按 calendar/event 中有效事件数(n_active)更高者定四档。Tier by the higher n_active。"""
    cands = [m for m in (cal, ev) if m is not None]
    if not cands:
        return TIER_CANNOT, None
    best = max(cands, key=lambda m: m["n_active"])
    if best["n_active"] < ACT_VERYLOW:
        return TIER_VERYLOW, best
    if best["n_active"] < ACT_LOW:
        return TIER_LOW, best
    return TIER_OK, best


def figure_caveats(tier, cal, ev):
    """据档位/有效事件数生成"图会有什么问题"的逐条说明（图照画，但问题写清楚）。"""
    cv = []
    best = next((m for m in (cal, ev) if m is not None), None)
    nact = best["n_active"] if best else 0
    if tier == TIER_CANNOT:
        cv.append("Regression cannot be estimated: the lag-coefficient plot (B) shows 'no regression "
                  "result'; only the time-series / zoom plots are descriptive.")
        cv.append("Long flat Kalshi segments = NO TRADE in that span (not 'probability unchanged'); "
                  "do not read lead direction from them.")
        cv.append("Too few active bars: the red/blue lead shading in zoom2/segments and the K#/E# "
                  "pairing in leadglance are illustrative only, with no statistical meaning.")
        return cv
    if tier == TIER_VERYLOW:
        cv.append(f"Very low info (only {nact} bars with an actual Kalshi move, < {ACT_VERYLOW}): even "
                  f"'significant' coefficients are untrustworthy (huge SE, possibly spurious significance).")
        cv.append("Most of the chart is flat no-trade lines; only a handful of bars carry real variation, "
                  "so the lead calls in leadglance/segments are not robust.")
        return cv
    if tier == TIER_LOW:
        cv.append(f"Low info ({ACT_VERYLOW}<= active bars <{ACT_LOW}): direction is indicative but imprecise; "
                  f"do not over-interpret any single coefficient.")
        return cv
    cv.append("Adequate info: figures and regression are mutually readable; note that flat Kalshi segments "
              "still mean 'no trade', not 'no change'.")
    return cv


def get_reliability(ticker, etf):
    """返回某对的可靠性 dict（供 make_pair_text 嵌入）。Reliability dict for one pair。"""
    cal = _one_mode_stats(_CAL[(_CAL.contract_ticker == ticker) & (_CAL.etf == etf)])
    ev  = _one_mode_stats(_EV[(_EV.contract_ticker == ticker) & (_EV.etf == etf)])
    tier, best = classify(cal, ev)
    return {"tier": tier, "cal": cal, "ev": ev, "best": best,
            "fig_caveats": figure_caveats(tier, cal, ev)}


def build_table():
    rows = []
    for _, p in _SIG.iterrows():
        tk, etf = p["contract_ticker"], p["etf"]
        r = get_reliability(tk, etf)
        b = r["best"] or {}
        rows.append({
            "contract_ticker": tk, "etf": etf, "tier": r["tier"],
            "cal_n_obs": (r["cal"] or {}).get("n_obs"), "cal_n_active": (r["cal"] or {}).get("n_active"),
            "cal_df": (r["cal"] or {}).get("df"), "cal_medSE": (r["cal"] or {}).get("medSE"),
            "ev_n_obs": (r["ev"] or {}).get("n_obs"), "ev_n_active": (r["ev"] or {}).get("n_active"),
            "ev_df": (r["ev"] or {}).get("df"),
            "best_n_active": b.get("n_active"), "best_df": b.get("df"), "best_medSE": b.get("medSE"),
        })
    return pd.DataFrame(rows)


def main():
    df = build_table()
    df.to_csv(OUT_CSV, index=False)
    print(f"可靠性分档完成：{len(df)} 对 -> {OUT_CSV.name}")
    print(df["tier"].value_counts().to_string())


if __name__ == "__main__":
    main()
