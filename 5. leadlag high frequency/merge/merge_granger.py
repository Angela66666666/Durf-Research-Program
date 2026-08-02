"""
merge_granger.py  (leadlag/pipeline/merge/)
================================================================================
这个文件做什么 (What this file does)
  对 4 个合并池化信号做标准 Granger 联合检验（headline 统计量的池化版）。
  把每个池化信号当「一个合成合约」，对其相关 ETF 并集里的每个 ETF，跑：
    linear·Pooled→ETF :  etfret = a + Σφ·etfret_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j} + 成员FE
    linear·ETF→Pooled :  Δprob  = c + Σψ·Δprob_{t-i}  + Σ_{j=1..K} d_j·etfret_{t-j} + 成员FE
    probit·Pooled→ETF :  Pr(ETF↑)=Φ(α + Σφ·↑_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j})
  各检验 H0: 那组 cause 滞后系数同时为 0 → 一个 p 值。

口径 (Conventions — 沿用 merge_leadlag 的池化范式 + Granger 的 SE)
  - 池化：成员 Δprob 符号对齐后堆叠(不拼价格)；shift 在 (成员×日) 内、不跨合约/隔夜。
  - 固定效应：linear 按成员(entity FE)；probit 不放 FE(与 merge_leadlag 一致，避免分离)。
  - 标准误：**面板 Newey-West(hac-panel，按 成员×日 分组)**——满秩、联合 Wald 恒有效
    (与单合约 Granger 同口径；理由见 GRANGER_TEST.md)。被解释变量自身滞后阶由 BIC 自选。

输出 (Output, 落在 leadlag/pipeline/merge/ 下)
  leadlag_merged_granger.csv —— 每行 = group × etf × mode × spec × direction
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

PIPE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PIPE))
import leadlag_common as C                      # noqa: E402
import merge_leadlag as M                       # GROUPS / 池化构造 / 窗口  # noqa: E402

HERE    = Path(__file__).resolve().parent
OUT_CSV = HERE / "leadlag_merged_granger.csv"
# 唯一门槛：n_active(非零 cause 观测数) >= 2K+5(K=3)。linear 与 probit 共用，
# 与单对驱动 leadlag_granger.py 一致；不再对 probit 另设主观的 len>=30。
MIN_BARS = 2 * 3 + 5


def _n_active(df, col):
    """有信息量的观测数 = cause 真正变动过的行数（平静 bar 不提供识别力）。"""
    return 0 if df is None or df.empty else int((df[col].abs() > 1e-12).sum())


def _panel_groups(df):
    """(成员×日) 面板块标签，供 hac-panel 在块内算 Newey-West。"""
    return pd.factorize(df["member"].astype(str) + "|" + df["date"].astype(str))[0]


def run_granger_pooled(df: pd.DataFrame, cause_col: str, effect_col: str, k: int,
                       own_lags="auto", min_obs: int | None = None):
    """池化单向 Granger(linear)。df 含 member, date, cause_col, effect_col。
       成员 FE + (成员×日)内 shift + hac-panel(成员×日) SE + cause block 的 Wald。"""
    df = df.copy()
    if min_obs is None:
        min_obs = 2 * k + 5
    df["_g"] = df["member"].astype(str) + "|" + df["date"].astype(str)
    g = df.groupby("_g", group_keys=False)

    cause_cols = []
    for j in range(1, k + 1):
        col = f"causelag_{j}"
        df[col] = g[cause_col].shift(j)
        cause_cols.append(col)

    pmax = max(0, min(k, C.ADL_PMAX))
    if isinstance(own_lags, str) and own_lags.lower() == "auto":
        el_full = {f"efflag_{i}": g[effect_col].shift(i) for i in range(1, pmax + 1)}
        etmp = pd.DataFrame(el_full, index=df.index)
        common = df.assign(**{c: etmp[c] for c in etmp.columns})
        common = common.dropna(subset=[effect_col] + cause_cols + list(etmp.columns))
        if pmax > 0 and len(common) >= min_obs:
            cX = common[cause_cols].astype(float)
            cs0 = common[cause_col].std()
            if cs0 > 1e-12:
                cX = cX / cs0
            fe = pd.get_dummies(common["member"], prefix="m", drop_first=True, dtype=float)
            p = C.choose_adl_order(common[effect_col], cX, common[list(etmp.columns)].astype(float), fe, pmax)
        else:
            p = 0
    else:
        p = int(own_lags)

    eff_cols = []
    for i in range(1, p + 1):
        col = f"efflag_{i}"
        df[col] = g[effect_col].shift(i)
        eff_cols.append(col)

    df = df.dropna(subset=[effect_col] + cause_cols + eff_cols).copy()
    if len(df) < min_obs:
        return None
    cs = df[cause_col].std()
    if cs > 1e-12:
        for col in cause_cols:
            df[col] = df[col] / cs

    df = df.sort_values(["member", "date"], kind="stable")
    mem_d = pd.get_dummies(df["member"], prefix="m", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df[cause_cols + eff_cols].astype(float), mem_d], axis=1))
    y = df[effect_col].astype(float)
    try:
        model = sm.OLS(y, X).fit(cov_type="hac-panel",
                                 cov_kwds={"groups": _panel_groups(df), "maxlags": max(1, k)})
    except Exception as e:
        print(f"    pooled Granger OLS 失败: {e}"); return None

    names = list(X.columns)
    R = np.zeros((len(cause_cols), len(names)))
    for r, c in enumerate(cause_cols):
        R[r, names.index(c)] = 1.0
    try:
        wt = model.wald_test(R, scalar=True, use_f=False)
        chi2, pval = float(np.squeeze(wt.statistic)), float(np.squeeze(wt.pvalue))
    except Exception:
        return None
    return {"K": k, "wald_df": len(cause_cols), "n_ylags": p, "wald_chi2": chi2, "p_value": pval,
            "n_obs": int(len(df)), "n_days": int(df["date"].nunique()),
            "n_members": int(df["member"].nunique()),
            "n_active": int((df[cause_col].abs() > 1e-12).sum()),
            "cov_type": "hac-panel"}   # linear 无退回：hac-panel 失败直接返回 None


def run_granger_probit_pooled(df: pd.DataFrame, x_col: str, y_col: str, k: int,
                              own_lags="auto", min_obs: int | None = None):
    """池化 probit Granger(仅 Pooled→ETF)。df 含 member, date, x, y。无 FE(与 merge_leadlag 一致)。
    最小样本量与 linear 同一套推导(2k+5)，不用主观的固定 30。"""
    if min_obs is None:
        min_obs = 2 * k + 5
    d0 = df.dropna(subset=[x_col, y_col]).copy()
    d0 = d0[d0[y_col] != 0.0]
    if len(d0) < min_obs or d0[x_col].std() < 1e-12:
        return None
    d0["up"] = (d0[y_col] > 0).astype(int)
    d0["_g"] = d0["member"].astype(str) + "|" + d0["date"].astype(str)
    g = d0.groupby("_g", group_keys=False)
    xstd = d0[x_col].std()

    cause_cols = []
    for j in range(1, k + 1):
        col = f"causelag_{j}"
        d0[col] = g[x_col].shift(j) / xstd
        cause_cols.append(col)
    pmax = max(0, min(k, C.ADL_PMAX))
    up_full = {f"uplag_{i}": g["up"].shift(i) for i in range(1, pmax + 1)}
    utmp = pd.DataFrame(up_full, index=d0.index)
    common = d0.assign(**{c: utmp[c] for c in utmp.columns})
    common = common.dropna(subset=["up"] + cause_cols + list(utmp.columns))
    if len(common) < min_obs or common["up"].nunique() < 2:
        return None
    if isinstance(own_lags, str) and own_lags.lower() == "auto":
        best_p, best_bic = 0, np.inf
        for p in range(0, pmax + 1):
            cols = cause_cols + [f"uplag_{i}" for i in range(1, p + 1)]
            Xc = sm.add_constant(common[cols].astype(float))
            try:
                mp = sm.Probit(common["up"].astype(float), Xc).fit(disp=0, maxiter=200)
            except Exception:
                continue
            if np.isfinite(mp.bic) and mp.bic < best_bic:
                best_bic, best_p = mp.bic, p
        p = best_p
    else:
        p = int(own_lags)

    use_cols = cause_cols + [f"uplag_{i}" for i in range(1, p + 1)]
    fit = common.dropna(subset=["up"] + use_cols).sort_values(["member", "date"], kind="stable")
    if len(fit) < min_obs or fit["up"].nunique() < 2:
        return None
    X = sm.add_constant(fit[use_cols].astype(float))
    yv = fit["up"].astype(float)
    try:
        try:
            model = sm.Probit(yv, X).fit(disp=0, maxiter=200, cov_type="hac-panel",
                                         cov_kwds={"groups": _panel_groups(fit), "maxlags": max(1, k)})
            cov_used = "hac-panel"
        except Exception:
            model = sm.Probit(yv, X).fit(disp=0, maxiter=200)
            cov_used = "default"   # hac-panel 失败退回普通标准误，记录下来供事后甄别
    except Exception:
        return None
    names = list(X.columns)
    R = np.zeros((len(cause_cols), len(names)))
    for r, c in enumerate(cause_cols):
        R[r, names.index(c)] = 1.0
    try:
        wt = model.wald_test(R, scalar=True, use_f=False)
        chi2, pval = float(np.squeeze(wt.statistic)), float(np.squeeze(wt.pvalue))
    except Exception:
        return None
    return {"K": k, "wald_df": len(cause_cols), "n_ylags": p, "wald_chi2": chi2, "p_value": pval,
            "n_obs": int(len(fit)), "n_days": int(fit["date"].nunique()),
            "n_members": int(fit["member"].nunique()),
            "n_active": int((fit[cause_cols[0]].abs() > 1e-12).sum()) if cause_cols else 0,
            "cov_type": cov_used}


def _emit(g, group, etf, mode, spec, direction):
    row = {"group": group, "etf": etf, "mode": mode, "spec": spec, "direction": direction}
    row.update(g); return row


def main():
    con = C.make_con()
    sig = pd.read_csv(C.SIG_PAIRS_CSV)
    win = M.member_windows(sig)
    print("=" * 80)
    print("合并池化信号 Granger 联合检验  |  linear 双向 + probit(S→E)  |  hac-panel(成员×日)")
    print("=" * 80)

    out = []
    etf_cache: dict = {}   # (etf, ds, de) -> df；同一 ETF 在多个组里复用，不重复读 DuckDB

    def _load_etf_cached(etf, ds, de):
        key = (etf, ds, de)
        if key not in etf_cache:
            etf_cache[key] = C.load_etf(con, etf, ds, de)
        return etf_cache[key]

    for gname, members_signs in M.GROUPS.items():
        etfs = M.group_etf_union(sig, list(members_signs))
        kbm = M.load_group_kalshi(con, members_signs, win)
        if not kbm:
            print(f"\n[{gname}] 无成员数据，跳过"); continue
        primary = C.BAR_LABEL[M.pooled_primary_bar(kbm)]
        # 窗口对整个组是固定的，提到 ETF 循环外算一次
        ds_g = min(win[t][0] for t in kbm)
        de_g = max(win[t][1] for t in kbm)
        print(f"\n[{gname}] 成员={len(kbm)} 主bar={primary} ETF并集={etfs}")
        for etf in etfs:
            etf_tk = _load_etf_cached(etf, ds_g, de_g)
            if etf_tk.empty:
                print(f"    {etf}: ETF 无数据"); continue

            # ---- calendar（池化主 bar 网格）：linear 双向 + probit 共用同一张 cal ----
            cal = M.build_calendar_pool(kbm, etf_tk, primary)
            n_cal = _n_active(cal, "dprob")
            if n_cal >= MIN_BARS:
                k = C.choose_k(n_cal)
                for cause, eff, d in [("dprob", "etfret", "kalshi->etf"), ("etfret", "dprob", "etf->kalshi")]:
                    g = run_granger_pooled(cal, cause, eff, k)
                    if g: out.append(_emit(g, gname, etf, "calendar", "linear", d))
                cal_pro = cal.rename(columns={"dprob": "x", "etfret": "y"})
                g = run_granger_probit_pooled(cal_pro, "x", "y", k)
                if g: out.append(_emit(g, gname, etf, "calendar", "probit", "kalshi->etf"))

            # ---- event（池化活跃事件）：只 concat 一次，linear 双向 + probit 共用同一张 ev ----
            evf = [M.build_event_member(kdf, etf_tk, sign, tk) for tk, (kdf, sign) in kbm.items()]
            evf = [m for m in evf if m is not None and not m.empty]
            if evf:
                ev = pd.concat(evf, ignore_index=True)
                n_evt = _n_active(ev, "x")
                if n_evt >= MIN_BARS:
                    k = C.choose_k(n_evt)
                    for cause, eff, d in [("x", "y", "kalshi->etf"), ("y", "x", "etf->kalshi")]:
                        g = run_granger_pooled(ev, cause, eff, k)
                        if g: out.append(_emit(g, gname, etf, "event", "linear", d))
                    g = run_granger_probit_pooled(ev, "x", "y", k)
                    if g: out.append(_emit(g, gname, etf, "event", "probit", "kalshi->etf"))
            print(f"    {etf}: done")

    if not out:
        print("\n无结果。"); return
    df = pd.DataFrame(out)
    # 多重检验校正：检验族 = 同一 (mode, spec, direction) 下跨所有 组×ETF 的联合 Wald p
    df = C.add_fdr(df, ("mode", "spec", "direction"), pcol="p_value", outcol="p_fdr")
    cols = ["group", "etf", "mode", "spec", "direction", "K", "n_ylags", "wald_chi2",
            "wald_df", "p_value", "p_fdr", "n_obs", "n_days", "n_members", "n_active", "cov_type"]
    df = df[cols]
    df.to_csv(OUT_CSV, index=False)
    print(f"\n完成 -> {OUT_CSV}  ({len(df)} 行)")
    for mode in ("calendar", "event"):
        lin = df[(df["mode"] == mode) & (df["spec"] == "linear")]
        kl = lin[(lin.direction == "kalshi->etf") & (lin.p_value < 0.05)]
        el = lin[(lin.direction == "etf->kalshi") & (lin.p_value < 0.05)]
        print(f"{mode:9}: linear Pooled→ETF 显著={len(kl)}  ETF→Pooled 显著={len(el)}  (共 {lin['group'].nunique()} 组×多ETF)")


if __name__ == "__main__":
    main()
