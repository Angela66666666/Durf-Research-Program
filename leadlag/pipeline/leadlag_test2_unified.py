"""
leadlag_test2_unified.py
================================================================================
这个文件做什么 (What this file does)
  稳健性检查：在「统一因果构造」下重新跑一遍 calendar / event 两套回归，
  与原始两套脚本的结论对照，量化"统一构造 + 杜绝 look-ahead"对结果的影响。
  Robustness check: re-run both calendar/event regressions under one unified,
  look-ahead-free construction and compare against the original two scripts.

为什么这么做 (Why)
  原 event 模式的 median 取点可能"偷看 bar 内未来"，会制造假显著；本脚本用同一套
  因果构造（两套同 bar、同收益定义，只差"滞后怎么数"）验证结论是否依赖该 bug。
  The original event median could peek at within-bar future and fabricate
  significance; this verifies the conclusions don't depend on that artifact.

思路 (Approach)
  构造全部来自 leadlag_common.build_unified_xy（右边沿 median、因果无 look-ahead）；
  calendar 用钟表网格序列、event 用活跃事件序列，回归引擎与主脚本一致。

输出 (Output)
  leadlag_test2_unified_kalshi_etf.csv，并打印与原 calendar/event 的显著数对比
  存放位置：leadlag/pipeline/ 下

函数 (Functions)
  main  逐对统一因果构造 -> 两套回归 -> 落盘 + 打印对比
"""
import numpy as np
import pandas as pd

import leadlag_common as C

OUT_CSV = C.HERE / "leadlag_test2_unified_kalshi_etf.csv"
MIN_OBS = 2 * 3 + 5


def main():
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 70)
    print("统一因果构造稳健性检查 (calendar=钟表滞后 / event=事件滞后；同 bar 同收益；右边沿 median 无 look-ahead)")
    print("=" * 70)
    out = []
    for i, pair in sig.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        if kalshi.empty or etf_tk.empty:
            continue
        med_gap = C.median_intertrade_sec(kalshi)
        freq = C.BAR_LABEL[C.choose_bar_sec(med_gap if np.isfinite(med_gap) else 60)]
        al_cal, act = C.build_unified_xy(kalshi, etf_tk, freq)

        for mode, df, xc, yc in [("calendar", al_cal, "dprob", "etfret"),
                                 ("event", act, "dprob_e", "etfret_e")]:
            if df is None or len(df) < MIN_OBS:
                continue
            k = C.choose_k(len(df))
            res = C.run_joint_lag_regression(df, x_col=xc, y_col=yc, k=k)
            if res is None or res.empty:
                continue
            res["contract_ticker"] = ticker; res["etf"] = etf; res["mode"] = mode
            res["bar_freq"] = freq; res["K_chosen"] = k; res["n_total"] = len(df)
            res["contract_title"] = str(pair.get("contract_title", ""))
            out.append(res)
        print(f"[{i+1}/{len(sig)}] {ticker}×{etf}  bar={freq}  done")

    if not out:
        print("无结果。"); return
    df_out = pd.concat(out, ignore_index=True)[
        ["contract_ticker", "etf", "mode", "bar_freq", "K_chosen", "k_lag", "direction",
         "coef", "t_stat", "p_value", "r_squared", "n_obs", "n_total", "contract_title"]]
    df_out.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}")
    for mode in ["calendar", "event"]:
        d = df_out[df_out["mode"] == mode]; s = d[d["p_value"] < 0.05]
        print(f"[统一] {mode:9}: 显著 {len(s):>3}/{len(d):<4}  "
              f"Kalshi领先(k>0)={len(s[s.k_lag>0]):>3}  ETF领先(k<0)={len(s[s.k_lag<0]):>3}  同期={len(s[s.k_lag==0]):>3}")


if __name__ == "__main__":
    main()
