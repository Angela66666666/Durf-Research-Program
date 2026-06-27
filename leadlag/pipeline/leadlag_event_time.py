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

思路 (Approach)
  - outlier：与 calendar 一致——先把 prob 与 mid 各自 median-resample 到细 bar
    （EVENT_CLEAN_BAR，默认 30s）吸收瞬时尖峰；清洗后每个 bar = 一个事件（既去 sub-bar
    噪声又保留较高事件粒度）
  - x = 相邻事件间 prob 变化；y = 事件后到下一个事件（不跨隔夜、最长 W_SEC）ETF 的前向 log return
  - ETF 取值用 lookup_etf_mid 就近匹配；K 按活跃度选；回归引擎同 calendar

输出 (Output)
  leadlag_event_kalshi_etf.csv —— 每行 = 一个 pair × 一个滞后阶 k
  存放位置：leadlag/pipeline/ 下

函数 (Functions)
  main  逐对加载 -> 清洗成事件 -> 构造 x/前向 y -> 选 K -> 联合滞后回归 -> 汇总落盘
"""
import numpy as np
import pandas as pd

import leadlag_common as C

OUT_CSV         = C.HERE / "leadlag_event_kalshi_etf.csv"
EVENT_CLEAN_BAR = "30s"     # event 模式清尖峰用的细 bar（median 聚合）
W_NS            = C.W_SEC * 1_000_000_000
MAX_GAP_NS      = C.MAX_GAP_SEC * 1_000_000_000


def main():
    con = C.make_con()
    sig_pairs = pd.read_csv(C.SIG_PAIRS_CSV)
    print("=" * 78)
    print(f"Event-time Lead-Lag (Kalshi → ETF) | outlier=resample+median(bar={EVENT_CLEAN_BAR}) | "
          f"W={C.W_SEC}s | TZ={C.TZ} | 盘内 09:30-16:00")
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

        # median-resample 清尖峰（细 bar），清洗后的 bar = 事件
        k_bars = C.bar_median_series(kalshi, "prob", EVENT_CLEAN_BAR)
        e_bars = C.bar_median_series(etf_tk, "mid",  EVENT_CLEAN_BAR)
        if len(k_bars) < 2 or e_bars.empty:
            print("  跳过：清洗后 bar 不足")
            continue
        k_bars = k_bars.sort_values("ts_et").reset_index(drop=True)
        k_bars["prob_change"] = k_bars.groupby("date")["prob"].diff()
        k_bars = k_bars.dropna(subset=["prob_change"]).reset_index(drop=True)
        if len(k_bars) < 2:
            print("  跳过：清洗后事件不足")
            continue

        # ETF 清洗后 bar 序列，供就近匹配
        etf_ns  = e_bars["ts_et"].astype("datetime64[ns]").astype("int64").values
        etf_mid = e_bars["mid"].values
        ev_ns   = k_bars["ts_et"].astype("datetime64[ns]").astype("int64").values

        etf_at_t = C.lookup_etf_mid(etf_ns, etf_mid, ev_ns, MAX_GAP_NS)

        # 前向窗口：到下一个事件（同日）否则 +W，封顶 t+W，再 cap 到当日 16:00 收盘
        dates_arr = k_bars["date"].values
        same_day = dates_arr[:-1] == dates_arr[1:]
        raw_next = np.empty_like(ev_ns)
        raw_next[:-1] = np.where(same_day, ev_ns[1:], ev_ns[:-1] + W_NS)
        raw_next[-1]  = ev_ns[-1] + W_NS
        forward_ns = np.minimum(raw_next, ev_ns + W_NS)
        # ③ cap 到当日 16:00（否则近收盘的最后一个事件 forward 会越过收盘，得到失真/超短 horizon）
        close_ns = (pd.to_datetime(k_bars["date"].astype(str)) + pd.Timedelta(hours=16)
                    ).astype("int64").values
        forward_ns = np.minimum(forward_ns, close_ns)

        etf_fwd = C.lookup_etf_mid(etf_ns, etf_mid, forward_ns, MAX_GAP_NS)
        y_ret = np.log(etf_fwd / etf_at_t)   # ETF 前向 log return（非 mid price）

        df = pd.DataFrame({
            "y_ret": y_ret,
            "x_prob_chg": k_bars["prob_change"].values,
            "date": k_bars["date"].values,
        }).dropna(subset=["y_ret", "x_prob_chg"])
        n_active = len(df)
        if n_active < 2 * 3 + 5:
            print(f"  跳过：样本不足 (n={n_active})")
            continue

        k = C.choose_k(n_active)
        print(f"  有效事件={n_active} -> K={k}")

        # 按日 shift(不跨隔夜) + ETF 自滞后控制(ADL/第8点)，与 calendar 口径一致
        res = C.run_joint_lag_regression(df, x_col="x_prob_chg", y_col="y_ret", k=k,
                                         group_by_day=True, y_lags=5)
        if res is None or res.empty:
            print("  跳过：回归样本不足")
            continue

        res["contract_ticker"] = ticker
        res["etf"]             = etf
        res["mode"]            = "event"
        res["clean_bar"]       = EVENT_CLEAN_BAR
        res["w_sec"]           = C.W_SEC
        res["K_chosen"]        = k
        res["n_active_events"] = n_active
        res["contract_title"]  = pair.get("contract_title", "")
        res["r2_daily_screen"] = pair.get("r_squared", np.nan)
        out.append(res)

    if out:
        df_out = pd.concat(out, ignore_index=True)
        # ④ BH-FDR：在每个 pair 的滞后族内校正
        df_out = C.add_fdr(df_out, ["contract_ticker", "etf"])
        cols = ["contract_ticker", "etf", "mode", "clean_bar", "w_sec", "K_chosen", "k_lag",
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
