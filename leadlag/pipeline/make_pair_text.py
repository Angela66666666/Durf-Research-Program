"""
make_pair_text.py
================================================================================
这个文件做什么 (What this file does)
  为每对生成「数据驱动的文字分析」：显式展开回归公式（真下标 βₖ/xₜ₋ₖ）、完整系数表、
  probit、结论、注意事项，以及（仅排名靠前合约的）查证过的现实事件。
  Generate a data-driven text analysis per pair: expanded regression formulas
  (subscript βₖ/xₜ₋ₖ), full coefficient table, probit, verdict, caveats, and
  (for top-ranked contracts only) WebSearch-verified real-world events.

为什么这么做 (Why)
  报告要把"系数显著在哪个滞后"翻成读者能读懂的公式与结论；现实事件必须查证、带 URL，
  避免旧 pair_analysis 凭空编造叙事的错误。
  The report must translate "which lag is significant" into readable formulas and
  conclusions; real-world events must be verified with URLs (no fabrication).

思路 / 可编辑工作流 (Approach / editable workflow)
  - 分析写成 plots/{tag}_analysis.md（纯文本，**这是可编辑的源文件**）
  - 想改文字 / 逐条核对事件：直接改对应 .md，再跑 build_pdf.py 重渲染即可
  - 重跑本脚本会用数据**覆盖** .md（丢失手改），所以定稿后别再跑本脚本
  - 章节：可靠性横幅 -> 定义 -> 1.calendar 公式 -> 2.event 公式 -> 3.系数表 -> 4.probit
    -> 5.数据可靠性(统计判据) -> 6.粗频率稳健性 -> 7.verdict -> 8.图的问题 -> 9.现实事件
  - 「稀疏/可靠性」由 leadlag_reliability 按统计量(自由度/标准误)判定，非成交笔数阈值；
    「粗频率」由 leadlag_coarse_freq 提供（30min/60min 重跑 calendar）

输出 (Outputs)
  - plots/{tag}_analysis.md   可编辑的分析源文件（每对一个）
  - plots/{tag}_text.png      渲染出的文字页（备用；PDF 现走矢量直出 build_text_fig）
  存放位置：leadlag/pipeline/plots/

函数 (Functions)
  stars/_sub/xlabel/blab  显著性星号 / Unicode 下标 / xₜ₋ₖ / βₖ 写法
  expand_equation         把某模式的显著项展开成显式公式 + 逐项明细，返回 lean
  coef_table              拼 calendar vs event 完整系数表
  probit_block            拼 probit 显著项
  verdict / caveats       结论 / 注意事项
  generate_md             组装一对的完整 .md 文本
  build_text_fig          由 .md 构建文字页 figure（供 PDF 矢量直出）
  render_md_to_png        把 .md 渲染成 PNG（备用）
  main                    为全部 48 对生成 .md + 渲染 PNG
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import leadlag_common as C
import leadlag_reliability as REL   # 统计可靠性分档 + 图的问题
import leadlag_coarse_freq as CF    # 30min/60min 粗频率稳健性

PLOTDIR = C.HERE / "plots"
CALP = pd.read_csv(C.HERE / "leadlag_calendar_kalshi_etf.csv")
CALP = CALP[CALP["is_primary_bar"]]
EV  = pd.read_csv(C.HERE / "leadlag_event_kalshi_etf.csv")
PRB = pd.read_csv(C.HERE / "leadlag_probit_kalshi_etf.csv") if (C.HERE / "leadlag_probit_kalshi_etf.csv").exists() else pd.DataFrame()
RANK = pd.read_csv(PLOTDIR / "pair_ranking.csv")
SIG = pd.read_csv(C.SIG_PAIRS_CSV)

_ELECTION = [
    "2024 US presidential election held Tue Nov 5, 2024; ballots counted overnight Nov 5-6.",
    "AP called the race for Trump ~5:34-5:37 AM ET on Wed Nov 6, 2024 (Wisconsin pushed him past 270) "
    "-- this is PRE-MARKET, so the regular-hours equity reaction shows up at the Nov 6 open.",
    "Final electoral result: Trump 312, Harris 226.",
    "Sources: en.wikipedia.org/wiki/2024_United_States_presidential_election ; "
    "spectrumlocalnews.com/us/snplus/news/2024/11/06/trump-wins-ap-projection-2024-election",
]
_FOMC_SEP = [
    "Sept 2024 FOMC decided Wed Sep 18, 2024 (statement 2:00 PM ET, Powell press conf 2:30 PM ET).",
    "Outcome: 50bps cut to 4.75-5.00% -- a surprise vs the 25bps many expected (first cut in 4+ years).",
    "This contract asked specifically about a 25bps cut; the 50bps outcome resolved it NO.",
    "Sources: federalreserve.gov/monetarypolicy/files/fomcminutes20240918.pdf ; "
    "jpmorgan.com/insights/outlook/economic-outlook/fed-meeting-september-2024",
]
EVENT_CONTEXT = {
    "KXECDJT306": _ELECTION, "KXECDJT316": _ELECTION, "KXECDJT281": _ELECTION,
    "KXECDJT312": _ELECTION, "KXECKH276": _ELECTION, "KXECKH287": _ELECTION,
    "FEDDECISION-24SEP-C25": _FOMC_SEP,
}


def stars(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""


# Unicode 下标，让公式肉眼可读（βₖ、xₜ₋₃、α、Σ、Φ）
_SUBD = str.maketrans("0123456789+-tkn", "₀₁₂₃₄₅₆₇₈₉₊₋ₜₖₙ")
def _sub(s):
    return s.translate(_SUBD)


def xlabel(k):
    """β_k 对应的回归元 xₜ₋ₖ 的可读写法（真下标）。"""
    if k == 0:
        return "xₜ"
    return "x" + _sub(f"t-{k}") if k > 0 else "x" + _sub(f"t+{abs(k)}")


def blab(k):
    """系数 βₖ 的可读写法，如 β₊₃ / β₋₄。"""
    return "β" + _sub(f"{k:+d}")


def _pc(df):
    """显著性用哪一列：优先 BH-FDR 校正后的 p_fdr。"""
    return "p_fdr" if "p_fdr" in df.columns else "p_value"


def expand_equation(df, coefcol, lhs, model_line):
    """把某模式显著项展开成显式公式 + 逐项明细。显著性=BH-FDR 校正后。返回(行列表, lean)。"""
    if df.empty:
        return [f"   {model_line}", "   -> no regression result (insufficient data)."], None
    pc = _pc(df)
    sig = df[df[pc] < 0.05].sort_values("k_lag")
    lines = [f"   {model_line}"]
    if sig.empty:
        lines.append(f"   -> {len(df)} coefficients tested, NONE significant after BH-FDR (p_fdr<0.05).")
        return lines, None
    terms = " + ".join(f"{blab(int(r.k_lag))}·{xlabel(int(r.k_lag))}" for r in sig.itertuples())
    lines.append(f"   Significant terms (BH-FDR) expanded:  {lhs} = α + {terms}")
    lines.append("   where:")
    for r in sig.itertuples():
        coef = getattr(r, coefcol)
        pfdr = getattr(r, "p_fdr", float("nan"))
        side = "Kalshi leads" if r.k_lag > 0 else ("ETF leads" if r.k_lag < 0 else "contemporaneous")
        lines.append(f"      {blab(int(r.k_lag))} = {coef:+.3e}   (t/z={r.t_stat if hasattr(r,'t_stat') else getattr(r,'z_stat',float('nan')):+.2f}, "
                     f"p={r.p_value:.1e}, p_fdr={pfdr:.1e}) {stars(pfdr)}   [{side}]")
    nkpos, nkneg = int((sig.k_lag > 0).sum()), int((sig.k_lag < 0).sum())
    lean = "Kalshi" if nkpos > nkneg else ("ETF" if nkneg > nkpos else "balanced")
    lab = {"Kalshi": "Kalshi-leads", "ETF": "ETF-leads", "balanced": "balanced/no clear side"}[lean]
    lines.append(f"   Lean by count of significant lags: {lab}  (k>0:{nkpos}, k<0:{nkneg}).")
    return lines, lean


def coef_table(cal, ev):
    """第3块：完整系数表(calendar primary vs event)，纯文本对齐。"""
    ks = sorted(set(cal["k_lag"]).union(set(ev["k_lag"])))
    if not ks:
        return ["   (no coefficients in either mode)"]
    cm = {int(r.k_lag): r for r in cal.itertuples()}
    em = {int(r.k_lag): r for r in ev.itertuples()}
    out = ["   {:>4} | {:>22} | {:>22}".format("k", "calendar b (FDR)", "event b (FDR)"),
           "   " + "-" * 54]
    for k in ks:
        c, e = cm.get(k), em.get(k)
        cs = f"{c.coef:+.2e} {stars(getattr(c,'p_fdr',c.p_value)):<3}" if c else "--"
        es = f"{e.coef:+.2e} {stars(getattr(e,'p_fdr',e.p_value)):<3}" if e else "--"
        out.append("   {:>+4d} | {:>22} | {:>22}".format(k, cs, es))
    out.append("   (stars = BH-FDR corrected:  *** p_fdr<.01  ** <.05  * <.10)")
    return out


def probit_block(ticker, etf):
    lines = ["   Model: P(ETFₜ up) = Φ(α + βₖ·xₜ₋ₖ),  one probit per lag k"]
    if PRB.empty:
        lines.append("   -> probit results not available."); return lines
    any_sig = False
    for mode in ["calendar", "event"]:
        d = PRB[(PRB.contract_ticker == ticker) & (PRB.etf == etf) & (PRB["mode"] == mode)]
        pc = _pc(d)
        sig = d[d[pc] < 0.05].sort_values("k_lag")
        if d.empty:
            lines.append(f"   {mode}: n/a"); continue
        if sig.empty:
            lines.append(f"   {mode}: {len(d)} lags tested, none significant after BH-FDR."); continue
        any_sig = True
        terms = ", ".join(f"{blab(int(r.k_lag))}={r.beta:+.2e}{stars(getattr(r,'p_fdr',r.p_value))}" for r in sig.itertuples())
        lines.append(f"   {mode}: {terms}")
    if not any_sig:
        lines.append("   -> no significant directional predictability either mode (BH-FDR).")
    return lines


def verdict(cal_lean, ev_lean, n_sig):
    lab = {"Kalshi": "Kalshi-leads", "ETF": "ETF-leads", "balanced": "balanced"}
    if n_sig == 0:
        return "No lead-lag detected -- too sparse / no significant structure."
    if not (cal_lean or ev_lean):
        return "No significant lead-lag in either time-axis."
    if cal_lean and ev_lean:
        if cal_lean == ev_lean:
            if cal_lean == "balanced":
                return "Both time-axes balanced -- no clean directional lead."
            return f"Both time-axes lean {lab[cal_lean]} (relatively robust; see strongest single term)."
        return f"Calendar leans {lab[cal_lean]} but Event leans {lab[ev_lean]} -- NOT robust across time-axis; no clean lead."
    one = cal_lean or ev_lean
    return f"Only one time-axis significant ({lab[one]}) -- weak / single-mode evidence."


def reliability_block(ticker, etf):
    """数据可靠性：用统计量（有效观测/自由度/中位标准误）判定，不用拍脑袋的成交笔数阈值。"""
    r = REL.get_reliability(ticker, etf)
    lines = [f"   Tier: {r['tier']}"]
    lines.append("   (criterion = n_active: bars with an actual Kalshi move (x!=0) = the real sample that "
                 "identifies the lead-lag. Full RTH grid makes n_obs large, so n_active is the honest size.)")
    def fmt(m, name):
        if m is None:
            return f"   {name}: not estimable (insufficient data)"
        return (f"   {name}: n_active={m['n_active']}  n_obs={m['n_obs']}  n_days={m['n_days']}  K={m['K']}  "
                f"params={m['nparam']}  df={m['df']}  median_SE={m['medSE']:.2e}  sig(FDR)={m['n_sig']}")
    lines.append(fmt(r["cal"], "calendar(full RTH grid)"))
    lines.append(fmt(r["ev"], "event"))
    if r["tier"] == REL.TIER_VERYLOW:
        lines.append("   => Very low info: even 'significant' coefficients are untrustworthy (huge SE, "
                     "possibly spurious significance).")
    elif r["tier"] == REL.TIER_CANNOT:
        lines.append("   => Neither axis is estimable: this pair has descriptive figures only, no "
                     "reliable regression result.")
    return lines, r


def coarse_block(ticker, etf):
    """粗频率稳健性：30min/60min bar 重跑 calendar 的汇总。"""
    rows = CF.get_coarse(ticker, etf)
    if not rows:
        return ["   (coarse-frequency robustness not available)"]
    lines = []
    for d in rows:
        if not bool(d["ran"]):
            lines.append(f"   {d['freq']:>6}: not estimable (n_obs={int(d['n_obs'])} < minimum) "
                         f"-- coarser bars have even fewer observations")
        else:
            lines.append(f"   {d['freq']:>6}: n_obs={int(d['n_obs'])} df={int(d['df'])} K={int(d['K'])}  "
                         f"sig={int(d['n_sig'])} (Kalshi-leads {int(d['kpos'])} / ETF-leads {int(d['kneg'])}) "
                         f"-> {d['lean']}")
    return lines


def caveats(cal, ev):
    """除可靠性外的额外注意事项（混合符号、项目级口径）。"""
    cv = []
    cp, ep = _pc(cal), _pc(ev)
    sig = pd.concat([cal[cal[cp] < 0.05], ev[ev[ep] < 0.05]])
    if not sig.empty and (sig["coef"] < 0).any() and (sig["coef"] > 0).any():
        cv.append("Mixed coefficient signs across lags -- relationship not monotone.")
    cv.append("Kalshi updates only on trades (flat line = no trade, NOT 'no change'); ETF mid refreshes continuously.")
    return cv


def generate_md(rrow):
    ticker, etf, tag = rrow["contract_ticker"], rrow["etf"], rrow["tag"]
    s = SIG[(SIG.contract_ticker == ticker) & (SIG.etf == etf)].iloc[0]
    cal = CALP[(CALP.contract_ticker == ticker) & (CALP.etf == etf)]
    ev  = EV[(EV.contract_ticker == ticker) & (EV.etf == etf)]
    bar = cal["bar_freq"].iloc[0] if not cal.empty else "n/a"

    rel_lines, rel = reliability_block(ticker, etf)

    L = [f"PAIR ANALYSIS    —    Rank {int(rrow['rank'])} / {len(RANK)}",
         "=" * 96,
         f"{ticker}   x   {etf}",
         f'Contract : "{s.get("contract_title","")}"',
         f"Sector relevance : {s.get('sector_relevance','')}",
         f"Window : {s['date_start']} to {s['date_end']}     Kalshi trades : {int(rrow['n_trades'])}"
         f"     primary bar : {bar}     daily-screen R^2 : {float(s.get('r_squared', np.nan)):.2f}",
         "",
         f">>> RELIABILITY:  {rel['tier']}   <<<   (see section 5; unreliable pairs still get figures, "
         f"but read their problems in section 8)",
         "",
         "DEFINITIONS",
         f"   xₜ₋ₖ = Kalshi yes-probability change, k bars before t   (1 bar = {bar})",
         "   yₜ   = ETF log return over bar t",
         "   calendar = full market-hours grid: x=0 in bars with no Kalshi trade (not dropped).",
         "   k>0 => Kalshi leads ETF ;  k<0 => ETF leads Kalshi ;  k=0 => contemporaneous",
         ""]
    L.append("1. CALENDAR-TIME REGRESSION (clock-time lags, full RTH grid)")
    eq1, cal_lean = expand_equation(cal, "coef", "yₜ",
        "Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE")
    L += eq1 + [""]
    L.append("2. EVENT-TIME REGRESSION (event-count lags)")
    eq2, ev_lean = expand_equation(ev, "coef", "yₜ",
        "Full model: yₜ = α + Σₖ βₖ·xₜ₋ₖ + Σᵢ φᵢ·yₜ₋ᵢ (ADL self-control) + day-FE")
    L += eq2 + [""]
    L.append("3. FULL COEFFICIENT TABLE  (calendar primary bar  vs  event)")
    L += coef_table(cal, ev) + [""]
    L.append("4. DIRECTIONAL TEST (probit, ETF up/down)")
    L += probit_block(ticker, etf) + [""]
    L.append("5. DATA RELIABILITY (statistical, not a trade-count cutoff)")
    L += rel_lines + [""]
    L.append("6. COARSE-FREQUENCY ROBUSTNESS (re-run calendar at 30min / 60min)")
    L += coarse_block(ticker, etf) + [""]
    L.append("7. VERDICT")
    L.append(f"   {verdict(cal_lean, ev_lean, int(rrow['n_sig']))}")
    if rel["tier"] in (REL.TIER_VERYLOW, REL.TIER_CANNOT):
        L.append("   (Note: this pair lacks the data to support reliable inference; the verdict above is "
                 "descriptive only -- do not put it in the conclusions.)")
    L.append("")
    L.append("8. FIGURE CAVEATS — figures are still drawn, but know their problems")
    for c in rel["fig_caveats"]:
        L.append(f"   - {c}")
    for c in caveats(cal, ev):
        L.append(f"   - {c}")
    ctx = EVENT_CONTEXT.get(ticker)
    if ctx:
        L += ["", "9. REAL-WORLD CONTEXT (WebSearch-verified; see URLs)"]
        for e in ctx:
            L.append(f"   - {e}")
    L += ["", "-" * 96,
          "Conventions: ET | 09:30-16:00 (forward windows capped to 16:00) | ETF in log return | "
          "median causal bars | full RTH grid | day-grouped lags (no overnight) | ADL self-control | "
          "significance = BH-FDR corrected.",
          "Figures for this pair follow on the next page."]
    return L


def _text_fonts():
    """等宽英文 + 中文回退：DejaVu Sans Mono 缺中文字形，matplotlib 会按列表逐字回退到中文字体。
    Monospace Latin + CJK fallback (per-glyph) so Chinese不再渲染成豆腐块。"""
    from matplotlib import font_manager
    avail = {f.name for f in font_manager.fontManager.ttflist}
    fb = next((f for f in ["Arial Unicode MS", "Heiti TC", "Songti SC", "STHeiti", "PingFang SC"]
               if f in avail), None)
    return ["DejaVu Sans Mono"] + ([fb] if fb else [])


_TEXT_FONTS = _text_fonts()


def _dw(s):
    """显示宽度：中日韩字符按 2 宽计（等宽英文 1 宽）。Display width, CJK counts as 2."""
    return sum(2 if ("⺀" <= c <= "鿿" or "＀" <= c <= "￯" or "　" <= c <= "〿")
               else 1 for c in s)


def _wrap(lines, budget=108):
    """按显示宽度折行（中文算 2 宽），在空格处断，避免中文行跑出页面。"""
    out = []
    for ln in lines:
        if _dw(ln) <= budget:
            out.append(ln); continue
        indent = " " * (len(ln) - len(ln.lstrip()) + 5)
        cur = ""
        for w in ln.split(" "):
            cand = w if cur == "" else cur + " " + w
            if cur == "" or _dw(cand) <= budget:
                cur = cand
            else:
                out.append(cur); cur = indent + w
        if cur:
            out.append(cur)
    return out


def build_text_fig(md_path, header=None):
    """读取(可能被手改过的) .md，构建文字页 figure（不落盘）。供 build_pdf 矢量直出。"""
    lines = _wrap(md_path.read_text(encoding="utf-8").splitlines())
    n = len(lines)
    fig = plt.figure(figsize=(13, max(6.0, 0.27 * n) + (0.45 if header else 0.0)))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    if header:
        fig.suptitle(header, fontsize=12, fontweight="bold", y=0.998, fontfamily=_TEXT_FONTS)
    step = 0.96 / (n + 1)
    y = 0.975 if header else 0.98
    for ln in lines:
        weight = "bold" if (ln.startswith("PAIR ANALYSIS") or (len(ln) > 2 and ln[0].isdigit() and ln[1] == ".")) else "normal"
        ax.text(0.02, y, ln, transform=ax.transAxes, family=_TEXT_FONTS, fontsize=10, va="top", ha="left", weight=weight)
        y -= step
    return fig


def render_md_to_png(md_path, png_path):
    """渲染文字页 PNG（备用；PDF 现已改矢量直出 build_text_fig）。"""
    fig = build_text_fig(md_path)
    fig.savefig(png_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    for _, rrow in RANK.iterrows():
        md = PLOTDIR / f"{rrow['tag']}_analysis.md"
        md.write_text("\n".join(generate_md(rrow)), encoding="utf-8")
        render_md_to_png(md, PLOTDIR / f"{rrow['tag']}_text.png")
    print(f"完成：为 {len(RANK)} 对生成 .md(可编辑源) + 渲染 _text.png -> {PLOTDIR}")
    print("以后改文字：直接编辑对应 *_analysis.md，再跑 build_pdf.py（勿重跑本脚本，会覆盖）。")


if __name__ == "__main__":
    main()
