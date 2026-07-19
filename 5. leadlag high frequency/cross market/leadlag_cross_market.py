import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Tuple, Optional
from pathlib import Path

# ====================== 全局可配置超参数 ======================
HERE = Path(__file__).parent
# 按老师的建议：不再写死绝对路径。所有输入数据统一放在项目文件夹下的 data/ 里，
# 再用"快捷方式"(Windows) 或"符号链接"(macOS/Linux) 把 data/ 指向你电脑上实际存数据的地方。
# 这样脚本本身只认 data/ 这个相对路径，换一台电脑跑，只需要重新建一个指向新位置的
# 快捷方式/符号链接，代码完全不用改。
#
# 路径不再依赖手工建立的符号链接：向上查找含 "1. data" 的目录作为项目根，
# 所以这个脚本放在任何机器、任何深度都能直接跑。
PROJ_ROOT = HERE
while PROJ_ROOT != PROJ_ROOT.parent and not (PROJ_ROOT / "1. data").is_dir():
    PROJ_ROOT = PROJ_ROOT.parent
DATA_DIR   = PROJ_ROOT / "1. data"
ETF_HF_DIR = DATA_DIR / "etf_hf"
TRADES_DIR = DATA_DIR / "kalshi" / "kalshi" / "trades"

# Model B / C 的真实配对表（与本脚本同目录，由 generate_pairs.py 生成）
PAIR_CONTRACT_CSV = HERE / "pair_contract.csv"
PAIR_ETF_CSV      = HERE / "pair_etf.csv"

print("ETF文件夹路径：", ETF_HF_DIR.resolve(), "存在？", ETF_HF_DIR.exists())

# 输出
OUT_CONTRACT_CONTR = HERE / "leadlag_calendar_contract_contract.csv"
OUT_ETF_ETF        = HERE / "leadlag_calendar_etf_etf.csv"
OUT_CONTRACT_SELF  = HERE / "leadlag_calendar_contract_self.csv"
OUT_ETF_SELF       = HERE / "leadlag_calendar_etf_self.csv"

# 回归设定
K               = 10          # 前后K个bar的滞后阶数（calendar-time下，k就是 k*BAR_FREQ 秒）
MIN_OBS         = 2 * K + 5    # 滞后构造后最小样本量（下限保护）
MIN_DOF         = 10           # 新增：最小自由度要求。dof = n_obs - (滞后变量数+日FE数+1截距)。
                                # 之前contract-contract的n_obs只有33~99，却要塞21个滞后参数
                                # +若干日FE虚拟变量，自由度极度紧张，OLS在数值上能跑出来，
                                # 但估计量本身不可信（标准误虚低、系数不稳定）。
                                # 下面用"自适应缩小K"的方式来保证每一行结果都满足这个底线。
RUN_MODEL_B     = True         # 跨合约 benchmark（需要 pair_contract.csv）
RUN_MODEL_C     = True         # 跨 ETF benchmark（需要 pair_etf.csv）
RUN_MODEL_B_SELF = True        # 教授要求：单个合约 自己现在 vs 自己k个bar前（自相关）
RUN_MODEL_C_SELF = True        # 教授要求：单个ETF   自己现在 vs 自己k个bar前（自相关）
ADL_PMAX        = 6            # Granger/ADL 中 effect 自身滞后阶数的 BIC 搜索上限

# ---- Calendar-time bar 频率：这是本次修改的核心 ----
ETF_BAR_FREQ      = "5s"   # ETF↔ETF：你要求先用5秒
CONTRACT_BAR_FREQ = "600s" # Kalshi合约↔合约：根据实测median inter-trade gap（多数合约
                            # 在87s~52335s之间，大量>>30s）调大到120s，
                            # 让大多数合约在每个bar里更可能有真实成交，
                            # 避免降采样后绝大多数bar为空、merge后样本量<MIN_OBS。
                            # 如果调整后仍有很多pair样本不足，可以继续调大到300s。

CONTRACT_MAX_GAP_SEC = int(pd.Timedelta(CONTRACT_BAR_FREQ).total_seconds())
                            # 合约部分(Model B)的merge_asof容忍度，必须跟着
                            # CONTRACT_BAR_FREQ 一起变，否则bar调大后容忍度还固定
                            # 在120s，会导致大量本该匹配上的bar因为"中心点距离
                            # 超过容忍度"被错误丢弃（这是之前Model B全军覆没的真实原因之一）。

ETF_MAX_GAP_SEC = int(pd.Timedelta(ETF_BAR_FREQ).total_seconds())
                            # ETF部分(Model C)的merge_asof容忍度，同样跟着
                            # ETF_BAR_FREQ走。之前固定写死120s、而bar=5s，
                            # 相当于容忍度是bar宽度的24倍——当两边都落在同一个5s
                            # 网格上时通常是精确匹配，所以实际影响不大，但这是口径
                            # 不一致的隐患，必须和Model B保持同样的"容忍度=跟着bar走"
                            # 的逻辑，不能一个改了一个没改。

# ---- 美股常规交易时段（仅用于ETF，过滤掉盘前盘后噪音）----
# 注意：这里假设 etf_hf parquet 里的 timestamp_utc 字段【确实是UTC】。
# 如果你的数据其实已经是naive Eastern Time，请把 ETF_TS_IS_UTC 改成 False。
ETF_TS_IS_UTC = True
ETF_TZ        = "America/New_York"
RTH_START     = "09:30"
RTH_END       = "16:00"


# 数据库连接
con = duckdb.connect()


# ====================== 共用工具函数 ======================
def load_kalshi_trades(ticker: str, date_start: str, date_end: str) -> pd.DataFrame:
    # 用 trades_*.parquet 精确匹配，排除 macOS 生成的 ._trades_*.parquet 垃圾文件
    raw_parquet_glob = str(TRADES_DIR / "trades_*.parquet")
    q = f"""
    SELECT
        (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
        yes_price
    FROM read_parquet('{raw_parquet_glob}')
    WHERE ticker       = '{ticker}'
      AND created_time >= TIMESTAMPTZ '{date_start} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{date_end} 23:59:59+00'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"] = pd.to_datetime(df["ts_utc"])
    df["prob"]   = df["yes_price"] / 100.0
    return df.dropna(subset=["prob"]).reset_index(drop=True)


def load_etf_ticks(etf: str, date_start: str, date_end: str) -> pd.DataFrame:
    etf_path = str(ETF_HF_DIR / f"{etf}_hf.parquet")
    q = f"""
    SELECT timestamp_utc AS ts_utc, mid
    FROM   read_parquet('{etf_path}')
    WHERE  timestamp_utc >= TIMESTAMP '{date_start} 00:00:00'
      AND  timestamp_utc <= TIMESTAMP '{date_end} 23:59:59'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["ts_utc"] = pd.to_datetime(df["ts_utc"])
    df = df.dropna(subset=["mid"])
    df = df[np.isfinite(df["mid"]) & (df["mid"] > 0)]
    return df.reset_index(drop=True)


def filter_rth(df: pd.DataFrame, ts_col: str = "ts_utc") -> pd.DataFrame:
    """把ETF tick过滤到纽约常规交易时段(9:30-16:00 ET)，去掉盘前盘后噪音。"""
    if df.empty:
        return df
    df = df.copy()
    ts = df[ts_col]
    if ETF_TS_IS_UTC:
        ts_et = ts.dt.tz_localize("UTC").dt.tz_convert(ETF_TZ)
    else:
        ts_et = ts.dt.tz_localize(ETF_TZ)
    start = pd.Timestamp(RTH_START).time()
    end = pd.Timestamp(RTH_END).time()
    keep = (ts_et.dt.time >= start) & (ts_et.dt.time < end)
    df = df.loc[keep].copy()
    df["date_et"] = ts_et.loc[keep].dt.date
    return df



def filter_contract_overlap(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict Kalshi trades to ETF regular trading hours (09:30-16:00 ET)."""
    if df.empty:
        return df
    df=df.copy()
    ts_et=df["ts_utc"].dt.tz_localize("UTC").dt.tz_convert(ETF_TZ)
    keep=(ts_et.dt.time>=pd.Timestamp(RTH_START).time()) & (ts_et.dt.time<pd.Timestamp(RTH_END).time())
    df=df.loc[keep].copy()
    df["date_et"]=ts_et.loc[keep].dt.date
    return df

def median_inter_trade_gap_sec(ts: pd.Series) -> float:
    diffs = ts.sort_values().diff().dropna().dt.total_seconds()
    return float(diffs.median()) if len(diffs) else np.nan


def to_bars(df: pd.DataFrame, value_col: str, ts_col: str, freq: str,
            change_type: str = "logret", date_col: Optional[str] = None) -> pd.DataFrame:
    """
    把不规则的tick/trade数据降采样成固定频率的calendar-time bar。
    每个bar取该bar内所有观测值的【中位数(median)】，而不是最后一个值(last)。
    用median是为了抹掉单笔尖峰/异常tick——如果用last，一笔瞬间的异常报价只要
    恰好是bar内最后一条，就会被原样当成整个bar的代表值，直接污染回归；
    median对这种单点离群值天然不敏感，更稳健。这是导师明确要求的口径。
    bar 用右边沿、闭右口径：(t-bar, t] 的中位数标在 t，避免把 bar 内未来数据
    标成 bar 左端时点。没有任何观测的bar直接丢弃(不强行插值/ffill，避免在长时间没有成交的窗口里
    人为制造假信号)。
    如果传入 date_col，diff 会在 date_col 内部做，不跨隔夜。
    change_type:
        'logret' -> 适用于价格(ETF mid)，bar间变化用 log(p_t/p_{t-1})
        'diff'   -> 适用于概率(Kalshi prob, 0~1有界)，bar间变化用算术差分
    """
    if change_type not in {"logret", "diff"}:
        raise ValueError("change_type must be 'logret' or 'diff'")

    pieces = []
    groups = [(None, df)] if date_col is None else df.groupby(date_col, sort=True)
    for d, g in groups:
        # 关键修正：这里不能像原来那样在算diff之前就把空bar(NaN)物理删掉！
        # resample()本身会生成一个规整的、按freq等间隔的时间网格，没有成交的bar
        # 自然是NaN——这个网格的"行号顺序"天然就等价于"真实时间顺序"。
        # 如果像原来那样在diff之前就.dropna()，会把网格里的空行删掉，
        # 表格里"挨着的两行"就不再对应"真实时间上相邻的两个bar"了：
        # 比如10:00和之后下一次真实成交在15:00，中间几十个空bar被删掉后，
        # 10:00和15:00在表格里变成相邻两行，diff()会把它们当成只差一个bar
        # 算出一个"变化量"，但实际中间隔了5个小时——这就是老师说的
        # "把不相邻的bar当成相邻bar"的根源。
        # 正确做法：保留完整网格算diff（NaN diff NaN/实数 自然还是NaN），
        # 只有"当前bar和上一个bar都确实有成交"时diff才有意义，
        # 最后再统一把chg是NaN的行丢弃即可。
        s = (g.set_index(ts_col)[value_col]
               .resample(freq, label="right", closed="right")
               .median())
        if s.notna().sum() < 2:
            continue
        bars = s.to_frame(name=value_col)
        if change_type == "logret":
            bars["chg"] = np.log(bars[value_col]).diff()
        else:
            bars["chg"] = bars[value_col].diff()
        bars = bars.dropna(subset=["chg"]).reset_index()
        if date_col is not None:
            bars[date_col] = d
        pieces.append(bars)
    return pd.concat(pieces, ignore_index=True) if pieces else pd.DataFrame(columns=[ts_col, value_col, "chg"])


def align_on_time(left: pd.DataFrame, right: pd.DataFrame, ts_col: str,
                  tolerance_sec: int) -> pd.DataFrame:
    """优先精确按 bar 时间合并；如时间网格有轻微错位，再用 backward as-of，避免未来匹配。"""
    exact = pd.merge(left, right, on=ts_col, how="inner")
    if not exact.empty:
        return exact
    return pd.merge_asof(
        left.sort_values(ts_col),
        right.sort_values(ts_col),
        on=ts_col,
        direction="backward",
        tolerance=pd.Timedelta(f"{tolerance_sec}s"),
    )


def _day_dummies(df: pd.DataFrame) -> pd.DataFrame:
    return pd.get_dummies(df["date"], prefix="d", drop_first=True, dtype=float)


def _wald_pvalue_matrix(model, cols, x_columns) -> float:
    """用矩阵约束做联合 Wald，避开 lag_+1 这类列名在公式字符串里的解析问题。"""
    if not cols:
        return np.nan
    names = list(x_columns)
    R = np.zeros((len(cols), len(names)))
    for r, col in enumerate(cols):
        if col not in names:
            return np.nan
        R[r, names.index(col)] = 1.0
    try:
        wald_res = model.wald_test(R, scalar=True)
        return float(np.squeeze(wald_res.pvalue))
    except Exception as e:
        print(f"    联合Wald检验失败: {str(e)}")
        return np.nan


def _choose_own_lags_bic(df_reg: pd.DataFrame, effect_col: str, cause_cols,
                         effect_lag_cols, include_day_fe: bool) -> int:
    """在固定候选样本上用 BIC 选择 effect 自身滞后阶数。"""
    best_p, best_bic = 0, np.inf
    for p in range(0, len(effect_lag_cols) + 1):
        use_cols = list(cause_cols) + list(effect_lag_cols[:p])
        subset = [effect_col] + use_cols
        d = df_reg.dropna(subset=subset).copy()
        if len(d) < MIN_OBS:
            continue
        parts = [d[use_cols].astype(float)] if use_cols else []
        fe = _day_dummies(d) if include_day_fe else pd.DataFrame(index=d.index)
        if fe.shape[1] > 0:
            parts.append(fe)
        X = sm.add_constant(pd.concat(parts, axis=1) if parts else pd.DataFrame(index=d.index))
        y = d[effect_col].astype(float)
        try:
            model = sm.OLS(y, X).fit()
        except Exception:
            continue
        if np.isfinite(model.bic) and model.bic < best_bic:
            best_bic, best_p = model.bic, p
    return best_p


def run_granger_direction(
        df_reg: pd.DataFrame,
        cause_col: str,
        effect_col: str,
        direction: str,
        max_k: int = K,
        group_lags_by_day: bool = True,
        include_day_fe: bool = True,
        min_dof: int = MIN_DOF,
        own_lags="auto",
) -> Optional[pd.DataFrame]:
    """
    标准单向 ADL/Granger 检验：
        effect_t = a + sum_i phi_i effect_{t-i} + sum_j beta_j cause_{t-j} + FE + e_t
    联合检验 H0: beta_1 = ... = beta_K = 0。
    """
    df0 = df_reg.copy()
    K_try = max_k

    while K_try >= 1:
        df = df0.copy()
        if group_lags_by_day:
            g = df.groupby("date", group_keys=False)
            cshift = lambda j: g[cause_col].shift(j)
            eshift = lambda j: g[effect_col].shift(j)
        else:
            cshift = lambda j: df[cause_col].shift(j)
            eshift = lambda j: df[effect_col].shift(j)

        cause_cols = []
        for j in range(1, K_try + 1):
            col = f"cause_lag_{j}"
            df[col] = cshift(j)
            cause_cols.append(col)

        pmax = min(K_try, ADL_PMAX)
        effect_lag_cols = []
        for j in range(1, pmax + 1):
            col = f"effect_lag_{j}"
            df[col] = eshift(j)
            effect_lag_cols.append(col)

        cs = df[cause_col].std()
        if cs > 1e-12:
            for col in cause_cols:
                df[col] = df[col] / cs

        if isinstance(own_lags, str) and own_lags.lower() == "auto":
            p = _choose_own_lags_bic(df, effect_col, cause_cols, effect_lag_cols, include_day_fe)
        else:
            p = min(int(own_lags), pmax)

        use_cols = cause_cols + effect_lag_cols[:p]
        df_clean = df.dropna(subset=[effect_col] + use_cols).copy()
        n_obs_final = len(df_clean)
        unique_days = df_clean["date"].nunique() if n_obs_final else 0
        n_day_dummies = max(unique_days - 1, 0) if include_day_fe else 0
        n_regressors = len(use_cols) + n_day_dummies + 1
        dof = n_obs_final - n_regressors

        if n_obs_final >= MIN_OBS and dof >= min_dof:
            break
        K_try -= 1
    else:
        print(f"    {direction} 放弃：即使把K缩到1，自由度仍不足(n_obs={n_obs_final}, dof={dof}，需要>= {min_dof})")
        return None

    if K_try < max_k:
        print(f"    {direction} Granger自由度自适应：K从{max_k}缩小到{K_try} "
              f"(最终 n_obs={n_obs_final}, dof={dof}, y_lags={p})")
    print(f"    {direction} Granger样本: n={n_obs_final} dof={dof} K={K_try} y_lags={p}")

    fe = _day_dummies(df_clean) if include_day_fe else pd.DataFrame(index=df_clean.index)
    X = sm.add_constant(pd.concat([df_clean[use_cols].astype(float), fe], axis=1))
    y = df_clean[effect_col].astype(float)
    groups = df_clean["date"].values
    try:
        if len(np.unique(groups)) >= 2:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
            cov_type = "cluster_by_day"
        else:
            model = sm.OLS(y, X).fit(cov_type="HC3")
            cov_type = "HC3"
    except Exception as e:
        print(f"    {direction} Granger OLS估计失败: {str(e)}")
        return None

    p_granger = _wald_pvalue_matrix(model, cause_cols, X.columns)
    tier = "high" if dof >= 30 else "medium"
    rows = []
    for j, col in enumerate(cause_cols, start=1):
        rows.append({
            "direction": direction,
            "cause_col": cause_col,
            "effect_col": effect_col,
            "k": j,
            "coef": model.params[col],
            "t_stat": model.tvalues[col],
            "p_value": model.pvalues[col],
            "p_granger": p_granger,
            "r_squared": model.rsquared,
            "n_obs": n_obs_final,
            "n_days": unique_days,
            "k_used": K_try,
            "n_ylags": p,
            "dof": dof,
            "cov_type": cov_type,
            "reliability_tier": tier,
        })
    return pd.DataFrame(rows)


def _build_lags_and_dropna(df_reg, x_col, y_col, k_lo, k_hi, skip_zero_lag, group_lags_by_day):
    """构造[k_lo, k_hi]范围内的滞后列并dropna，返回(df_clean, lag_cols dict)。"""
    df_reg = df_reg.copy()
    lag_cols = {}
    if group_lags_by_day:
        g = df_reg.groupby("date", group_keys=False)
        shifter = lambda k: g[x_col].shift(k)
    else:
        shifter = lambda k: df_reg[x_col].shift(k)
    for k in range(k_lo, k_hi + 1):
        if skip_zero_lag and k == 0:
            continue
        col = f"lag_{k:+d}"
        df_reg[col] = shifter(k)
        lag_cols[k] = col
    all_lag_cols = list(lag_cols.values())
    df_reg = df_reg.dropna(subset=[y_col] + all_lag_cols).copy()
    return df_reg, lag_cols, all_lag_cols


def run_unified_regression(
        df_reg: pd.DataFrame,
        x_col: str,
        y_col: str,
        k_range: Tuple[int, int] = (-K, K),
        skip_zero_lag: bool = False,
        group_lags_by_day: bool = True,
        min_dof: int = MIN_DOF,
) -> Optional[pd.DataFrame]:
    """
    通用联合滞后回归执行函数（calendar-time版）。

    group_lags_by_day=True (ETF默认): lag 用 groupby("date") 内部 shift，保证
        不会跨交易日/跨session把上一天收盘前最后一个bar和第二天开盘第一个bar
        错误地当成"紧邻"的两个观测，否则隔夜跳空会污染短期lag的系数估计。
        这对ETF（有明确的RTH收盘）是必须的。

    group_lags_by_day=True (合约B/B-self用): 连续整体shift，不按日期切断。
        Kalshi合约24/7连续交易，没有"收盘"这个概念，按日期分组反而会在
        每个稀疏交易日内部人为制造大量NaN，把本来够用的样本砍没。

    skip_zero_lag: 自相关检验(self lead-lag)时设为True，跳过k=0，
        因为k=0时 lag_+0 就是 y_col 自身，回归没有意义（必然coef=1, R2=1）。

    【新增】自由度自适应(K shrinkage)：
        固定K=10意味着至少21个滞后参数，再加上若干日FE虚拟变量。如果某个pair
        的n_obs本来就只有三四十行（这在稀疏交易的Kalshi合约上很常见），
        参数个数和样本量几乎相当，自由度被压缩到个位数——OLS在数值上
        依然能跑出系数和p值，但这些估计量统计上不可信(标准误虚低、
        系数极不稳定，一两个观测点就能让结果天翻地覆)。
        这里改成：先尝试完整的k_range；如果dof = n_obs - n_regressors - 1
        不够min_dof，就把K对称缩小1再重试，直到满足dof要求或者K缩到1为止；
        如果连K=1都不满足，直接放弃这个pair（返回None），而不是硬跑一个
        不可信的结果出来。每一行结果都会记录实际用的K(k_used)、dof、
        以及一个可读的可靠性分档(reliability_tier)，方便你下游筛选时
        知道哪些结果统计上更扎实、哪些只是勉强达标。
    """
    lag_start, lag_end = k_range
    K_try = lag_end  # 假设对称的(-K, K)

    while K_try >= 1:
        df_clean, lag_cols, all_lag_cols = _build_lags_and_dropna(
            df_reg, x_col, y_col, -K_try, K_try, skip_zero_lag, group_lags_by_day
        )
        n_obs_final = len(df_clean)
        unique_days = df_clean["date"].nunique() if n_obs_final else 0
        n_day_dummies = max(unique_days - 1, 0)
        n_regressors = len(all_lag_cols) + n_day_dummies + 1  # +1 截距
        dof = n_obs_final - n_regressors

        if n_obs_final >= MIN_OBS and dof >= min_dof:
            break  # 这个K可以用
        K_try -= 1
    else:
        print(f"    放弃：即使把K缩到1，自由度仍不足(n_obs={n_obs_final}, dof={dof}，需要>= {min_dof})")
        return None

    if K_try < lag_end:
        print(f"    自由度自适应：K从{lag_end}缩小到{K_try}才满足 dof>={min_dof} "
              f"(最终 n_obs={n_obs_final}, dof={dof})")
    print(f"    构造lag并dropna后剩余行数: {n_obs_final}  dof={dof}  (要求 n_obs>={MIN_OBS} 且 dof>={min_dof})")

    df_reg = df_clean
    x_std = df_reg[x_col].std()
    if x_std > 1e-12:
        for col in all_lag_cols:
            df_reg[col] = df_reg[col] / x_std

    day_dummies = pd.get_dummies(df_reg["date"], prefix="d", drop_first=True, dtype=float)
    X = sm.add_constant(pd.concat([df_reg[all_lag_cols].astype(float), day_dummies], axis=1))
    y = df_reg[y_col].astype(float)

    groups = df_reg["date"].values
    try:
        if len(np.unique(groups)) >= 2:
            model = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})
        else:
            model = sm.OLS(y, X).fit(cov_type="HC3")
    except Exception as e:
        print(f"OLS估计失败: {str(e)}")
        return None

    if dof >= 30:
        tier = "high"
    elif dof >= min_dof:
        tier = "medium"
    else:
        tier = "low"  # 理论上不会出现，因为上面已经过滤掉了，留着做兜底标记

    # ---- 新增：联合Wald检验(老师要求的Granger式检验) ----
    # 不再只看单个b_k的p值数有几个显著(多重检验噪音)，而是一次性检验
    # "x_leads_y方向(k>0)的所有系数是否同时为0"，和
    # "y_leads_x方向(k<0)的所有系数是否同时为0"，
    # 各得到一个干净的联合p值。clustered协方差会自动带入这个Wald检验，
    # 不需要额外处理。
    pos_cols = [lag_cols[k] for k in lag_cols if k > 0 and lag_cols[k] in model.params.index]
    neg_cols = [lag_cols[k] for k in lag_cols if k < 0 and lag_cols[k] in model.params.index]

    def _joint_wald_pvalue(cols):
        """对给定的一组系数列名，做联合H0: 全部=0的Wald检验，返回p值。
        用矩阵约束，避免 lag_+1 / lag_-1 这类列名被公式解析器误读。"""
        return _wald_pvalue_matrix(model, cols, X.columns)

    p_joint_x_leads_y = _joint_wald_pvalue(pos_cols)   # H0: 所有k>0的b_k=0 → 拒绝=x领先y
    p_joint_y_leads_x = _joint_wald_pvalue(neg_cols)   # H0: 所有k<0的b_k=0 → 拒绝=y领先x

    res_rows = []
    n_obs_final = len(df_reg)
    unique_days = df_reg["date"].nunique()

    for k, col in lag_cols.items():
        if col not in model.params.index:
            continue
        if k > 0:
            direction = "x_leads_y"
        elif k < 0:
            direction = "y_leads_x"
        else:
            direction = "contemporaneous"

        res_rows.append({
            "k": k,
            "direction": direction,
            "coef": model.params[col],
            "t_stat": model.tvalues[col],
            "p_value": model.pvalues[col],
            "r_squared": model.rsquared,
            "n_obs": n_obs_final,
            "n_days": unique_days,
            "k_used": K_try,            # 实际用的K（可能比配置的K=10小，因为自由度自适应缩小过）
            "dof": dof,                 # 自由度
            "reliability_tier": tier,   # high(dof>=30) / medium(10<=dof<30)
            # ---- 新增：联合Granger式Wald检验p值，整个pair内每一行都一样（方便筛选时直接用） ----
            "p_joint_x_leads_y": p_joint_x_leads_y,  # H0: 所有"x过去预测y"的系数同时=0
            "p_joint_y_leads_x": p_joint_y_leads_x,  # H0: 所有"y过去预测x"的系数同时=0
        })
    return pd.DataFrame(res_rows)


# ====================== Model B: Contract <-> Contract (calendar-time, fixed bars) ======================
if RUN_MODEL_B:
    print("=" * 60)
    print(f"开始运行 Model B (calendar-time): Kalshi合约A ↔ Kalshi合约B   bar={CONTRACT_BAR_FREQ}")
    print("=" * 60)
    out_b = []
    if not PAIR_CONTRACT_CSV.exists():
        print(f"跳过 Model B：未找到 {PAIR_CONTRACT_CSV}")
        pair_contr = pd.DataFrame()
    else:
        pair_contr = pd.read_csv(PAIR_CONTRACT_CSV)

    for idx, pair in pair_contr.iterrows():
        ticker_x = pair["ticker_x"]
        ticker_y = pair["ticker_y"]
        ds = str(pair["date_start"])
        de = str(pair["date_end"])
        if ticker_x == ticker_y:
            print(f"\n[{idx+1}/{len(pair_contr)}] 跳过自配对：{ticker_x}")
            continue
        print(f"\n[{idx+1}/{len(pair_contr)}] X:{ticker_x}  Y:{ticker_y}")

        kalshi_x = filter_contract_overlap(load_kalshi_trades(ticker_x, ds, de))
        kalshi_y = filter_contract_overlap(load_kalshi_trades(ticker_y, ds, de))
        if kalshi_x.empty or kalshi_y.empty:
            print("跳过：无成交数据")
            continue

        # 诊断信息：帮助你判断 CONTRACT_BAR_FREQ 设的是否合理
        gx = median_inter_trade_gap_sec(kalshi_x["ts_utc"])
        gy = median_inter_trade_gap_sec(kalshi_y["ts_utc"])
        print(f"  median inter-trade gap: X={gx:.1f}s  Y={gy:.1f}s  (当前bar={CONTRACT_BAR_FREQ})")

        bars_x = to_bars(kalshi_x, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff", date_col="date_et")
        bars_y = to_bars(kalshi_y, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff", date_col="date_et")
        if len(bars_x) < MIN_OBS or len(bars_y) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_b = align_on_time(
            bars_x.rename(columns={"chg": "chg_x"})[["ts_utc", "chg_x"]],
            bars_y.rename(columns={"chg": "chg_y"})[["ts_utc", "chg_y"]],
            "ts_utc",
            CONTRACT_MAX_GAP_SEC,
        )
        df_b = df_b.dropna(subset=["chg_x", "chg_y"])
        df_b["date"] = df_b["ts_utc"].dt.date  # Kalshi常年无休，用UTC日期分组即可

        print(f"  对齐后行数: {len(df_b)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_xy = run_granger_direction(df_b, "chg_x", "chg_y", "x_to_y", group_lags_by_day=True)
        res_yx = run_granger_direction(df_b, "chg_y", "chg_x", "y_to_x", group_lags_by_day=True)
        pair_rows = [r for r in [res_xy, res_yx] if r is not None and not r.empty]
        if not pair_rows:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df = pd.concat(pair_rows, ignore_index=True)
        res_df["x_ticker"] = ticker_x
        res_df["y_ticker"] = ticker_y
        res_df["bar_freq"] = CONTRACT_BAR_FREQ
        out_b.append(res_df)

    if out_b:
        df_out_b = pd.concat(out_b, ignore_index=True)
        df_out_b.to_csv(OUT_CONTRACT_CONTR, index=False)
        print(f"\nModel B 完成，结果保存至: {OUT_CONTRACT_CONTR}")
        sig_b = df_out_b.drop_duplicates(["x_ticker", "y_ticker", "direction"])
        sig_b = sig_b[sig_b["p_granger"] < 0.05]
        total_b = df_out_b.drop_duplicates(["x_ticker", "y_ticker", "direction"])
        print(f"Granger联合显著方向(p_granger<0.05): {len(sig_b)} / {len(total_b)}")


# ====================== Model C: ETF <-> ETF (calendar-time, fixed bars, RTH only) ======================
if RUN_MODEL_C:
    print("\n" + "=" * 60)
    print(f"开始运行 Model C (calendar-time): ETF1 ↔ ETF2   bar={ETF_BAR_FREQ}, RTH only ({RTH_START}-{RTH_END} {ETF_TZ})")
    print("=" * 60)
    out_c = []
    if not PAIR_ETF_CSV.exists():
        print(f"跳过 Model C：未找到 {PAIR_ETF_CSV}")
        pair_etf = pd.DataFrame()
    else:
        pair_etf = pd.read_csv(PAIR_ETF_CSV)

    for idx, pair in pair_etf.iterrows():
        etf_x = pair["etf_x"]
        etf_y = pair["etf_y"]
        ds = str(pair["date_start"])
        de = str(pair["date_end"])
        if etf_x == etf_y:
            print(f"\n[{idx+1}/{len(pair_etf)}] 跳过自配对：{etf_x}")
            continue
        print(f"\n[{idx+1}/{len(pair_etf)}] X:{etf_x}  Y:{etf_y}")

        etf_x_ticks = filter_rth(load_etf_ticks(etf_x, ds, de))
        etf_y_ticks = filter_rth(load_etf_ticks(etf_y, ds, de))
        if etf_x_ticks.empty or etf_y_ticks.empty:
            print("跳过：无ETF数据（或RTH过滤后为空）")
            continue

        bars_x = to_bars(etf_x_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret", date_col="date_et")
        bars_y = to_bars(etf_y_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret", date_col="date_et")
        print(f"  降采样后: X={len(bars_x):,} bars, Y={len(bars_y):,} bars")
        if len(bars_x) < MIN_OBS or len(bars_y) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_c = align_on_time(
            bars_x.rename(columns={"chg": "ret_x"})[["ts_utc", "ret_x"]],
            bars_y.rename(columns={"chg": "ret_y"})[["ts_utc", "ret_y"]],
            "ts_utc",
            ETF_MAX_GAP_SEC,
        )
        df_c = df_c.dropna(subset=["ret_x", "ret_y"])
        # 用纽约时区的日期分组，确保shift()不会跨交易日
        ts_et = df_c["ts_utc"].dt.tz_localize("UTC").dt.tz_convert(ETF_TZ) if ETF_TS_IS_UTC \
            else df_c["ts_utc"].dt.tz_localize(ETF_TZ)
        df_c["date"] = ts_et.dt.date

        print(f"  对齐后行数: {len(df_c)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_xy = run_granger_direction(df_c, "ret_x", "ret_y", "x_to_y")
        res_yx = run_granger_direction(df_c, "ret_y", "ret_x", "y_to_x")
        pair_rows = [r for r in [res_xy, res_yx] if r is not None and not r.empty]
        if not pair_rows:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df = pd.concat(pair_rows, ignore_index=True)
        res_df["x_etf"] = etf_x
        res_df["y_etf"] = etf_y
        res_df["bar_freq"] = ETF_BAR_FREQ
        out_c.append(res_df)

    if out_c:
        df_out_c = pd.concat(out_c, ignore_index=True)
        df_out_c.to_csv(OUT_ETF_ETF, index=False)
        print(f"\nModel C 完成，结果保存至: {OUT_ETF_ETF}")
        sig_c = df_out_c.drop_duplicates(["x_etf", "y_etf", "direction"])
        sig_c = sig_c[sig_c["p_granger"] < 0.05]
        total_c = df_out_c.drop_duplicates(["x_etf", "y_etf", "direction"])
        print(f"Granger联合显著方向(p_granger<0.05): {len(sig_c)} / {len(total_c)}")

# ====================== Model B-self: 单个合约 自相关 (k bars ago vs now) ======================
if RUN_MODEL_B_SELF:
    print("\n" + "=" * 60)
    print(f"开始运行 Model B-self (calendar-time): 单合约自身 lead-lag   bar={CONTRACT_BAR_FREQ}")
    print("=" * 60)
    out_b_self = []
    if not PAIR_CONTRACT_CSV.exists():
        print(f"跳过 Model B-self：未找到 {PAIR_CONTRACT_CSV}")
        contracts_unique = pd.DataFrame()
    else:
        pair_contr_raw = pd.read_csv(PAIR_CONTRACT_CSV)
        # 把 ticker_x / ticker_y 去重展开成单个合约清单（沿用同样的date_start/date_end）
        contracts_unique = pd.concat([
            pair_contr_raw[["ticker_x", "date_start", "date_end"]].rename(columns={"ticker_x": "ticker"}),
            pair_contr_raw[["ticker_y", "date_start", "date_end"]].rename(columns={"ticker_y": "ticker"}),
        ]).drop_duplicates(subset=["ticker", "date_start", "date_end"]).reset_index(drop=True)

    for idx, row in contracts_unique.iterrows():
        ticker = row["ticker"]
        ds = str(row["date_start"])
        de = str(row["date_end"])
        print(f"\n[{idx+1}/{len(contracts_unique)}] ticker:{ticker}")

        kalshi_x = filter_contract_overlap(load_kalshi_trades(ticker, ds, de))
        if kalshi_x.empty:
            print("跳过：无成交数据")
            continue

        gx = median_inter_trade_gap_sec(kalshi_x["ts_utc"])
        print(f"  median inter-trade gap: {gx:.1f}s  (当前bar={CONTRACT_BAR_FREQ})")

        bars_x = to_bars(kalshi_x, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff", date_col="date_et")
        if len(bars_x) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_self = bars_x.rename(columns={"chg": "chg_self"})[["ts_utc", "chg_self"]].copy()
        df_self["date"] = df_self["ts_utc"].dt.date

        # x_col == y_col：自己预测自己，跳过k=0（否则lag_+0就是y本身，没意义）
        print(f"  bar行数: {len(df_self)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_df = run_unified_regression(df_self, x_col="chg_self", y_col="chg_self", skip_zero_lag=True, group_lags_by_day=True)
        if res_df is None or res_df.empty:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df["ticker"] = ticker
        res_df["bar_freq"] = CONTRACT_BAR_FREQ
        out_b_self.append(res_df)

    if out_b_self:
        df_out_b_self = pd.concat(out_b_self, ignore_index=True)
        df_out_b_self.to_csv(OUT_CONTRACT_SELF, index=False)
        print(f"\nModel B-self 完成，结果保存至: {OUT_CONTRACT_SELF}")
        sig_b_self = df_out_b_self.drop_duplicates(["ticker"])
        sig_b_self = sig_b_self[sig_b_self["p_joint_x_leads_y"] < 0.05]
        total_b_self = df_out_b_self.drop_duplicates(["ticker"])
        print(f"self联合显著合约(p_joint<0.05): {len(sig_b_self)} / {len(total_b_self)}")


# ====================== Model C-self: 单个ETF 自相关 (k bars ago vs now) ======================
if RUN_MODEL_C_SELF:
    print("\n" + "=" * 60)
    print(f"开始运行 Model C-self (calendar-time): 单ETF自身 lead-lag   bar={ETF_BAR_FREQ}, RTH only")
    print("=" * 60)
    out_c_self = []
    if not PAIR_ETF_CSV.exists():
        print(f"跳过 Model C-self：未找到 {PAIR_ETF_CSV}")
        etfs_unique = pd.DataFrame()
    else:
        pair_etf_raw = pd.read_csv(PAIR_ETF_CSV)
        etfs_unique = pd.concat([
            pair_etf_raw[["etf_x", "date_start", "date_end"]].rename(columns={"etf_x": "etf"}),
            pair_etf_raw[["etf_y", "date_start", "date_end"]].rename(columns={"etf_y": "etf"}),
        ]).drop_duplicates(subset=["etf", "date_start", "date_end"]).reset_index(drop=True)

    for idx, row in etfs_unique.iterrows():
        etf = row["etf"]
        ds = str(row["date_start"])
        de = str(row["date_end"])
        print(f"\n[{idx+1}/{len(etfs_unique)}] etf:{etf}")

        etf_ticks = filter_rth(load_etf_ticks(etf, ds, de))
        if etf_ticks.empty:
            print("跳过：无ETF数据（或RTH过滤后为空）")
            continue

        bars_x = to_bars(etf_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret", date_col="date_et")
        print(f"  降采样后: {len(bars_x):,} bars")
        if len(bars_x) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_self = bars_x.rename(columns={"chg": "ret_self"})[["ts_utc", "ret_self"]].copy()
        ts_et = df_self["ts_utc"].dt.tz_localize("UTC").dt.tz_convert(ETF_TZ) if ETF_TS_IS_UTC \
            else df_self["ts_utc"].dt.tz_localize(ETF_TZ)
        df_self["date"] = ts_et.dt.date

        print(f"  bar行数: {len(df_self)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_df = run_unified_regression(df_self, x_col="ret_self", y_col="ret_self", skip_zero_lag=True)
        if res_df is None or res_df.empty:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df["etf"] = etf
        res_df["bar_freq"] = ETF_BAR_FREQ
        out_c_self.append(res_df)

    if out_c_self:
        df_out_c_self = pd.concat(out_c_self, ignore_index=True)
        df_out_c_self.to_csv(OUT_ETF_SELF, index=False)
        print(f"\nModel C-self 完成，结果保存至: {OUT_ETF_SELF}")
        sig_c_self = df_out_c_self.drop_duplicates(["etf"])
        sig_c_self = sig_c_self[sig_c_self["p_joint_x_leads_y"] < 0.05]
        total_c_self = df_out_c_self.drop_duplicates(["etf"])
        print(f"self联合显著ETF(p_joint<0.05): {len(sig_c_self)} / {len(total_c_self)}")

print("\n全部选定模型运行结束！")
