"""
leadlag_coarse_freq.py
================================================================================
这个文件做什么 (What this file does)
  粗频率稳健性检查：对全部 48 对，额外用 30min / 60min 粗 bar 重跑 calendar 回归，
  看"换低频会不会有结果 / 方向会不会变"。
  Coarse-frequency robustness: re-run the calendar regression at 30min / 60min
  bars for all 48 pairs, to test whether lower frequency yields results or flips
  the lead direction.

为什么这么做 (Why)
  回答疑问"是不是没试过低频才没结果"。结论可预期：① 充足组在粗 bar 下观测变少、
  但可看方向是否稳健；② 稀疏组 bar 越粗、观测越少，更估不出来——证明它们没结果是
  数据量问题，不是频率没试到。按"天"不做：多数合约窗口仅 2-4 周，日 bar 自由度不足。
  Answers "did we just not try low frequency?". Expected: adequate pairs lose obs
  but let us check direction stability; sparse pairs get even fewer obs and still
  cannot estimate — confirming it is a data-quantity problem, not a frequency gap.
  Daily is skipped: most windows are 2-4 weeks, too few days for the lags + day-FE.

思路 (Approach)
  复用 calendar 口径：median 右沿 bar（common.bar_median_series）-> 同日变化量
  -> 内连对齐 -> choose_k -> 联合滞后回归。每对每频率出一行汇总（不逐滞后展开）。

输出 (Output)
  leadlag_coarse_freq.csv —— 每行 = 一个 pair × 一个粗频率(30min/60min) 的汇总
  字段：ran(能否估计)、n_obs、n_days、K、df、n_sig、kpos(Kalshi 领先显著数)、
        kneg(ETF 领先显著数)、lean(倾向)
  存放位置：leadlag/pipeline/ 下
  另导出 get_coarse(ticker, etf) 供 make_pair_text 嵌入「粗频率稳健性」一节。

函数 (Functions)
  run_pair_freq  对某对某频率跑一次 calendar 回归，返回汇总 dict
  build_table    遍历 48 对 × {30min,60min}
  get_coarse     返回某对两频率的汇总（被 make_pair_text import）
  main           生成表并落盘
"""
import numpy as np
import pandas as pd

import leadlag_common as C
from leadlag_calendar_time import bar_change

OUT_CSV = C.HERE / "leadlag_coarse_freq.csv"
COARSE_FREQS = ["30min", "60min"]
MIN_BARS = 2 * 3 + 5     # 最小 K=3 所需观测下限（与 calendar 一致）

_SIG = pd.read_csv(C.SIG_PAIRS_CSV)
_TABLE = None            # 懒加载缓存（get_coarse 用）


def run_pair_freq(kalshi, etf_tk, freq):
    """对某对某粗频率跑一次 calendar 回归，返回汇总 dict。One coarse-bar calendar fit -> summary."""
    base = {"freq": freq, "ran": False, "n_obs": 0, "n_days": 0, "K": np.nan,
            "df": np.nan, "n_sig": 0, "kpos": 0, "kneg": 0, "lean": "not-estimable"}
    kb = bar_change(kalshi, "prob", "x", freq, "kalshi")
    eb = bar_change(etf_tk, "mid",  "y", freq, "etf")
    if kb.empty or eb.empty:
        return base
    m = pd.merge(kb[["ts_et", "x", "date"]], eb[["ts_et", "y"]], on="ts_et", how="inner")
    n_active = len(m)
    if n_active < MIN_BARS:
        base["n_obs"] = n_active
        return base
    k = C.choose_k(n_active)
    res = C.run_joint_lag_regression(m, x_col="x", y_col="y", k=k)
    if res is None or res.empty:
        base["n_obs"] = n_active
        return base
    n_obs  = int(res["n_obs"].iloc[0]); n_days = int(res["n_days"].iloc[0])
    nparam = (2 * k + 1) + (n_days - 1) + 1
    sig = res[res["p_value"] < 0.05]
    kpos, kneg = int((sig.k_lag > 0).sum()), int((sig.k_lag < 0).sum())
    lean = "Kalshi-leads" if kpos > kneg else ("ETF-leads" if kneg > kpos else
            ("Balanced/mixed" if kpos > 0 else "No-sig"))
    base.update({"ran": True, "n_obs": n_obs, "n_days": n_days, "K": k,
                 "df": n_obs - nparam, "n_sig": len(sig), "kpos": kpos,
                 "kneg": kneg, "lean": lean})
    return base


def build_table():
    con = C.make_con()
    rows = []
    for i, p in _SIG.iterrows():
        tk, etf = p["contract_ticker"], p["etf"]
        ds, de = str(p["date_start"]), str(p["date_end"])
        kalshi = C.load_kalshi(con, tk, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        for freq in COARSE_FREQS:
            if kalshi.empty or etf_tk.empty:
                r = {"freq": freq, "ran": False, "n_obs": 0, "n_days": 0, "K": np.nan,
                     "df": np.nan, "n_sig": 0, "kpos": 0, "kneg": 0, "lean": "no-data"}
            else:
                r = run_pair_freq(kalshi, etf_tk, freq)
            r["contract_ticker"] = tk; r["etf"] = etf
            rows.append(r)
        print(f"[{i+1}/{len(_SIG)}] {tk}×{etf}  done")
    return pd.DataFrame(rows)


def get_coarse(ticker, etf):
    """返回某对在各粗频率下的汇总行（懒加载 CSV）。Coarse-freq summary rows for one pair."""
    global _TABLE
    if _TABLE is None:
        _TABLE = pd.read_csv(OUT_CSV) if OUT_CSV.exists() else pd.DataFrame()
    if _TABLE.empty:
        return []
    d = _TABLE[(_TABLE.contract_ticker == ticker) & (_TABLE.etf == etf)]
    return d.to_dict("records")


def main():
    df = build_table()
    cols = ["contract_ticker", "etf", "freq", "ran", "n_obs", "n_days", "K", "df",
            "n_sig", "kpos", "kneg", "lean"]
    df = df[cols]
    df.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}")
    for freq in COARSE_FREQS:
        d = df[df.freq == freq]
        ran = int(d["ran"].sum())
        print(f"{freq}: 能估计 {ran}/{len(d)}  显著系数合计 {int(d['n_sig'].sum())}  "
              f"Kalshi领先 {int(d['kpos'].sum())} / ETF领先 {int(d['kneg'].sum())}")


if __name__ == "__main__":
    main()
