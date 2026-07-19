"""
build_md.py
================================================================================
这个文件做什么 (What this file does)
  生成 leadlag_pairs_report.md —— 与 leadlag_pairs_report.pdf **逐页对应**的 Markdown 版：
  总览 -> 48 对(按 pair_ranking 排序，每对 文字 + 图) -> 4 个 merge 超信号(文字 + 图)。
  文字段用 ```text``` 代码块原样嵌入(保留公式下标与对齐)；图用 ![](相对路径) 内嵌
  (引用与 PDF 完全相同的 PNG)。这样 GitHub 上直接渲染成图文报告，替代 44MB 的 PDF。

为什么这么做 (Why)
  仓库里推 Markdown 而非 PDF：可在 GitHub 直接浏览(图自动加载)、可 diff、体积小。
  内容与 build_pdf.py 完全同源(同样的 .md 文字 + 同样的 PNG、同样顺序、同样去掉 segments)。

输出 (Output)
  leadlag_pairs_report.md（与 leadlag_pairs_report.pdf 内容一致）
"""
import re
import pandas as pd
import leadlag_common as C

PLOTDIR  = C.HERE / "plots"
MERGEDIR = C.HERE / "merge" / "plots"
RANK     = pd.read_csv(PLOTDIR / "pair_ranking.csv")
OUT_MD   = C.HERE / "leadlag_pairs_report.md"
PAIR_FIGS = ["timeseries", "zoom2", "leadglance", "leadzoom", "event", "lagcoef"]   # 与 build_pdf 同


def _fenced(md_path):
    """把一份 .md 文字原样放进代码块，保留 monospace 对齐与公式下标。
    外层 fence 用「比内容里最长 backtick 串还长」的反引号，避免内容自带的 ``` 提前闭合
    （那些内层 ``` 会原样显示，与 PDF 逐行渲染 summary.md 的效果一致）。"""
    txt = md_path.read_text(encoding="utf-8").rstrip("\n")
    longest = max((len(m) for m in re.findall(r"`+", txt)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{txt}\n{fence}\n"


def main():
    L = ["# Lead-Lag Report — Kalshi prediction markets × Vanguard sector ETFs",
         "",
         "_This Markdown mirrors `leadlag_pairs_report.pdf` in the same order: overview, then "
         f"{len(RANK)} ranked single pairs (each: text analysis + figures). "
         "Merged pooled signals live in their own report (`leadlag_merge_report.md`). "
         "Figures are the very PNGs the PDF embeds; text blocks are the same `.md` sources._",
         "",
         "**Ranking order:** has_result → n_trades → n_sig (raw p<0.15) → best_p.  "
         "**Per-pair significance:** raw p<0.15.  **ADL ETF self-lags:** chosen per pair by BIC.",
         ""]

    # ---- overview ----
    L += ["---", "", "## OVERVIEW — conclusions (graded thresholds p<0.05 / 0.10 / 0.15)", ""]
    summ = C.HERE / "leadlag_classification_summary.md"
    if summ.exists():
        L.append(_fenced(summ))
    cs = PLOTDIR / "classification_summary.png"
    if cs.exists():
        L += [f"![classification summary](plots/{cs.name})", ""]

    # ---- 48 pairs in ranking order (merge 已独立成 leadlag_merge_report，主报告不含 merge) ----
    for _, r in RANK.iterrows():
        bp = "n/a" if pd.isna(r.best_p) else f"{r.best_p:.1e}"
        noreg = "" if bool(r.has_result) else "  (no regression result)"
        L += ["---", "",
              f"## Rank {int(r['rank'])}/{len(RANK)} — {r.contract_ticker} × {r.etf}"
              f"  (n_sig={int(r.n_sig)}, best_p={bp}, n_trades={int(r.n_trades)}){noreg}", ""]
        md = PLOTDIR / f"{r.tag}_analysis.md"
        if md.exists():
            L.append(_fenced(md))
        for s in PAIR_FIGS:
            p = PLOTDIR / f"{r.tag}_{s}.png"
            if p.exists():
                L.append(f"![{r.tag} {s}](plots/{p.name})")
        L.append("")

    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"完成 -> {OUT_MD}  ({len(RANK)} single pairs + overview; merge in its own report)")


if __name__ == "__main__":
    main()
