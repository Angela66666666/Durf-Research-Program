"""
make_merge_pair_plots.py  (leadlag/pipeline/merge/)
================================================================================
这个文件做什么 (What this file does)
  把每个 merge 池化信号当作「一个合成合约」，对它并集里的每个 ETF 出一套与单对完全相同的
  6 张图(timeseries / zoom2 / leadglance / leadzoom / event / lagcoef) + 一页方向表。
  即「一类 × k 个 ETF」，每个 (类×ETF) 是一个伪 pair。

关键口径 (Why / how the combined contract is built)
  不同成员合约的**概率水平不可比**(不同阈值)，只能在 Δprob 层面合并(merge 红线)。所以
  「合成合约线」= 把每个成员**符号对齐后的 Δprob**(同合约同日内差分 × sign)在公共 1min 网格上
  **逐 bar 取均值**，再**累加**成一条合成指数(起点 0.5，单位 pp)。它不是真实概率，只是该类
  信息流向的可视化载体——所以左轴标注为 “combined pooled signal index”，绝不叫 probability。
  6 图全部复用 make_pair_plots / make_enhanced_plots 的函数(传 klabel 改轴名)，保证样式一致；
  lagcoef 直接用 merge 回归输出的 (类×ETF) 系数行。

输出 (Outputs, 落在 merge/plots/ 下)
  merge_{group}_{etf}_{timeseries,zoom2,leadglance,leadzoom,event,lagcoef}.png
  merge_{group}_{etf}_analysis.md     (该 类×ETF 的分级方向表 + 结论)
  merge_pairs_order.csv               (group, etf 顺序，供 build_merge_report 拼装)
用法: python make_merge_pair_plots.py [GROUP]      # 不带参数=全部 4 组
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PIPE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPE))
import leadlag_common as C                                   # noqa: E402
import merge_leadlag as M                                    # GROUPS / windows / etf union  # noqa: E402
import make_pair_plots as MPP                                # noqa: E402
import make_enhanced_plots as MEP                            # noqa: E402

HERE  = Path(__file__).resolve().parent
PLOTS = HERE / "plots"; PLOTS.mkdir(exist_ok=True)
KLABEL = "Combined pooled signal index (cum. sign-aligned ΔP, pp)"
THRESH = (0.05, 0.10, 0.15)
CAL = pd.read_csv(HERE / "leadlag_merged_calendar_kalshi_etf.csv")
EV  = pd.read_csv(HERE / "leadlag_merged_event_kalshi_etf.csv")
PRB = pd.read_csv(HERE / "leadlag_merged_probit_kalshi_etf.csv")


# ============================ 合成合并合约 ============================
def build_combined_kalshi(con, members_signs: dict, win: dict, bar: str = "1min"):
    """返回合成合约的「类 kalshi」df(ts_et, prob)：成员符号对齐 Δprob 逐 bar 取均值再累加(起点0.5)。"""
    cols = {}
    for tk, sign in members_signs.items():
        if tk not in win:
            continue
        ds, de = win[tk]
        kdf = C.load_kalshi(con, tk, ds, de)
        if kdf.empty:
            continue
        kb = C.causal_bars(kdf, "prob", bar)
        if kb.empty:
            continue
        kb = kb.sort_values("ts_et")
        d = kb.groupby("date")["prob"].diff().fillna(0.0) * sign     # 同日内 Δprob × 符号
        cols[tk] = pd.Series(d.values, index=pd.DatetimeIndex(kb["ts_et"]))   # 保留 tz-aware ET
    if not cols:
        return None
    mat = pd.DataFrame(cols).sort_index()
    comb = mat.mean(axis=1, skipna=True).dropna()                    # 逐 bar 跨成员均值
    if comb.empty:
        return None
    level = 0.5 + comb.cumsum()                                      # 合成指数(起点0.5)
    ts = pd.DatetimeIndex(comb.index)
    syn = pd.DataFrame({"ts_et": ts, "prob": level.values})
    syn["date"] = syn["ts_et"].dt.date                               # datetime.date，与 load_* 同款，供按日分组
    return syn


# ============================ 该 (类×ETF) 的方向表页 ============================
def _ke(df):
    return {t: (int(((df["k_lag"] > 0) & (df["p_value"] < t)).sum()),
               int(((df["k_lag"] < 0) & (df["p_value"] < t)).sum())) for t in THRESH}


def combo_md(group, etf, members_signs, path):
    cal = CAL[(CAL["group"] == group) & (CAL["etf"] == etf)]
    if "is_primary_bar" in cal.columns and not cal[cal["is_primary_bar"]].empty:
        cal = cal[cal["is_primary_bar"]]
    ev  = EV[(EV["group"] == group) & (EV["etf"] == etf)]
    prb = PRB[(PRB["group"] == group) & (PRB["etf"] == etf)]
    pos = [t for t, s in members_signs.items() if s > 0]
    neg = [t for t, s in members_signs.items() if s < 0]
    L = [f"MERGE pseudo-pair:  {group}  ×  {etf}",
         "",
         "'Contract' = combined pooled signal (members' sign-aligned Δprob, pooled — NOT a price level):",
         f"  +  {', '.join(pos)}",
         (f"  -  {', '.join(neg)}   (reverse contracts: Δprob flipped)" if neg else "  -  (none)"),
         "",
         "Pooled regression vs this ETF (per-member FE, day-clustered SE, ADL self-lags by BIC).",
         "Direction counts use RAW p (graded thresholds), k>0 Kalshi-leads / k<0 ETF-leads.",
         ""]
    for lab, df in [("CALENDAR (primary bar)", cal), ("EVENT (active-event)", ev),
                    ("PROBIT (Pr(ETF up))", prb)]:
        if df.empty:
            L += [f"== {lab} ==", "  (no result)", ""]; continue
        r = df.iloc[0]
        K  = int(r["K_chosen"]) if "K_chosen" in df.columns and pd.notna(r["K_chosen"]) else "-"
        yl = int(r["n_ylags"]) if "n_ylags" in df.columns and pd.notna(r.get("n_ylags")) else "-"
        no = int(r["n_obs"]) if "n_obs" in df.columns and pd.notna(r["n_obs"]) else "-"
        ke = _ke(df)
        L += [f"== {lab} ==",
              f"  K={K}  ADL self-lags={yl}  n_obs={no}",
              "  " + "   ".join(f"p<{t:.2f}: Kalshi-leads {ke[t][0]} / ETF-leads {ke[t][1]}" for t in THRESH),
              ""]
    # 结论：calendar+event 合计
    agg = pd.concat([cal, ev], ignore_index=True)
    ke = _ke(agg)
    verdict = " | ".join(
        f"p<{t:.2f}: " + ("Kalshi-leads" if ke[t][0] > ke[t][1] else
                          ("ETF-leads" if ke[t][1] > ke[t][0] else "balanced/none")) +
        f" (K{ke[t][0]}/E{ke[t][1]})" for t in THRESH)
    L += ["== Conclusion (calendar+event) ==", "  " + verdict]
    Path(path).write_text("\n".join(L), encoding="utf-8")


# ============================ 主流程 ============================
def run_group(con, group, members_signs, sig, win):
    etfs = M.group_etf_union(sig, list(members_signs))
    syn = build_combined_kalshi(con, members_signs, win)
    if syn is None or len(syn) < 10:
        print(f"  [{group}] 合成合约为空，跳过"); return []
    ds = min(win[t][0] for t in members_signs if t in win)
    de = max(win[t][1] for t in members_signs if t in win)
    title = f"{group} (combined pooled signal)"
    rows = []
    for etf in etfs:
        etf_tk = C.load_etf(con, etf, ds, de)
        if etf_tk.empty:
            print(f"    {etf}: ETF 无数据，跳过"); continue
        tag = f"merge_{group}_{etf}"
        # (1) 全窗时序
        kb = C.causal_bars(syn, "prob", MPP.PLOT_BAR)
        eb = MPP.etf_cumret(etf_tk)
        MPP.plot_timeseries(0, title, etf, "", kb, eb, PLOTS / f"{tag}_timeseries.png", klabel=KLABEL)
        # (2)(3)(4) zoom2 / leadglance / leadzoom（盘连盘对齐序列）
        lo, hi = MPP.zoom_window(syn)
        med = C.median_intertrade_sec(syn[(syn['ts_et'] >= lo) & (syn['ts_et'] <= hi)])
        bar_sec = MPP.snap_plot_bar(med if np.isfinite(med) else 60)
        freq = MPP.PLOT_BAR_LABEL[bar_sec]
        al = MEP.build_aligned(syn, etf_tk, lo, hi, freq)
        figs = ["timeseries"]
        if al is not None and len(al) >= 5:
            MEP.plot_zoom2(title, etf, "", al, freq, PLOTS / f"{tag}_zoom2.png", klabel=KLABEL); figs.append("zoom2")
            if MEP.plot_leadglance(title, etf, "", al, freq, bar_sec, PLOTS / f"{tag}_leadglance.png", klabel=KLABEL):
                figs.append("leadglance")
            if MEP.plot_leadzoom(title, etf, "", al, freq, bar_sec, PLOTS / f"{tag}_leadzoom.png", klabel=KLABEL):
                figs.append("leadzoom")
        # (5) event 视角
        if MEP.plot_event(title, etf, "", syn, etf_tk, PLOTS / f"{tag}_event.png", klabel=KLABEL):
            figs.append("event")
        # (6) lagcoef（直接用 merge 回归系数）
        cpair = CAL[(CAL["group"] == group) & (CAL["etf"] == etf)]
        if "is_primary_bar" in cpair.columns and not cpair[cpair["is_primary_bar"]].empty:
            cpair = cpair[cpair["is_primary_bar"]]
        epair = EV[(EV["group"] == group) & (EV["etf"] == etf)]
        MPP.plot_lagcoef(0, title, etf, "", cpair, epair, PLOTS / f"{tag}_lagcoef.png"); figs.append("lagcoef")
        # 表页
        combo_md(group, etf, members_signs, PLOTS / f"{tag}_analysis.md")
        rows.append({"group": group, "etf": etf})
        print(f"    {etf}: {figs}")
    return rows


def main():
    sel = sys.argv[1] if len(sys.argv) > 1 else None
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    win = M.member_windows(sig)
    order = []
    print("=" * 80); print("MERGE 伪 pair 图：每个池化信号 × 每个 ETF 出 6 图 + 表"); print("=" * 80)
    for group, members_signs in M.GROUPS.items():
        if sel and group != sel:
            continue
        print(f"\n[{group}]")
        order += run_group(con, group, members_signs, sig, win)
    pd.DataFrame(order).to_csv(PLOTS / "merge_pairs_order.csv", index=False)
    print(f"\n完成 -> {PLOTS}  (merge_pairs_order.csv: {len(order)} 个 类×ETF)")


if __name__ == "__main__":
    main()
