"""
leadlag_probit.py
================================================================================
这个文件做什么 (What this file does)
  方向性检验：把"Kalshi 能不能预测 ETF"从"猜幅度"降级成"猜涨跌方向"。
  对每个滞后阶 k 跑一个 probit：Pr(ETF 下一期收益 > 0) = Φ(α + β·Δprob_{t-k})。
  Directional test: reduce "can Kalshi predict ETF" to predicting up/down only,
  one probit per lag k: Pr(ETF return > 0) = Φ(α + β·Δprob_{t-k}).

为什么这么做 (Why)
  线性回归对 outlier/幅度敏感；只问方向更稳健，也更贴近"领先"的经济含义。
  β_k>0 显著且落在 k>0 一侧 -> 过去的 Kalshi 概率变化能预测 ETF 方向 -> Kalshi 方向上领先。
  Direction-only is robust to outliers and closer to the economic meaning of "lead".

思路 (Approach)
  - 与主回归口径一致、两套并行：calendar 用按活跃度选的 median 主 bar、y=同 bar log return；
    event 用 30s median bar、y=事件后前向 log return
  - y 取 sign（>0 涨 / <0 跌），去掉恰好不动 (y==0) 的 bar（只问"动的时候往哪动"）
  - 标准误按交易日聚类（失败则退化为普通 probit）

输出 (Output)
  leadlag_probit_kalshi_etf.csv —— 每行 = 一个 pair × mode × 滞后阶 k
  存放位置：leadlag/pipeline/ 下

函数 (Functions)
  build_calendar_xy  造 calendar 口径的 (x=Δprob, y=同bar log return) 表
  build_event_xy     造 event 口径的 (x=Δprob, y=前向 log return) 表
  run_probit_lags    对每个滞后阶 k 跑一个 probit，返回 β/z/p 系数表
  main               逐对 × 两 mode 跑 probit，汇总落盘并打印方向分布
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm

import leadlag_common as C
from leadlag_calendar_time import bar_change   # calendar 的 median-bar 变化量

OUT_CSV     = C.HERE / "leadlag_probit_kalshi_etf.csv"
EVENT_BAR   = "30s"
W_NS        = C.W_SEC * 1_000_000_000
MAX_GAP_NS  = C.MAX_GAP_SEC * 1_000_000_000
MIN_PROBIT  = 30          # probit 最小样本（小样本不稳，跟主回归一样稀疏对会被跳过）


def build_calendar_xy(con, ticker, etf, ds, de):
    """造 calendar 口径 (x=Δprob, y=同 bar log return) 表。Build calendar-mode x/y table."""
    kalshi = C.load_kalshi(con, ticker, ds, de)
    etf_tk = C.load_etf(con, etf, ds, de)
    if kalshi.empty or etf_tk.empty:
        return None, None
    med_gap = C.median_intertrade_sec(kalshi)
    freq = C.BAR_LABEL[C.choose_bar_sec(med_gap if np.isfinite(med_gap) else 60)]
    kb = bar_change(kalshi, "prob", "x", freq, "kalshi")
    eb = bar_change(etf_tk, "mid",  "y", freq, "etf")
    if kb.empty or eb.empty:
        return None, None
    m = pd.merge(kb[["ts_et", "x", "date"]], eb[["ts_et", "y"]], on="ts_et", how="inner")
    return m, freq


def build_event_xy(con, ticker, etf, ds, de):
    """造 event 口径 (x=Δprob, y=前向 log return) 表。Build event-mode x/y table."""
    kalshi = C.load_kalshi(con, ticker, ds, de)
    etf_tk = C.load_etf(con, etf, ds, de)
    if kalshi.empty or etf_tk.empty:
        return None, None
    kb = C.bar_median_series(kalshi, "prob", EVENT_BAR).sort_values("ts_et").reset_index(drop=True)
    eb = C.bar_median_series(etf_tk, "mid", EVENT_BAR).sort_values("ts_et").reset_index(drop=True)
    if len(kb) < 2 or eb.empty:
        return None, None
    kb["x"] = kb.groupby("date")["prob"].diff()
    kb = kb.dropna(subset=["x"]).reset_index(drop=True)
    if len(kb) < 2:
        return None, None
    e_ns  = eb["ts_et"].astype("datetime64[ns]").astype("int64").values
    e_mid = eb["mid"].values
    ev_ns = kb["ts_et"].astype("datetime64[ns]").astype("int64").values
    at = C.lookup_etf_mid(e_ns, e_mid, ev_ns, MAX_GAP_NS)
    dates = kb["date"].values
    same = dates[:-1] == dates[1:]
    raw = np.empty_like(ev_ns)
    raw[:-1] = np.where(same, ev_ns[1:], ev_ns[:-1] + W_NS)
    raw[-1]  = ev_ns[-1] + W_NS
    fwd = np.minimum(raw, ev_ns + W_NS)
    # ③ cap 到当日 16:00 收盘
    close_ns = (pd.to_datetime(kb["date"].astype(str)) + pd.Timedelta(hours=16)).astype("int64").values
    fwd = np.minimum(fwd, close_ns)
    fmid = C.lookup_etf_mid(e_ns, e_mid, fwd, MAX_GAP_NS)
    y = np.log(fmid / at)
    m = pd.DataFrame({"x": kb["x"].values, "y": y, "date": kb["date"].values})
    return m.dropna(subset=["x", "y"]).reset_index(drop=True), EVENT_BAR


def run_probit_lags(df, k):
    """对每个滞后阶 k 跑 probit：Pr(y_t>0)=Φ(α+β·x_{t-k})，返回系数表。
    One probit per lag k; returns a coefficient table (β/z/p per lag)."""
    df = df.dropna(subset=["x", "y"]).copy()
    df = df[df["y"] != 0.0]                       # 只问"动的时候往哪动"
    if len(df) < MIN_PROBIT or df["x"].std() < 1e-12:
        return None
    df["up"] = (df["y"] > 0).astype(int)
    xstd = df["x"].std()
    rows = []
    for j in range(-k, k + 1):
        d = pd.DataFrame({"up": df["up"].values,
                          "xv": (df["x"].shift(j) / xstd).values,
                          "date": df["date"].values}).dropna()
        if len(d) < MIN_PROBIT or d["up"].nunique() < 2:
            continue
        X = sm.add_constant(d["xv"])
        try:
            try:
                mod = sm.Probit(d["up"], X).fit(disp=0, maxiter=200,
                                                cov_type="cluster", cov_kwds={"groups": d["date"].values})
            except Exception:
                mod = sm.Probit(d["up"], X).fit(disp=0, maxiter=200)
        except Exception:
            continue
        if "xv" not in mod.params.index:
            continue
        direction = "kalshi_leads_etf" if j > 0 else ("etf_leads_kalshi" if j < 0 else "contemp")
        rows.append({"k_lag": j, "direction": direction,
                     "beta": mod.params["xv"], "z_stat": mod.tvalues["xv"],
                     "p_value": mod.pvalues["xv"], "pseudo_r2": mod.prsquared,
                     "n_obs": int(len(d)), "n_up": int(d["up"].sum())})
    return pd.DataFrame(rows) if rows else None


def main():
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 70)
    print("Probit 方向检验 (Kalshi → ETF 涨/跌)  |  calendar + event 两套")
    print("=" * 70)
    out = []
    for i, pair in sig.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        title = str(pair.get("contract_title", ""))

        for mode, builder in [("calendar", build_calendar_xy), ("event", build_event_xy)]:
            df, bar = builder(con, ticker, etf, ds, de)
            if df is None or len(df) < MIN_PROBIT:
                continue
            k = C.choose_k(len(df))
            res = run_probit_lags(df, k)
            if res is None or res.empty:
                continue
            res["contract_ticker"] = ticker
            res["etf"] = etf
            res["mode"] = mode
            res["bar"] = bar
            res["K_chosen"] = k
            res["n_total"] = len(df)
            res["contract_title"] = title
            out.append(res)
        print(f"[{i+1}/{len(sig)}] {ticker}×{etf}  done")

    if not out:
        print("无结果。"); return
    df_out = pd.concat(out, ignore_index=True)
    # ④ BH-FDR：在每个 pair×mode 的滞后族内校正
    df_out = C.add_fdr(df_out, ["contract_ticker", "etf", "mode"])
    cols = ["contract_ticker", "etf", "mode", "bar", "K_chosen", "k_lag", "direction",
            "beta", "z_stat", "p_value", "p_fdr", "pseudo_r2", "n_obs", "n_up", "n_total", "contract_title"]
    df_out = df_out[cols]
    df_out.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}")

    # 汇总：方向显著分布
    print("\n===== 方向性结论汇总 (β 显著 p<0.05) =====")
    for mode in ["calendar", "event"]:
        d = df_out[df_out["mode"] == mode]
        s = d[d["p_value"] < 0.05]
        kl = s[(s.direction == "kalshi_leads_etf") & (s.beta > 0)]
        el = s[(s.direction == "etf_leads_kalshi")]
        print(f"{mode:9}: 显著={len(s):>3}/{len(d):<4}  "
              f"Kalshi方向领先(k>0,β>0)={len(kl):>3}  ETF方向领先(k<0)={len(el):>3}  "
              f"同期={len(s[s.direction=='contemp']):>3}")


if __name__ == "__main__":
    main()
