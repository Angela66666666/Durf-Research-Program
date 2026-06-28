"""
merge_leadlag.py  (leadlag/pipeline/merge/)
================================================================================
这个文件做什么 (What this file does)
  整改 #5「合并相似合约」。把 19 个合约按大类合成 **4 个超信号**，每组成员的
  Δprob 经**符号对齐**后**池化堆叠**，对该组「相关 ETF 并集」重跑 calendar /
  event / probit 三套，以提升自由度。
  Reform #5: pool 19 contracts into 4 sign-aligned super-signals; for each,
  re-run calendar/event/probit against the union of its members' ETFs.

为什么这么做 / 关键口径 (Why / conventions)
  - **不能拼价格**：不同阈值合约(P(Trump≥281) vs ≥316)价格水平不可比，直接拼
    yes_price 会把"换合约"当成"价格跳变"。**只池化各合约自己的 Δprob**(同合约、
    同日内差分)。
  - **符号对齐**：组内反向合约(Harris 获胜、approval below、FOMC hold)乘 -1，
    使 +Δ 一致表示同一方向(更利好 Trump / 支持率更强 / 更宽松 / 油价更高)。
  - **池化回归口径(本脚本自带 run_pooled_lag_regression / run_probit_pooled)**：
      · 滞后 shift：在 (成员 × 交易日) 内做 —— 不跨合约、不跨隔夜。
      · 固定效应：**按成员(entity FE)**，只有几个虚拟变量 —— 省自由度(贴合并初衷)。
      · 标准误：**按日历日聚类** —— 吸收"同一天不同合约被同一新闻一起推"的共同冲击。
    这三处分别用不同的分组键，故不复用 common.run_joint_lag_regression(它把 shift/
    FE/聚类都绑在同一个 "date" 列上)。
    与单合约 pipeline 的 day-FE 相比，这里把 FE 粒度从"合约×日"放宽到"合约" —— 这是
    池化面板数据的标准范式(entity-FE + 时间聚类)，目的是把池化攒来的自由度真正留住，
    而不是又被上百个日固定效应吃回去。
  - 其余口径(ET / 盘内 / median 清 outlier / K 按活跃度 / BH-FDR)全部沿用 leadlag_common。

输出 (Outputs, 落在 leadlag/pipeline/merge/ 下)
  leadlag_merged_calendar_kalshi_etf.csv   每行 = 组 × ETF × 候选bar × 滞后阶
  leadlag_merged_event_kalshi_etf.csv      每行 = 组 × ETF × 滞后阶
  leadlag_merged_probit_kalshi_etf.csv     每行 = 组 × ETF × mode × 滞后阶
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

# 让本子目录能 import 上层 pipeline 的模块
PIPE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPE))
import leadlag_common as C                      # noqa: E402
from leadlag_calendar_time import bar_change    # calendar 的 median-bar 变化量  # noqa: E402

HERE = Path(__file__).resolve().parent
ADL_YLAGS  = 5
MIN_BARS   = 2 * 3 + 5      # K=3 时最小有效事件数
MIN_PROBIT = 30

# ============================ 4 个超信号定义（成员 + 符号） ============================
# +1 = 原方向计入；-1 = 反向合约，Δprob 翻转后并入，使组内 +Δ 同向。
GROUPS = {
    "ELECTION_trump_fav": {   # +Δ = 更利好 Trump
        "KXECDJT281": +1, "KXECDJT306": +1, "KXECDJT312": +1, "KXECDJT316": +1,
        "KXECKH276":  -1, "KXECKH287":  -1,                       # Harris 获胜 → 翻转
    },
    "FOMC_easing": {          # +Δ = 更宽松(降息概率上升)
        "FEDDECISION-24SEP-C25": +1, "RATECUT-24SEP18": +1, "KXFEDDECISION-24DEC-C25": +1,
        "FEDDECISION-24NOV-H0": -1, "KXFEDDECISION-24DEC-H0": -1,  # hold/不动 → 翻转
    },
    "GAS_above": {            # +Δ = 油价更高
        "AAAGASM-24OCT31-US-3.15": +1, "AAAGASM-24OCT31-US-3.20": +1,
        "AAAGASM-24SEP30-US-3.15": +1, "KXAAAGASM-24NOV30-US-3.30": +1,
    },
    "APPROVAL_strength": {    # +Δ = 支持率更强
        "538APPROVEMAX-24OCT31-T43": +1, "538APPROVEMAX-24SEP30-T43": +1,
        "KX538APPROVEMAX-24NOV30-T41": +1,
        "KX538APPROVEMIN-24NOV30-T37": -1,                         # below-37 → 翻转
    },
}


# ============================ 配置/窗口/ETF并集 ============================
def member_windows(sig: pd.DataFrame) -> dict:
    w = {}
    for tk, g in sig.groupby("contract_ticker"):
        w[tk] = (str(g["date_start"].iloc[0]), str(g["date_end"].iloc[0]))
    return w


def group_etf_union(sig: pd.DataFrame, members) -> list:
    return sorted(sig[sig["contract_ticker"].isin(members)]["etf"].unique())


# ============================ 池化回归引擎（B 口径） ============================
def run_pooled_lag_regression(df: pd.DataFrame, x_col: str, y_col: str, k: int,
                              y_lags: int = ADL_YLAGS, min_obs: int | None = None):
    """池化联合滞后回归(B口径)。df 需含列: member, date(日历日), x_col, y_col。
      - 滞后/ADL shift：在 (member, date) 内(不跨合约/隔夜)。
      - 固定效应：按 member(entity FE，少量虚拟变量，省自由度)。
      - 标准误：按 calendar date 聚类。
      - 标准化 x(除以 std)，系数可比。返回与单合约引擎同结构的系数表。
    """
    df = df.copy()
    if min_obs is None:
        min_obs = 2 * k + 5
    df["_g"] = df["member"].astype(str) + "|" + df["date"].astype(str)   # shift 用：成员×日
    g = df.groupby("_g", group_keys=False)

    lag_cols = {}
    for j in range(-k, k + 1):
        col = f"lag_{j:+d}"
        df[col] = g[x_col].shift(j)
        lag_cols[j] = col
    all_lag_cols = list(lag_cols.values())

    ylag_cols = []
    for i in range(1, y_lags + 1):
        col = f"ylag_{i}"
        df[col] = g[y_col].shift(i)
        ylag_cols.append(col)

    df = df.dropna(subset=[y_col] + all_lag_cols + ylag_cols).copy()
    if len(df) < min_obs:
        return None

    xstd = df[x_col].std()
    if xstd > 1e-12:
        for col in all_lag_cols:
            df[col] = df[col] / xstd

    # entity FE：按成员(几个虚拟变量)；若只剩一个成员则无虚拟变量
    mem_d = pd.get_dummies(df["member"], prefix="m", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df[all_lag_cols + ylag_cols].astype(float), mem_d], axis=1))
    y = df[y_col].astype(float)

    groups = df["date"].values  # 按日历日聚类
    try:
        if len(np.unique(groups)) >= 2:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        else:
            model = sm.OLS(y, X).fit(cov_type="HC3")
    except Exception as e:
        print(f"  OLS 估计失败: {e}")
        return None

    rows = []
    n_obs_final = len(df)
    n_days      = df["date"].nunique()
    n_members   = df["member"].nunique()
    n_params    = int(X.shape[1])
    n_active    = int((df[x_col].abs() > 1e-12).sum())
    for j, col in lag_cols.items():
        if col not in model.params.index:
            continue
        direction = "kalshi_leads_etf" if j > 0 else ("etf_leads_kalshi" if j < 0 else "contemp")
        rows.append({
            "k_lag": j, "direction": direction,
            "coef": model.params[col], "t_stat": model.tvalues[col], "p_value": model.pvalues[col],
            "r_squared": model.rsquared, "n_obs": n_obs_final, "n_days": n_days,
            "n_members_used": n_members, "n_params": n_params, "n_active": n_active,
        })
    return pd.DataFrame(rows)


def run_probit_pooled(df: pd.DataFrame, k: int):
    """池化方向检验。df 含 member, date, x, y。shift 在(成员×日)内、聚类按日历日(无 FE，
    与单合约 probit 一致——probit 不放 entity 虚拟变量以免分离/偏误)。"""
    d0 = df.dropna(subset=["x", "y"]).copy()
    d0 = d0[d0["y"] != 0.0]
    if len(d0) < MIN_PROBIT or d0["x"].std() < 1e-12:
        return None
    d0["up"] = (d0["y"] > 0).astype(int)
    d0["_g"] = d0["member"].astype(str) + "|" + d0["date"].astype(str)
    xstd = d0["x"].std()
    g = d0.groupby("_g", group_keys=False)
    rows = []
    for j in range(-k, k + 1):
        d = pd.DataFrame({"up": d0["up"].values,
                          "xv": (g["x"].shift(j) / xstd).values,
                          "date": d0["date"].values}).dropna()
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
        rows.append({"k_lag": j, "direction": direction, "beta": mod.params["xv"],
                     "z_stat": mod.tvalues["xv"], "p_value": mod.pvalues["xv"],
                     "pseudo_r2": mod.prsquared, "n_obs": int(len(d)), "n_up": int(d["up"].sum())})
    return pd.DataFrame(rows) if rows else None


# ============================ 数据加载 / 主 bar ============================
def load_group_kalshi(con, members_signs: dict, win: dict) -> dict:
    """{member -> (load_kalshi 后的 df, sign)}；空合约跳过。"""
    out = {}
    for tk, sign in members_signs.items():
        if tk not in win:
            print(f"    ⚠️ {tk} 不在 significant_pairs，跳过"); continue
        ds, de = win[tk]
        kdf = C.load_kalshi(con, tk, ds, de)
        if not kdf.empty:
            out[tk] = (kdf, sign)
    return out


def pooled_primary_bar(kalshi_by_member: dict) -> int:
    gaps = [C.median_intertrade_sec(k) for k, _ in kalshi_by_member.values()]
    gaps = [g for g in gaps if np.isfinite(g)]
    return C.choose_bar_sec(np.median(gaps)) if gaps else 60


# ============================ CALENDAR 池化构造 ============================
def build_calendar_pool(kalshi_by_member: dict, etf_tk: pd.DataFrame, freq: str):
    """返回 [member, date(日历日), dprob, etfret]，dprob 已符号对齐。"""
    frames = []
    for tk, (kdf, sign) in kalshi_by_member.items():
        al_cal, _ = C.build_unified_xy(kdf, etf_tk, freq)
        if al_cal is None or al_cal.empty:
            continue
        al_cal = al_cal.copy()
        al_cal["dprob"]  = al_cal["dprob"] * sign      # 符号对齐
        al_cal["member"] = tk
        frames.append(al_cal[["member", "date", "dprob", "etfret"]])
    return pd.concat(frames, ignore_index=True) if frames else None


def run_calendar(kalshi_by_member, etf_tk, bar_sec):
    pool = build_calendar_pool(kalshi_by_member, etf_tk, C.BAR_LABEL[bar_sec])
    if pool is None or pool.empty:
        return None, {"n_active": 0, "K": np.nan}
    n_active = int((pool["dprob"].abs() > 1e-12).sum())
    if n_active < MIN_BARS:
        return None, {"n_active": n_active, "K": np.nan}
    k = C.choose_k(n_active)
    res = run_pooled_lag_regression(pool, x_col="dprob", y_col="etfret", k=k)
    return res, {"n_active": n_active, "K": k}


# ============================ EVENT 池化构造 ============================
def build_event_member(kdf: pd.DataFrame, etf_tk: pd.DataFrame, sign: int, tk: str):
    """单成员 event 构造：统一因果构造(build_unified_xy)的活跃事件子序列，x=Δprob、
    y=相邻两事件间 ETF log return(后向差分，与 event_time/probit 同口径)。返回 [member, date, x, y]。"""
    med_gap = C.median_intertrade_sec(kdf)
    freq = C.BAR_LABEL[C.choose_bar_sec(med_gap if np.isfinite(med_gap) else 60)]
    _, act = C.build_unified_xy(kdf, etf_tk, freq)
    if act is None or act.empty:
        return None
    df = pd.DataFrame({"member": tk, "date": act["date"].values,
                       "x": act["dprob_e"].values * sign,   # 符号对齐
                       "y": act["etfret_e"].values})
    return df.dropna(subset=["x", "y"])


def run_event(kalshi_by_member, etf_tk):
    frames = []
    for tk, (kdf, sign) in kalshi_by_member.items():
        m = build_event_member(kdf, etf_tk, sign, tk)
        if m is not None and not m.empty:
            frames.append(m)
    if not frames:
        return None, {"n_active": 0, "K": np.nan}
    pool = pd.concat(frames, ignore_index=True)
    if len(pool) < MIN_BARS:
        return None, {"n_active": len(pool), "K": np.nan}
    k = C.choose_k(len(pool))
    res = run_pooled_lag_regression(pool, x_col="x", y_col="y", k=k)
    return res, {"n_active": len(pool), "K": k}


# ============================ PROBIT 池化构造（calendar + event 两套） ============================
def build_probit_calendar_pool(kalshi_by_member, etf_tk, freq):
    """返回 [member, date, x, y]（calendar 口径，x 符号对齐）。"""
    frames = []
    for tk, (kdf, sign) in kalshi_by_member.items():
        kb = bar_change(kdf, "prob", "x", freq, "kalshi")
        eb = bar_change(etf_tk, "mid", "y", freq, "etf")
        if kb.empty or eb.empty:
            continue
        m = pd.merge(kb[["ts_et", "x", "date"]], eb[["ts_et", "y"]], on="ts_et", how="inner")
        if m.empty:
            continue
        m["x"] = m["x"] * sign
        m["member"] = tk
        frames.append(m[["member", "date", "x", "y"]])
    return pd.concat(frames, ignore_index=True) if frames else None


def run_probit_both(kalshi_by_member, etf_tk, primary_freq):
    out = []
    cal_pool = build_probit_calendar_pool(kalshi_by_member, etf_tk, primary_freq)
    if cal_pool is not None and len(cal_pool) >= MIN_PROBIT:
        k = C.choose_k(len(cal_pool))
        res = run_probit_pooled(cal_pool, k)
        if res is not None and not res.empty:
            res["mode"] = "calendar"; res["bar"] = primary_freq
            res["K_chosen"] = k; res["n_total"] = len(cal_pool)
            out.append(res)
    ev_frames = []
    for tk, (kdf, sign) in kalshi_by_member.items():
        m = build_event_member(kdf, etf_tk, sign, tk)
        if m is not None and not m.empty:
            ev_frames.append(m)
    if ev_frames:
        ev_pool = pd.concat(ev_frames, ignore_index=True)
        if len(ev_pool) >= MIN_PROBIT:
            k = C.choose_k(len(ev_pool))
            res = run_probit_pooled(ev_pool, k)
            if res is not None and not res.empty:
                res["mode"] = "event"; res["bar"] = "event(active)"
                res["K_chosen"] = k; res["n_total"] = len(ev_pool)
                out.append(res)
    return out


# ============================ 主流程 ============================
def main():
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    win = member_windows(sig)

    cal_out, ev_out, pro_out = [], [], []
    print("=" * 80)
    print(f"合并合约 Lead-Lag (B口径: 成员FE + 按日聚类) | 4 超信号 × 相关ETF并集 | "
          f"calendar+event+probit | TZ={C.TZ} | 盘内 09:30-16:00")
    print("=" * 80)

    for gname, members_signs in GROUPS.items():
        etfs = group_etf_union(sig, list(members_signs))
        kbm = load_group_kalshi(con, members_signs, win)
        if not kbm:
            print(f"\n[{gname}] 无任何成员数据，跳过"); continue
        primary_sec = pooled_primary_bar(kbm)
        n_trades = sum(len(k) for k, _ in kbm.values())
        print(f"\n[{gname}] 成员={len(kbm)} 池化成交={n_trades} 主bar={C.BAR_LABEL[primary_sec]} "
              f"ETF并集={etfs}")

        for etf in etfs:
            etf_tk = C.load_etf(con, etf, min(win[t][0] for t in kbm), max(win[t][1] for t in kbm))
            if etf_tk.empty:
                print(f"    {etf}: ETF 无数据，跳过"); continue

            ca = None
            for bar_sec in C.BAR_GRID_SEC:
                res, meta = run_calendar(kbm, etf_tk, bar_sec)
                if res is None or res.empty:
                    continue
                res["group"] = gname; res["etf"] = etf; res["mode"] = "calendar"
                res["bar_freq"] = C.BAR_LABEL[bar_sec]; res["bar_sec"] = bar_sec
                res["is_primary_bar"] = (bar_sec == primary_sec)
                res["K_chosen"] = meta["K"]; res["n_active_bars"] = meta["n_active"]
                res["n_members"] = len(kbm)
                cal_out.append(res); ca = meta["n_active"]

            res, meta = run_event(kbm, etf_tk)
            ev_ok = res is not None and not res.empty
            if ev_ok:
                res["group"] = gname; res["etf"] = etf; res["mode"] = "event"
                res["K_chosen"] = meta["K"]; res["n_active_events"] = meta["n_active"]
                res["n_members"] = len(kbm)
                ev_out.append(res)

            for res in run_probit_both(kbm, etf_tk, C.BAR_LABEL[primary_sec]):
                res["group"] = gname; res["etf"] = etf; res["n_members"] = len(kbm)
                pro_out.append(res)

            print(f"    {etf}: cal_active≈{ca}  event{'✓' if ev_ok else '·'}")

    def _save(rows, fname, fdr_cols):
        if not rows:
            print(f"  {fname}: 无结果"); return
        df = pd.concat(rows, ignore_index=True)
        df = C.add_fdr(df, fdr_cols)
        df.to_csv(HERE / fname, index=False)
        print(f"  {fname}: {len(df)} 行，p<0.05 显著 {(df['p_value'] < 0.05).sum()}")

    print("\n" + "=" * 80)
    _save(cal_out, "leadlag_merged_calendar_kalshi_etf.csv", ["group", "etf", "bar_sec"])
    _save(ev_out,  "leadlag_merged_event_kalshi_etf.csv",    ["group", "etf"])
    _save(pro_out, "leadlag_merged_probit_kalshi_etf.csv",   ["group", "etf", "mode"])
    print("完成 -> leadlag/pipeline/merge/")


if __name__ == "__main__":
    main()
