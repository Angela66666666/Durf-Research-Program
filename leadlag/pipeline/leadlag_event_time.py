"""
leadlag_event_time.py
================================================================================
这个文件做什么 (What this file does)
  Event-time（事件时间）口径的 lead-lag：以 Kalshi 的「价格更新事件」为节点，
  滞后 k = k 个事件之前（平静期被压缩、活跃期被拉伸）。与 calendar 模式并行。
  Lead-lag on an event axis: nodes are Kalshi price-update events; lag k means
  k events earlier. Runs in parallel with the calendar mode.

为什么这么做 (Why)
  和 calendar 唯一差别就是「滞后怎么数」——calendar 数钟表时间、event 数事件个数；
  两套并列，可对比哪种时间轴更能反映领先滞后关系。
  Only difference vs calendar is how lags are counted (clock time vs event count);
  reporting both lets one compare which axis better captures the lead-lag.

思路 (Approach) —— 与 calendar 完全同一套统一因果构造，只差"相邻怎么定义"
  - 用 build_unified_xy 的 act：只保留 Kalshi 有成交的 bar(=事件)，相邻事件间算变化量。
  - x = 相邻事件间 Δprob(dprob_e)；y = 同样这两个事件点间的 ETF log return(etfret_e)。
    两者都在【相邻两事件】之间、同口径(右边沿 median 抗 outlier、因果无 look-ahead)。
    => 不再用"前向收益+就近匹配"(那会让前向窗口与下一个事件重叠，把同期共动误记成 ETF 领先)。
  - 与 calendar 的唯一差别 = 钟表格 vs 仅活跃事件；K 按活跃度选；回归引擎(ADL+按日 shift)同 calendar。

输出 (Output)
  leadlag_event_kalshi_etf.csv —— 每行 = 一个 pair × 一个滞后阶 k
  存放位置：leadlag/pipeline/ 下

函数 (Functions)
  main  逐对加载 -> 统一构造活跃事件(x=Δprob, y=后向 log return) -> 选 K -> 联合滞后回归 -> 落盘
"""
import numpy as np
import pandas as pd

import leadlag_common as C

OUT_CSV         = C.HERE / "leadlag_event_kalshi_etf.csv"
MIN_EVENTS      = 2 * 3 + 5   # K=3 时最小有效事件数


def main():
    con = C.make_con()
    sig_pairs = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 78)
    print(f"Event-time Lead-Lag (Kalshi → ETF) | 统一因果构造(后向差分,与 calendar 同口径) | "
          f"TZ={C.TZ} | 盘内 09:30-16:00")
    print("=" * 78)

    out = []
    for idx, pair in sig_pairs.iterrows():
        ticker, etf = pair["contract_ticker"], pair["etf"]
        ds, de = str(pair["date_start"]), str(pair["date_end"])
        print(f"\n[{idx+1}/{len(sig_pairs)}] X:{ticker} Y:{etf}  [{ds}~{de}]")

        kalshi = C.load_kalshi(con, ticker, ds, de)
        etf_tk = C.load_etf(con, etf, ds, de)
        if kalshi.empty or etf_tk.empty:
            print("  跳过：无数据")
            continue

        # 统一因果构造：active 事件子序列(只取 Kalshi 有成交的 bar)，x=Δprob、y=ETF log return
        # 都在【相邻两个事件】之间算，与 calendar 完全同公式，仅"相邻"的定义不同(事件 vs 钟表格)。
        med_gap = C.median_intertrade_sec(kalshi)
        freq = C.BAR_LABEL[C.choose_bar_sec(med_gap if np.isfinite(med_gap) else 60)]
        _, act = C.build_unified_xy(kalshi, etf_tk, freq)
        if act is None or len(act) < MIN_EVENTS:
            print("  跳过：活跃事件不足")
            continue

        n_active = int((act["dprob_e"].abs() > 1e-12).sum())   # x≠0 的有效事件数
        k = C.choose_k(n_active)
        print(f"  bar={freq} 活跃事件={len(act)} 有效={n_active} -> K={k}")

        # 按日 shift(不跨隔夜) + ETF 自滞后控制(ADL)，与 calendar 口径完全一致
        res = C.run_joint_lag_regression(act, x_col="dprob_e", y_col="etfret_e", k=k,
                                         group_by_day=True, y_lags=5)
        if res is None or res.empty:
            print("  跳过：回归样本不足")
            continue

        res["contract_ticker"] = ticker
        res["etf"]             = etf
        res["mode"]            = "event"
        res["bar_freq"]        = freq
        res["K_chosen"]        = k
        res["n_active_events"] = len(act)
        res["contract_title"]  = pair.get("contract_title", "")
        res["r2_daily_screen"] = pair.get("r_squared", np.nan)
        out.append(res)

    if out:
        df_out = pd.concat(out, ignore_index=True)
        # ④ BH-FDR：在每个 pair 的滞后族内校正
        df_out = C.add_fdr(df_out, ["contract_ticker", "etf"])
        cols = ["contract_ticker", "etf", "mode", "bar_freq", "K_chosen", "k_lag",
                "direction", "coef", "t_stat", "p_value", "p_fdr", "r_squared", "n_obs", "n_days",
                "n_params", "n_active", "n_active_events", "r2_daily_screen", "contract_title"]
        df_out = df_out[cols]
        df_out.to_csv(OUT_CSV, index=False)
        sig = df_out[df_out["p_value"] < 0.05]
        print(f"\n完成 -> {OUT_CSV}")
        print(f"显著系数(p<0.05): {len(sig)} / {len(df_out)}")
    else:
        print("\n无任何配对产出结果。")


if __name__ == "__main__":
    main()
