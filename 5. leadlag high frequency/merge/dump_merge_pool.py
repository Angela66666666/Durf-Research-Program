"""
dump_merge_pool.py  (leadlag/pipeline/merge/)
================================================================================
这个文件做什么 (What this file does)
  把 merge_leadlag 在回归前**构造好的池化长表**原样导出 + 终端预览，让你能直接看到
  「4 个超信号 × 相关ETF」池化后到底长什么样：哪个成员(member)、哪天(date)、
  符号对齐后的 Δprob(x)、配对的 ETF log-return(y)，逐行堆叠的样子。
  Dump (and preview) the per-observation pooled panel that merge_leadlag builds
  *before* it runs the regression — so you can eyeball the stacked rows.

为什么单独写 (Why a separate script)
  merge_leadlag 只落地回归结果 CSV(每行=组×ETF×滞后阶)，看不到底层逐观测的池化数据。
  这里**复用它的构造函数**(build_calendar_pool / build_event_member)，只导出、不回归，
  保证你看到的就是回归真正吃进去的那张表(同样的符号对齐、同样的 bar、同样的清洗)。

输出 (Outputs, 落在 leadlag/pipeline/merge/ 下)
  merged_pool_calendar.csv   每行 = group, etf, member, date, dprob(已符号对齐), etfret
  merged_pool_event.csv      每行 = group, etf, member, date, x(已符号对齐 Δprob), y(ETF logret)
  并在终端打印每个超信号的 成员数 / 行数 / 各成员贡献行数 / 前几行预览。

用法 (Usage)
  python dump_merge_pool.py                 # 全部 4 组 × ETF并集
  python dump_merge_pool.py ELECTION_trump_fav VCR   # 只看某组 × 某ETF（调试用）
"""
from __future__ import annotations
import sys
from pathlib import Path

import pandas as pd

import merge_leadlag as M          # 复用超信号定义 + 池化构造函数
import leadlag_common as C

HERE = Path(__file__).resolve().parent
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def _preview(tag: str, pool: pd.DataFrame):
    """终端打印一张池化表的体检信息：行数 / 成员构成 / 符号 / 头几行。"""
    print(f"\n  ── {tag} ── 行数={len(pool)}  成员数={pool['member'].nunique()}")
    by_mem = pool.groupby("member").size().sort_values(ascending=False)
    print("     各成员贡献行数:")
    for m, n in by_mem.items():
        print(f"        {m:<28} {n:>5}")
    print("     预览(前 6 行):")
    print(pool.head(6).to_string(index=False).replace("\n", "\n        ").rjust(0))
    print("        ...")


def main():
    sel_group = sys.argv[1] if len(sys.argv) > 1 else None
    sel_etf   = sys.argv[2] if len(sys.argv) > 2 else None

    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    win = M.member_windows(sig)

    cal_rows, ev_rows = [], []
    print("=" * 80)
    print("导出 merge 池化数据(回归前的逐观测长表) | 符号对齐后的 Δprob 堆叠")
    print("=" * 80)

    for gname, members_signs in M.GROUPS.items():
        if sel_group and gname != sel_group:
            continue
        etfs = M.group_etf_union(sig, list(members_signs))
        if sel_etf:
            etfs = [e for e in etfs if e == sel_etf]
        kbm = M.load_group_kalshi(con, members_signs, win)
        if not kbm:
            print(f"\n[{gname}] 无任何成员数据，跳过"); continue
        primary_sec = M.pooled_primary_bar(kbm)
        signs = {tk: s for tk, (_, s) in kbm.items()}
        print(f"\n[{gname}] 成员={len(kbm)} 主bar={C.BAR_LABEL[primary_sec]} "
              f"符号={ {tk: ('+' if s>0 else '-') for tk, s in signs.items()} } ETF并集={etfs}")

        for etf in etfs:
            etf_tk = C.load_etf(con, etf, min(win[t][0] for t in kbm), max(win[t][1] for t in kbm))
            if etf_tk.empty:
                print(f"    {etf}: ETF 无数据，跳过"); continue

            # calendar 池：全网格 bar，已符号对齐
            cal = M.build_calendar_pool(kbm, etf_tk, C.BAR_LABEL[primary_sec])
            if cal is not None and not cal.empty:
                cal = cal.copy()
                cal.insert(0, "etf", etf); cal.insert(0, "group", gname)
                cal["sign"] = cal["member"].map(signs)
                cal_rows.append(cal)
                _preview(f"{gname} × {etf}  [CALENDAR  bar={C.BAR_LABEL[primary_sec]}]", cal)

            # event 池：活跃事件子序列，逐成员构造后堆叠
            ev_frames = []
            for tk, (kdf, sign) in kbm.items():
                m = M.build_event_member(kdf, etf_tk, sign, tk)
                if m is not None and not m.empty:
                    ev_frames.append(m)
            if ev_frames:
                ev = pd.concat(ev_frames, ignore_index=True)
                ev.insert(0, "etf", etf); ev.insert(0, "group", gname)
                ev["sign"] = ev["member"].map(signs)
                ev_rows.append(ev)
                _preview(f"{gname} × {etf}  [EVENT  active-subsequence]", ev)

    print("\n" + "=" * 80)
    if cal_rows:
        cdf = pd.concat(cal_rows, ignore_index=True)
        cdf.to_csv(HERE / "merged_pool_calendar.csv", index=False)
        print(f"  merged_pool_calendar.csv : {len(cdf)} 行  "
              f"({cdf['group'].nunique()} 组 × {cdf['etf'].nunique()} ETF, "
              f"列: {list(cdf.columns)})")
    if ev_rows:
        edf = pd.concat(ev_rows, ignore_index=True)
        edf.to_csv(HERE / "merged_pool_event.csv", index=False)
        print(f"  merged_pool_event.csv    : {len(edf)} 行  "
              f"({edf['group'].nunique()} 组 × {edf['etf'].nunique()} ETF, "
              f"列: {list(edf.columns)})")
    print("完成 -> leadlag/pipeline/merge/")


if __name__ == "__main__":
    main()
