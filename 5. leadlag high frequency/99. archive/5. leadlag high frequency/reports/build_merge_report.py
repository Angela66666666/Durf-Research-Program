"""
build_merge_report.py
================================================================================
这个文件做什么 (What this file does)
  把 merge 池化信号单独拼成一份**专属报告**(PDF + 内容一模一样的 MD)：
    每个池化信号一节 = 池化总览(成员/符号/各ETF分级方向表 + lagcoef 网格) +
    其下「该类 × 每个 ETF」逐个伪 pair(文字方向表 + 6 张图，与单对同格式)。
  主报告(leadlag_pairs_report)已不含 merge，merge 全部在这里。

为什么 (Why)
  合并合约的「类×ETF」共 ~37 个伪 pair、~222 张图，单独成册更清楚；
  且合并合约是「合成指数」(累加符号对齐 Δprob)，与单合约报告分开避免混淆。

输入 (Inputs, 由这些脚本先生成)
  merge/leadlag_merged_{calendar,event,probit}_*.csv  (merge_leadlag.py)
  merge/plots/merge_{group}_analysis.md, _lagcoef.png  (make_merge_pages.py)
  merge/plots/merge_{group}_{etf}_*.png, _analysis.md, merge_pairs_order.csv  (make_merge_pair_plots.py)

输出 (Outputs, 落在 leadlag/pipeline/ 下)
  leadlag_merge_report.pdf   (本地查看, 不入库)
  leadlag_merge_report.md    (入库, 图用相对路径内嵌, GitHub 直接渲染)
"""
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

import leadlag_common as C
import make_pair_text as MPT          # 复用 .md -> 矢量文字页

MERGEDIR = C.HERE / "merge" / "plots"
ORDER    = pd.read_csv(MERGEDIR / "merge_order.csv")          # 组顺序
PAIRS    = pd.read_csv(MERGEDIR / "merge_pairs_order.csv")    # (group, etf) 顺序
COMBO_FIGS = ["timeseries", "zoom2", "leadglance", "leadzoom", "event", "lagcoef"]
OUT_PDF  = C.HERE / "leadlag_merge_report.pdf"
OUT_MD   = C.HERE / "leadlag_merge_report.md"


# ---------------- PDF helpers ----------------
def _stack(pdf, img_paths, header=None):
    imgs = [p for p in img_paths if p.exists()]
    if not imgs:
        return
    arrs = [plt.imread(p) for p in imgs]
    W = 13.0
    heights = [W * a.shape[0] / a.shape[1] for a in arrs]
    fig = plt.figure(figsize=(W, (0.5 if header else 0.1) + sum(heights)))
    gs = fig.add_gridspec(len(arrs), 1, height_ratios=heights, hspace=0.03)
    if header:
        fig.suptitle(header, fontsize=12, fontweight="bold", y=0.999)
    for i, a in enumerate(arrs):
        ax = fig.add_subplot(gs[i]); ax.imshow(a, aspect="auto", interpolation="none"); ax.axis("off")
    pdf.savefig(fig, dpi=200, bbox_inches="tight"); plt.close(fig)


def _text_page(pdf, md_path, header):
    if md_path.exists():
        fig = MPT.build_text_fig(md_path, header=header)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def build_pdf():
    print(f"拼 merge 专属 PDF -> {OUT_PDF}")
    with PdfPages(OUT_PDF) as pdf:
        # 封面说明
        intro = C.HERE / "_merge_report_intro.md"
        intro.write_text(_INTRO, encoding="utf-8")
        _text_page(pdf, intro, header="MERGE REPORT — pooled signals as combined contracts")
        for _, gr in ORDER.iterrows():
            g = gr["group"]
            _text_page(pdf, MERGEDIR / f"merge_{g}_analysis.md",
                       header=f"MERGE {g} — pooled overview (all member ETFs)")
            _stack(pdf, [MERGEDIR / f"merge_{g}_lagcoef.png"])
            for etf in PAIRS[PAIRS["group"] == g]["etf"]:
                tag = f"merge_{g}_{etf}"
                _text_page(pdf, MERGEDIR / f"{tag}_analysis.md", header=f"{g} (combined)  ×  {etf}")
                _stack(pdf, [MERGEDIR / f"{tag}_{s}.png" for s in COMBO_FIGS])
                print(f"  {g} × {etf}")
        intro.unlink(missing_ok=True)
    print(f"完成 -> {OUT_PDF}")


# ---------------- MD ----------------
def _fenced(md_path):
    txt = md_path.read_text(encoding="utf-8").rstrip("\n")
    longest = max((len(m) for m in re.findall(r"`+", txt)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}text\n{txt}\n{fence}\n"


def build_md():
    L = ["# MERGE Report — pooled signals as combined contracts", "", _INTRO, ""]
    for _, gr in ORDER.iterrows():
        g = gr["group"]
        L += ["---", "", f"## MERGE — {g}  (pooled overview)", ""]
        gmd = MERGEDIR / f"merge_{g}_analysis.md"
        if gmd.exists():
            L.append(_fenced(gmd))
        gpng = MERGEDIR / f"merge_{g}_lagcoef.png"
        if gpng.exists():
            L += [f"![{g} lagcoef](merge/plots/{gpng.name})", ""]
        for etf in PAIRS[PAIRS["group"] == g]["etf"]:
            tag = f"merge_{g}_{etf}"
            L += ["", f"### {g} (combined)  ×  {etf}", ""]
            cmd = MERGEDIR / f"{tag}_analysis.md"
            if cmd.exists():
                L.append(_fenced(cmd))
            for s in COMBO_FIGS:
                p = MERGEDIR / f"{tag}_{s}.png"
                if p.exists():
                    L.append(f"![{tag} {s}](merge/plots/{p.name})")
            L.append("")
    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    print(f"完成 -> {OUT_MD}  ({len(PAIRS)} 个 类×ETF)")


_INTRO = (
    "Each pooled signal is treated as one **combined contract**: members' Δprob are sign-aligned "
    "(reverse contracts ×-1) and pooled — never their price levels (different thresholds are not "
    "comparable). *Sign-aligned* means each member's Δprob is multiplied by ±1 so that a positive value "
    "always denotes the same real-world direction; the **continuous magnitude of Δprob is preserved** — "
    "moves are not discretized to ±1. The combined 'contract line' shown in the time-series figures is a "
    "**synthetic index** "
    "= cumulative bar-by-bar mean of the members' sign-aligned Δprob (start 0.5, in pp); it is NOT a real "
    "probability, only a carrier for visualizing the group's information flow. Each section: pooled overview "
    "(per-ETF graded-threshold direction table + lag-coef grid), then one pseudo-pair per ETF (combined "
    "contract × that ETF) with the same 6 figures + a direction table as the single-pair report. "
    "Regression: per-member fixed effects, day-clustered SE, ADL self-lags chosen by BIC; direction counts "
    "use raw p at p<0.05 / 0.10 / 0.15."
)


def main():
    build_md()
    build_pdf()


if __name__ == "__main__":
    main()
