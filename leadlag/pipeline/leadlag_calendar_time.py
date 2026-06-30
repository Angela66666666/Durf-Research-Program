"""
leadlag_calendar_time.py
================================================================================
这个文件做什么 (What this file does)
  Calendar-time（钟表时间）口径的 lead-lag：把 Kalshi 与 ETF 都重采样到固定日历 bar，
  在等间隔时间轴上做联合滞后回归，滞后 k = k × bar 的真实钟表时间。
  Lead-lag on a fixed clock-time grid: resample both series to equal bars and run
  one joint-lag regression; lag k means k × bar of wall-clock time.

为什么这么做 (Why)
  Kalshi 成交不连续，用 event/tick 时间会混淆"没成交"和"没信息"；日历时间给可比的等距网格。
  Trades are sparse; an event/tick axis conflates "no trade" with "no news",
  so a clock-time grid gives a comparable, evenly spaced axis.

思路 (Approach)
  - **完整盘内网格**(build_unified_xy)：Kalshi prob 在网格上 ffill，平静 bar 的 Δx=0、不丢弃，
    这样"滞后 j"才是真正的钟表间隔(不是"第 j 个有交易的 bar")。
  - outlier：bar 内取 median（causal 右沿），瞬时尖峰自然吸收，不做逐点删除
  - **按日 shift**(不跨隔夜) + **ETF 自滞后控制 ADL**(净掉 ETF 自身动量)
  - bar 大小不固定：按合约交易节奏选「主 bar」，全网格 robustness，is_primary_bar 标注
  - K 与可靠性按**有效事件数 n_active**(x≠0 的 bar)而非网格行数；显著性用 **BH-FDR** 校正(p_fdr)
  - 回归引擎 common.run_joint_lag_regression（日固定效应 + 按日聚类 SE）

输出 (Output)
  leadlag_calendar_kalshi_etf.csv —— 每行 = 一个 pair × 一个候选 bar × 一个滞后阶 k
  含 p_fdr / n_params / n_active 列。存放位置：leadlag/pipeline/ 下
"""
import numpy as np
import pandas as pd

import leadlag_common as C

OUT_CSV = C.HERE / "leadlag_calendar_kalshi_etf.csv"
MIN_BARS = 2 * 3 + 5   # 最小有效事件数下限（K=3 时）
ADL_YLAGS = "auto"     # ETF 自滞后控制阶数：每对在自己 bar 上用 BIC 自选（第8点：净掉 ETF 自身动量）


def bar_change(df, value_col, out_col, freq, kind):
    """median-resample 到 bar，再算同日内变化量：etf->log return，kalshi->prob 差分。
    Resample to median bars, then per-day change: ETF log return / Kalshi prob diff."""
    bars = C.bar_median_series(df, value_col, freq)
    if bars.empty:
        return pd.DataFrame(columns=["ts_et", out_col, "date"])
    pieces = []
    for d, g in bars.groupby("date"):
        s = g.set_index("ts_et")[value_col]
        if len(s) < 2:
            continue
        chg = np.log(s).diff() if kind == "etf" else s.diff()
        piece = pd.DataFrame({"ts_et": s.index, out_col: chg.values, "date": d})
        pieces.append(piece.dropna(subset=[out_col]))
    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=["ts_et", out_col, "date"])


def run_one_bar(kalshi, etf_tk, bar_sec):
    """对单一 bar 大小：建**完整盘内网格**(Kalshi prob ffill, 平静 bar Δx=0)，选 K，跑联合滞后回归。
    Full RTH grid (forward-filled Kalshi prob, Δx=0 in quiet bars) so lag j is a true clock lag.
    用按日 shift(不跨隔夜) + ETF 自滞后控制(ADL)；K 与可靠性按**有效事件数**(x≠0)而非网格行数。"""
    freq = C.BAR_LABEL[bar_sec]
    al_cal, _ = C.build_unified_xy(kalshi, etf_tk, freq)
    meta = {"bar_sec": bar_sec, "bar_freq": freq, "n_active_bars": 0, "K_chosen": np.nan}
    if al_cal is None or al_cal.empty:
        return None, meta
    n_events = int((al_cal["dprob"].abs() > 1e-12).sum())   # x≠0 的有效信息量
    meta["n_active_bars"] = n_events
    if n_events < MIN_BARS:
        return None, meta
    k = C.choose_k(n_events)
    meta["K_chosen"] = k
    res = C.run_joint_lag_regression(al_cal, x_col="dprob", y_col="etfret", k=k,
                                     group_by_day=True, y_lags=ADL_YLAGS)
    return res, meta


def main():
    con = C.make_con()
    sig_pairs = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 78)
    print(f"Calendar-time Lead-Lag (Kalshi → ETF) | outlier=resample+median | bar 按活跃度一合约一选 | TZ={C.TZ} | 盘内 09:30-16:00")
    print(f"候选 bar 网格: {[C.BAR_LABEL[s] for s in C.BAR_GRID_SEC]}")
    print("=" * 78)

    out = []
    for idx, pair in sig_pairs.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])

        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        if kalshi.empty or etf_tk.empty:
            print(f"\n[{idx+1}/{len(sig_pairs)}] X:{ticker} Y:{etf}  跳过：无数据")
            continue

        med_gap = C.median_intertrade_sec(kalshi)
        primary_sec = C.choose_bar_sec(med_gap)
        print(f"\n[{idx+1}/{len(sig_pairs)}] X:{ticker} Y:{etf}  "
              f"成交={len(kalshi)} 间隔中位={med_gap:.0f}s -> 主bar={C.BAR_LABEL[primary_sec]}")

        for bar_sec in C.BAR_GRID_SEC:
            res, meta = run_one_bar(kalshi, etf_tk, bar_sec)
            tag = " *主*" if bar_sec == primary_sec else ""
            if res is None or res.empty:
                print(f"    {C.BAR_LABEL[bar_sec]:>5}: bar={meta['n_active_bars']:>4} 样本不足跳过{tag}")
                continue
            print(f"    {C.BAR_LABEL[bar_sec]:>5}: bar={meta['n_active_bars']:>4} K={meta['K_chosen']}{tag}")
            res["contract_ticker"] = ticker
            res["etf"]             = etf
            res["mode"]            = "calendar"
            res["bar_freq"]        = meta["bar_freq"]
            res["bar_sec"]         = bar_sec
            res["is_primary_bar"]  = (bar_sec == primary_sec)
            res["median_intertrade_sec"] = round(med_gap, 1) if np.isfinite(med_gap) else np.nan
            res["K_chosen"]        = meta["K_chosen"]
            res["n_active_bars"]   = meta["n_active_bars"]
            res["contract_title"]  = pair.get("contract_title", "")
            res["r2_daily_screen"] = pair.get("r_squared", np.nan)
            out.append(res)

    if out:
        df_out = pd.concat(out, ignore_index=True)
        # ④ BH-FDR：在每个 pair×bar 的滞后族内校正
        df_out = C.add_fdr(df_out, ["contract_ticker", "etf", "bar_sec"])
        cols = ["contract_ticker", "etf", "mode", "bar_freq", "bar_sec", "is_primary_bar",
                "median_intertrade_sec", "K_chosen", "k_lag", "direction", "coef", "t_stat",
                "p_value", "p_fdr", "r_squared", "n_obs", "n_days", "n_params", "n_active",
                "n_ylags", "n_active_bars", "r2_daily_screen", "contract_title"]
        df_out = df_out[cols]
        df_out.to_csv(OUT_CSV, index=False)
        prim = df_out[df_out["is_primary_bar"]]
        sig_prim = prim[prim["p_value"] < 0.05]
        print(f"\n完成 -> {OUT_CSV}")
        print(f"主 bar 下显著系数(p<0.05): {len(sig_prim)} / {len(prim)}")
    else:
        print("\n无任何配对产出结果。")


if __name__ == "__main__":
    main()
