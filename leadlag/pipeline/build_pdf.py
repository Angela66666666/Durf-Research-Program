"""
build_pdf.py
================================================================================
这个文件做什么 (What this file does)
  把全部 48 组按「最能说明问题在前」的顺序拼成一个 PDF 报告：每组一页文字分析 + 一页图。
  Assemble all 48 pairs into one PDF report, "most-illustrative-first": each pair
  gets a text page + a figure page.

为什么这么做 (Why)
  需要一份能通读全部 48 对的单一报告；排序让有信号的对在前、稀疏无结果的在后。
  A single readable report over all 48 pairs, ordered so signal-bearing pairs come
  first and sparse/no-result pairs come last.

思路 (Approach)
  - 顺序读自 plots/pair_ranking.csv
  - 文字页：从可编辑的 .md **矢量直出**（不过 PNG，文字清晰可选中、且手改 .md 即时生效）
  - 图页：全窗 -> zoom2 -> leadglance -> 分段 -> event -> 滞后系数；源 PNG 已 200dpi、拼页关插值
  - 页眉标注排名、合约名称、关键统计

输出 (Output)
  leadlag_pairs_report.pdf（96 页 = 48 对 × (文字页 + 图页)）
  存放位置：leadlag/pipeline/ 下

函数 (Functions)
  add_stacked_page  把若干图按真实高宽比竖排成一页（关插值、200dpi）
  overview_pages    报告首页：全局分类总览图（含统计可靠性维度）
  page_for_group    生成一对的文字页(矢量) + 图页
  main              先放总览页，再按排序逐对拼页、写出 PDF
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

import leadlag_common as C
import make_pair_text as MPT   # 复用 .md -> png 渲染（保证用最新(可能手改过)的 .md）

PLOTDIR = C.HERE / "plots"
RANK    = pd.read_csv(PLOTDIR / "pair_ranking.csv")
OUT_PDF = C.HERE / "leadlag_pairs_report.pdf"


def add_stacked_page(pdf, img_paths, header=None):
    """把若干图按真实高宽比竖排成一页。源 PNG 已 200dpi，这里关插值、200dpi 输出避免二次模糊。"""
    imgs = [p for p in img_paths if p.exists()]
    if not imgs:
        return
    arrs = [plt.imread(p) for p in imgs]
    W = 13.0
    heights = [W * a.shape[0] / a.shape[1] for a in arrs]
    fig = plt.figure(figsize=(W, (0.6 if header else 0.1) + sum(heights)))
    gs = fig.add_gridspec(len(arrs), 1, height_ratios=heights, hspace=0.03)
    if header:
        fig.suptitle(header, fontsize=12, fontweight="bold", y=0.998)
    for ax_i, arr in enumerate(arrs):
        ax = fig.add_subplot(gs[ax_i]); ax.imshow(arr, aspect="auto", interpolation="none"); ax.axis("off")
    pdf.savefig(fig, dpi=200, bbox_inches="tight")
    plt.close(fig)


def page_for_group(pdf, row):
    bp = "n/a" if pd.isna(row.best_p) else f"{row.best_p:.1e}"
    head = (f"Rank {int(row['rank'])}/{len(RANK)}   |   {row.contract_ticker} × {row.etf}   |   "
            f"n_sig={int(row.n_sig)}   best_p={bp}   n_trades={int(row.n_trades)}"
            f"{'   (no regression result)' if not bool(row.has_result) else ''}")
    # 第1页：文字分析——矢量直出（从可编辑的 .md 重建，文字无限清晰，不过 PNG）
    md = PLOTDIR / f"{row.tag}_analysis.md"
    if md.exists():
        fig = MPT.build_text_fig(md, header=head)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    # 第2页：图（全窗 → 增强放大 → 分段 → event → 滞后系数）
    figs = ["timeseries", "zoom2", "leadglance", "segments", "event", "lagcoef"]
    add_stacked_page(pdf, [PLOTDIR / f"{row.tag}_{s}.png" for s in figs], header=None)


def overview_pages(pdf):
    """报告首页：分类总览图（按合约类型/板块/统计可靠性看谁领先）+ 可靠性说明。"""
    summ = PLOTDIR / "classification_summary.png"
    head = ("OVERVIEW — Lead/Lag classification across all 48 pairs   |   "
            "reliability = df-based (not a trade-count cutoff)")
    if summ.exists():
        add_stacked_page(pdf, [summ], header=head)


def main():
    print(f"按排序拼 {len(RANK)} 组（每组 文字页+图页）-> {OUT_PDF}")
    with PdfPages(OUT_PDF) as pdf:
        overview_pages(pdf)
        for _, row in RANK.iterrows():
            page_for_group(pdf, row)
            print(f"  rank {int(row['rank']):>2}: {row.contract_ticker} × {row.etf}")
    print(f"完成 -> {OUT_PDF}")


if __name__ == "__main__":
    main()
