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
  - **linear 与 probit 吃同一张表、同一个门槛**：每对每个 mode 只构造一次 al_cal/act，
    两个 spec 共用；门槛统一为 n_active(非零 cause 观测数) >= 2*3+5，K = choose_k(n_active)。
    (旧版 probit 另走 build_calendar_xy 的 inner-merge 表、门槛写死 len>=30，样本和阈值
     都与 linear 不同 —— 那是主观且不可比的，已废弃。)
  - 被解释变量自身滞后阶由 BIC 自选(linear=OLS-BIC；probit=probit-BIC)；
    probit 的最小样本量同样由 2k+5 推出，不再用固定 30。

输出 (Output)
  leadlag_granger_pairs.csv —— 每行 = 一个 pair × mode × spec × direction
    列：contract_ticker, etf, mode, spec, direction, bar_freq, K, n_ylags,
        wald_chi2, wald_df, p_value, n_obs, n_days, n_active, contract_title
  存放位置：leadlag/pipeline/ 下
"""
import numpy as np
import pandas as pd

import leadlag_common as C

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


def _n_active(df, col):
    """有信息量的观测数 = cause 真正变动过的 bar 数（平静 bar 不提供识别力）。"""
    return 0 if df is None or df.empty else int((df[col].abs() > 1e-12).sum())


def granger_pair(al_cal, act, ticker, etf, freq, title):
    """给一个 pair 的两张统一表(al_cal / act)，跑 linear 双向 + probit(仅 K→E)，返回行列表。

    样本与门槛口径（linear 与 probit 完全一致，避免主观差异）：
      - 两个 spec 吃**同一张表**：calendar 用 al_cal，event 用 act；
      - 门槛都是 n_active = 非零 cause 的观测数 >= MIN(=2*3+5)；
      - K 都由 choose_k(n_active) 选；
      - probit 额外只要求「涨/跌两类都出现」——那是模型固有要求，不是人为门槛。
    """
    rows = []
    # ---- calendar：linear 双向 + probit(K→E)，同一张 al_cal ----
    n_cal = _n_active(al_cal, "dprob")
    if n_cal >= MIN:
        k = C.choose_k(n_cal)
        for cause, eff, d in DIRECTIONS_CAL:
            g = C.run_granger_direction(al_cal, cause, eff, k, group_by_day=True, own_lags="auto")
            if g:
                rows.append(_emit(g, ticker, etf, "calendar", "linear", d, freq, title))
        pro = al_cal.rename(columns={"dprob": "x", "etfret": "y"})[["x", "y", "date"]]
        g = C.run_granger_probit(pro, "x", "y", k, group_by_day=True, own_lags="auto")
        if g:
            rows.append(_emit(g, ticker, etf, "calendar", "probit", "kalshi->etf", freq, title))

    # ---- event：linear 双向 + probit(K→E)，同一张 act ----
    n_evt = _n_active(act, "dprob_e")
    if n_evt >= MIN:
        k = C.choose_k(n_evt)
        for cause, eff, d in DIRECTIONS_EVT:
            g = C.run_granger_direction(act, cause, eff, k, group_by_day=True, own_lags="auto")
            if g:
                rows.append(_emit(g, ticker, etf, "event", "linear", d, freq, title))
        pro = act.rename(columns={"dprob_e": "x", "etfret_e": "y"})[["x", "y", "date"]]
        g = C.run_granger_probit(pro, "x", "y", k, group_by_day=True, own_lags="auto")
        if g:
            rows.append(_emit(g, ticker, etf, "event", "probit", "kalshi->etf", freq, title))
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
        # 只构造一次：linear 与 probit 共用 al_cal / act，不再重复 load DuckDB
        al_cal, act = C.build_unified_xy(kalshi, etf_tk, freq)
        rows = granger_pair(al_cal, act, ticker, etf, freq, title)
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
    # 多重检验校正：检验族 = 同一 (mode, spec, direction) 下跨所有配对的那一组联合 Wald p。
    # 我们对 ~27 对各跑一次同一个检验；不校正的话光靠运气就会有几个 p<0.05。
    df = C.add_fdr(df, ("mode", "spec", "direction"), pcol="p_value", outcol="p_fdr")
    cols = ["contract_ticker", "etf", "mode", "spec", "direction", "bar_freq", "K", "n_ylags",
            "wald_chi2", "wald_df", "p_value", "p_fdr", "n_obs", "n_days", "n_active", "cov_type",
            "contract_title"]
    df = df[cols]
    df.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}  ({len(df)} 行 = pair×mode×spec×方向)")

    for mode in ("calendar", "event"):
        lin = df[(df["mode"] == mode) & (df["spec"] == "linear")]
        pro = df[(df["mode"] == mode) & (df["spec"] == "probit")]
        npair = lin["contract_ticker"].nunique()

        def _cnt(d, col):
            return int((d[col] < 0.05).sum())
        kl, ke = lin[lin.direction == "kalshi->etf"], lin[lin.direction == "etf->kalshi"]
        print(f"{mode:9}: {npair} 对  linear[K→E raw={_cnt(kl,'p_value')} fdr={_cnt(kl,'p_fdr')} / "
              f"E→K raw={_cnt(ke,'p_value')} fdr={_cnt(ke,'p_fdr')}]  "
              f"probit[K→E raw={_cnt(pro,'p_value')} fdr={_cnt(pro,'p_fdr')} /{len(pro)}]")


if __name__ == "__main__":
    main()
