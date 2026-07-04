"""
leadlag_granger.py
================================================================================
这个文件做什么 (What this file does)
  标准 Granger 联合因果检验（headline 统计量），与 calendar/event/probit 平级。
  对每个 pair，跑三套「一条单向回归 + 一个联合 Wald」的检验：
    linear·Kalshi→ETF :  etfret_t = a + Σφ·etfret_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j} + 日FE
    linear·ETF→Kalshi :  Δprob_t  = c + Σψ·Δprob_{t-i}  + Σ_{j=1..K} d_j·etfret_{t-j} + 日FE
    probit·Kalshi→ETF :  Pr(ETF↑_t)=Φ(α + Σφ·↑_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j})
  linear 两个模式(calendar/event)各双向；probit 每个模式仅 Kalshi→ETF(因变量是离散涨跌)。
  各检验 H0: 那组 cause 滞后系数同时为 0 → 一个 p 值。

为什么这么做 (Why)
  取代旧 pipeline「对称大方程逐系数数显著个数」：只放 cause 的**过去**(剔除同期/未来)，
  一个方向一个联合 Wald(面板 Newey-West / hac-panel，满秩、对单日事件也有效)取代 2K+1 个
  t 检验的多重检验散点。差分序列天然平稳 → VAR-式 Granger，无需协整。见 GRANGER_TEST.md。

思路 / 口径 (Approach — 与 calendar/event/probit 完全同一套因果构造)
  - 数据、bar、盘内过滤、按日 shift(不跨隔夜)全部复用 leadlag_common；
  - calendar 用主 bar 完整网格(al_cal)；event 用活跃事件子序列(act)；K 按活跃度选；
  - 被解释变量自身滞后阶由 BIC 自选(linear=OLS-BIC；probit=probit-BIC)。

输出 (Output)
  leadlag_granger_pairs.csv —— 每行 = 一个 pair × mode × spec × direction
    列：contract_ticker, etf, mode, spec, direction, bar_freq, K, n_ylags,
        wald_chi2, wald_df, p_value, n_obs, n_days, n_active, contract_title
  存放位置：leadlag/pipeline/ 下
"""
import numpy as np
import pandas as pd

import leadlag_common as C
from leadlag_probit import build_calendar_xy, build_event_xy   # probit 口径的 x/y 表

OUT_CSV = C.HERE / "leadlag_granger_pairs.csv"
MIN     = 2 * 3 + 5   # K=3 时最小有效事件数

DIRECTIONS_CAL = [("dprob",   "etfret",   "kalshi->etf"),
                  ("etfret",  "dprob",    "etf->kalshi")]
DIRECTIONS_EVT = [("dprob_e", "etfret_e", "kalshi->etf"),
                  ("etfret_e", "dprob_e", "etf->kalshi")]


def _emit(g, ticker, etf, mode, spec, direction, freq, title):
    row = {"contract_ticker": ticker, "etf": etf, "mode": mode, "spec": spec,
           "direction": direction, "bar_freq": freq, "contract_title": title}
    row.update(g)
    return row


def granger_pair(al_cal, act, cal_pro, evt_pro, ticker, etf, freq, title):
    """给一个 pair 的各口径表，跑 linear 双向 + probit(仅 K→E)，返回行列表。"""
    rows = []
    # ---- linear calendar ----
    if al_cal is not None and not al_cal.empty:
        n = int((al_cal["dprob"].abs() > 1e-12).sum())
        if n >= MIN:
            k = C.choose_k(n)
            for cause, eff, d in DIRECTIONS_CAL:
                g = C.run_granger_direction(al_cal, cause, eff, k, group_by_day=True, own_lags="auto")
                if g:
                    rows.append(_emit(g, ticker, etf, "calendar", "linear", d, freq, title))
    # ---- linear event ----
    if act is not None and len(act) >= MIN:
        n = int((act["dprob_e"].abs() > 1e-12).sum())
        if n >= MIN:
            k = C.choose_k(n)
            for cause, eff, d in DIRECTIONS_EVT:
                g = C.run_granger_direction(act, cause, eff, k, group_by_day=True, own_lags="auto")
                if g:
                    rows.append(_emit(g, ticker, etf, "event", "linear", d, freq, title))
    # ---- probit（仅 Kalshi→ETF 方向；calendar + event 两口径）----
    for mode, tbl in [("calendar", cal_pro), ("event", evt_pro)]:
        if tbl is None or len(tbl) < 30:
            continue
        # K 按「有信息量的观测数」(非零 cause) 选，与 linear 一致；len(tbl) 会把平静 bar 也算进去
        k = C.choose_k(int((tbl["x"].abs() > 1e-12).sum()))
        g = C.run_granger_probit(tbl, "x", "y", k, group_by_day=True, own_lags="auto")
        if g:
            rows.append(_emit(g, ticker, etf, mode, "probit", "kalshi->etf", freq, title))
    return rows


def _verdict(p_kalshi, p_etf, alpha=0.05):
    a = np.isfinite(p_kalshi) and p_kalshi < alpha
    b = np.isfinite(p_etf) and p_etf < alpha
    if a and not b:
        return "Kalshi leads"
    if b and not a:
        return "ETF leads"
    if a and b:
        return "bidir"
    return "neither"


def main():
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 78)
    print("标准 Granger 联合检验  |  linear 双向 + probit(K→E)  |  面板 Newey-West(hac-panel)")
    print("=" * 78)

    out = []
    for idx, pair in sig.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        title = str(pair.get("contract_title", ""))

        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        if kalshi.empty or etf_tk.empty:
            print(f"[{idx+1}/{len(sig)}] {ticker}×{etf}  跳过：无数据")
            continue

        med = C.median_intertrade_sec(kalshi)
        freq = C.BAR_LABEL[C.choose_bar_sec(med if np.isfinite(med) else 60)]
        al_cal, act = C.build_unified_xy(kalshi, etf_tk, freq)
        cal_pro, _ = build_calendar_xy(con, ticker, etf, ds, de)
        evt_pro, _ = build_event_xy(con, ticker, etf, ds, de)
        rows = granger_pair(al_cal, act, cal_pro, evt_pro, ticker, etf, freq, title)
        out += rows

        msg = []
        for mode in ("calendar", "event"):
            pk = next((r["p_value"] for r in rows if r["mode"] == mode and r["spec"] == "linear" and r["direction"] == "kalshi->etf"), np.nan)
            pe = next((r["p_value"] for r in rows if r["mode"] == mode and r["spec"] == "linear" and r["direction"] == "etf->kalshi"), np.nan)
            pp = next((r["p_value"] for r in rows if r["mode"] == mode and r["spec"] == "probit"), np.nan)
            if np.isfinite(pk) or np.isfinite(pe):
                msg.append(f"{mode}: K→E {pk:.2g}/E→K {pe:.2g}[{_verdict(pk, pe)}] probit {pp:.2g}")
        print(f"[{idx+1}/{len(sig)}] {ticker}×{etf}  " + (" | ".join(msg) if msg else "样本不足"))

    if not out:
        print("\n无任何配对产出结果。"); return
    df = pd.DataFrame(out)
    cols = ["contract_ticker", "etf", "mode", "spec", "direction", "bar_freq", "K", "n_ylags",
            "wald_chi2", "wald_df", "p_value", "n_obs", "n_days", "n_active", "cov_type", "contract_title"]
    df = df[cols]
    df.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}  ({len(df)} 行 = pair×mode×spec×方向)")

    for mode in ("calendar", "event"):
        lin = df[(df["mode"] == mode) & (df["spec"] == "linear")]
        kl = lin[(lin.direction == "kalshi->etf") & (lin.p_value < 0.05)]
        el = lin[(lin.direction == "etf->kalshi") & (lin.p_value < 0.05)]
        pro = df[(df["mode"] == mode) & (df["spec"] == "probit")]
        ps = pro[pro.p_value < 0.05]
        npair = lin["contract_ticker"].nunique()
        print(f"{mode:9}: {npair} 对  linear[Kalshi→ETF 显著={len(kl)} / ETF→Kalshi 显著={len(el)}]  "
              f"probit[K→E 显著={len(ps)}/{len(pro)}]")


if __name__ == "__main__":
    main()
