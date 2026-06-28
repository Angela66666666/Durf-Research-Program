import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
from typing import Tuple, Optional
from pathlib import Path

# ====================== 全局可配置超参数 ======================
HERE          = Path(__file__).parent
ETF_HF_DIR    = HERE / "etf_hf"
TRADES_DIR = Path("/Users/ariashy/Desktop/Durf-Research-Program/regression/data/kalshi/market/trades")

# Model B / C 的真实配对表（如不存在则自动跳过对应模型）
PAIR_CONTRACT_CSV = HERE / "pair_contract.csv"  # 字段: ticker_x, ticker_y, date_start, date_end
PAIR_ETF_CSV      = HERE / "pair_etf.csv"       # 字段: etf_x, etf_y, date_start, date_end

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
    raw_parquet_glob = str(TRADES_DIR / "*.parquet")
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
    return df.dropna(subset=["mid"]).reset_index(drop=True)


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
    keep = ts_et.dt.time.between(
        pd.Timestamp(RTH_START).time(), pd.Timestamp(RTH_END).time()
    )
    df = df.loc[keep].copy()
    df["date_et"] = ts_et.loc[keep].dt.date
    return df


def median_inter_trade_gap_sec(ts: pd.Series) -> float:
    diffs = ts.sort_values().diff().dropna().dt.total_seconds()
    return float(diffs.median()) if len(diffs) else np.nan


def to_bars(df: pd.DataFrame, value_col: str, ts_col: str, freq: str,
            change_type: str = "logret") -> pd.DataFrame:
    """
    把不规则的tick/trade数据降采样成固定频率的calendar-time bar。
    每个bar取该bar内所有观测值的【中位数(median)】，而不是最后一个值(last)。
    用median是为了抹掉单笔尖峰/异常tick——如果用last，一笔瞬间的异常报价只要
    恰好是bar内最后一条，就会被原样当成整个bar的代表值，直接污染回归；
    median对这种单点离群值天然不敏感，更稳健。这是导师明确要求的口径。
    没有任何观测的bar直接丢弃(不强行插值/ffill，避免在长时间没有成交的窗口里
    人为制造假信号)。
    change_type:
        'logret' -> 适用于价格(ETF mid)，bar间变化用 log(p_t/p_{t-1})
        'diff'   -> 适用于概率(Kalshi prob, 0~1有界)，bar间变化用算术差分
    """
    s = df.set_index(ts_col)[value_col].resample(freq).median().dropna()
    bars = s.to_frame(name=value_col)
    if change_type == "logret":
        bars["chg"] = np.log(bars[value_col]).diff()
    elif change_type == "diff":
        bars["chg"] = bars[value_col].diff()
    else:
        raise ValueError("change_type must be 'logret' or 'diff'")
    bars = bars.dropna(subset=["chg"]).reset_index()
    return bars


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

    group_lags_by_day=False (合约B/B-self用): 连续整体shift，不按日期切断。
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

        kalshi_x = load_kalshi_trades(ticker_x, ds, de)
        kalshi_y = load_kalshi_trades(ticker_y, ds, de)
        if kalshi_x.empty or kalshi_y.empty:
            print("跳过：无成交数据")
            continue

        # 诊断信息：帮助你判断 CONTRACT_BAR_FREQ 设的是否合理
        gx = median_inter_trade_gap_sec(kalshi_x["ts_utc"])
        gy = median_inter_trade_gap_sec(kalshi_y["ts_utc"])
        print(f"  median inter-trade gap: X={gx:.1f}s  Y={gy:.1f}s  (当前bar={CONTRACT_BAR_FREQ})")

        bars_x = to_bars(kalshi_x, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff")
        bars_y = to_bars(kalshi_y, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff")
        if len(bars_x) < MIN_OBS or len(bars_y) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_b = pd.merge_asof(
            bars_x.rename(columns={"chg": "chg_x"})[["ts_utc", "chg_x"]],
            bars_y.rename(columns={"chg": "chg_y"})[["ts_utc", "chg_y"]],
            on="ts_utc", direction="nearest",
            tolerance=pd.Timedelta(f"{CONTRACT_MAX_GAP_SEC}s"),
        )
        df_b = df_b.dropna(subset=["chg_x", "chg_y"])
        df_b["date"] = df_b["ts_utc"].dt.date  # Kalshi常年无休，用UTC日期分组即可

        print(f"  merge_asof后对齐行数: {len(df_b)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_df = run_unified_regression(df_b, x_col="chg_x", y_col="chg_y", group_lags_by_day=False)
        if res_df is None or res_df.empty:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df["x_ticker"] = ticker_x
        res_df["y_ticker"] = ticker_y
        res_df["bar_freq"] = CONTRACT_BAR_FREQ
        out_b.append(res_df)

    if out_b:
        df_out_b = pd.concat(out_b, ignore_index=True)
        df_out_b.to_csv(OUT_CONTRACT_CONTR, index=False)
        print(f"\nModel B 完成，结果保存至: {OUT_CONTRACT_CONTR}")
        sig_b = df_out_b[df_out_b["p_value"] < 0.05]
        print(f"显著系数数量(p<0.05): {len(sig_b)} / {len(df_out_b)}")


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

        bars_x = to_bars(etf_x_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret")
        bars_y = to_bars(etf_y_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret")
        print(f"  降采样后: X={len(bars_x):,} bars, Y={len(bars_y):,} bars")
        if len(bars_x) < MIN_OBS or len(bars_y) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_c = pd.merge_asof(
            bars_x.rename(columns={"chg": "ret_x"})[["ts_utc", "ret_x"]],
            bars_y.rename(columns={"chg": "ret_y"})[["ts_utc", "ret_y"]],
            on="ts_utc", direction="nearest",
            tolerance=pd.Timedelta(f"{ETF_MAX_GAP_SEC}s"),
        )
        df_c = df_c.dropna(subset=["ret_x", "ret_y"])
        # 用纽约时区的日期分组，确保shift()不会跨交易日
        ts_et = df_c["ts_utc"].dt.tz_localize("UTC").dt.tz_convert(ETF_TZ) if ETF_TS_IS_UTC \
            else df_c["ts_utc"].dt.tz_localize(ETF_TZ)
        df_c["date"] = ts_et.dt.date

        print(f"  merge_asof后对齐行数: {len(df_c)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_df = run_unified_regression(df_c, x_col="ret_x", y_col="ret_y")
        if res_df is None or res_df.empty:
            print("  跳过：回归内部判定样本不足或OLS失败（见上方行数）")
            continue
        res_df["x_etf"] = etf_x
        res_df["y_etf"] = etf_y
        res_df["bar_freq"] = ETF_BAR_FREQ
        out_c.append(res_df)

    if out_c:
        df_out_c = pd.concat(out_c, ignore_index=True)
        df_out_c.to_csv(OUT_ETF_ETF, index=False)
        print(f"\nModel C 完成，结果保存至: {OUT_ETF_ETF}")
        sig_c = df_out_c[df_out_c["p_value"] < 0.05]
        print(f"显著系数数量(p<0.05): {len(sig_c)} / {len(df_out_c)}")

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

        kalshi_x = load_kalshi_trades(ticker, ds, de)
        if kalshi_x.empty:
            print("跳过：无成交数据")
            continue

        gx = median_inter_trade_gap_sec(kalshi_x["ts_utc"])
        print(f"  median inter-trade gap: {gx:.1f}s  (当前bar={CONTRACT_BAR_FREQ})")

        bars_x = to_bars(kalshi_x, "prob", "ts_utc", CONTRACT_BAR_FREQ, change_type="diff")
        if len(bars_x) < MIN_OBS:
            print("跳过：降采样后样本不足")
            continue

        df_self = bars_x.rename(columns={"chg": "chg_self"})[["ts_utc", "chg_self"]].copy()
        df_self["date"] = df_self["ts_utc"].dt.date

        # x_col == y_col：自己预测自己，跳过k=0（否则lag_+0就是y本身，没意义）
        print(f"  bar行数: {len(df_self)}  (需要至少 {MIN_OBS} 行才能回归)")
        res_df = run_unified_regression(df_self, x_col="chg_self", y_col="chg_self", skip_zero_lag=True, group_lags_by_day=False)
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
        sig_b_self = df_out_b_self[df_out_b_self["p_value"] < 0.05]
        print(f"显著系数数量(p<0.05): {len(sig_b_self)} / {len(df_out_b_self)}")


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

        bars_x = to_bars(etf_ticks, "mid", "ts_utc", ETF_BAR_FREQ, change_type="logret")
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
        sig_c_self = df_out_c_self[df_out_c_self["p_value"] < 0.05]
        print(f"显著系数数量(p<0.05): {len(sig_c_self)} / {len(df_out_c_self)}")

print("\n全部选定模型运行结束！")