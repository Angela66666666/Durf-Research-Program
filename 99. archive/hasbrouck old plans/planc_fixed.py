import pandas as pd
import numpy as np
import os


def find_project_root(target_folder="regression"):
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if target_folder in os.listdir(current):
            return current
        current = os.path.dirname(current)
    raise FileNotFoundError("未定位到项目根目录")


def locate_beta_csv(root_dir, filename="etf_beta_significant_june_july.csv"):
    """
    E1修复：Step1用相对路径写文件(写到运行时CWD)，Plan C原来只认
    root_dir下的绝对路径，两边约定不一致，换个目录跑就找不到。
    这里依次尝试几个最可能的位置，而不是假设某一个。
    """
    candidates = [
        os.path.join(root_dir, filename),                      # 项目根目录
        os.path.join(root_dir, "regression", filename),         # regression子目录
        os.path.join(os.getcwd(), filename),                    # 当前工作目录
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"在以下位置都没找到{filename}，请确认Step1的输出路径：\n"
        + "\n".join(candidates)
    )


def load_beta_vector(root_dir):
    beta_csv = locate_beta_csv(root_dir)
    beta_df = pd.read_csv(beta_csv)

    # B1修复：Step1现在每个ticker天然只有一行，不再需要drop_duplicates。
    # 但保留一个显式检查，而不是静默drop——如果哪天Step1又意外产出了
    # 重复ticker，这里应该报错让你注意到，而不是悄悄挑一行了事。
    dup = beta_df["ticker"][beta_df["ticker"].duplicated()].unique()
    if len(dup) > 0:
        raise ValueError(
            f"beta表里发现重复ticker: {dup.tolist()}，"
            f"说明Step1的输出不是预期的单行/ticker格式，请先检查Step1，"
            f"不要在这里drop_duplicates掩盖问题。"
        )
    return beta_df


def load_hf_panel(tk_list, root_dir, resample_freq="1min"):
    ret_dict = {}
    hf_base = os.path.join(root_dir, "leadlag", "etf_hf")
    valid_tickers = []
    for tk in tk_list:
        print(f"【进度】处理 {tk}_hf.parquet")
        parquet_path = os.path.join(hf_base, f"{tk}_hf.parquet")
        df = pd.read_parquet(parquet_path, columns=["timestamp_utc", "mid"])

        # 时区标准化
        df["dt"] = pd.to_datetime(df["timestamp_utc"])
        df["dt_utc"] = df["dt"].dt.tz_localize("UTC")
        df["dt_et"] = df["dt_utc"].dt.tz_convert("US/Eastern")

        # 过滤美股交易时段 9:30-16:00 ET
        hour = df["dt_et"].dt.hour
        minute = df["dt_et"].dt.minute
        trading_mask = ((hour > 9) | ((hour == 9) & (minute >= 30))) & (hour < 16)
        df_trade = df[trading_mask].copy()
        df_trade = df_trade.set_index("dt_et")["mid"]

        # ⚠️ C1未修：这里仍是 resample().last()，默认 label="left"，
        # 标签09:31的bar实际取的是09:31:59的价格，存在最多1分钟的look-ahead。
        # 你朋友建议直接复用主pipeline的 leadlag_common.causal_bars()
        # （右沿标签 + 区间内median），但我没看到那个函数的实现，
        # 没法直接帮你接进来——这里先保留原逻辑，需要你确认
        # causal_bars() 的签名之后再补这一步。
        resampled_mid = df_trade.resample(resample_freq).last().dropna()

        # C2修复：按自然日分组做diff，避免每天第一根bar把隔夜跳空
        # 算成"1分钟收益"
        log_price = np.log(resampled_mid)
        log_ret = log_price.groupby(log_price.index.date).diff().dropna()

        if len(log_ret) < 30:
            print(f"⚠️ {tk} 重采样后有效样本过少，剔除")
            continue
        ret_dict[tk] = log_ret
        valid_tickers.append(tk)
        print(f"✅ {tk} 处理完成，重采样后样本量：{len(log_ret)}")

    if len(ret_dict) == 0:
        raise Exception("无任何ETF存在充足有效高频数据")

    print("\n全部有效标的：", valid_tickers)
    print("按统一1分钟时间轴对齐...")

    # C3修复：外对齐后直接做complete-case，不再让cov()做pairwise，
    # 保证Sigma是同一个样本上的一致估计
    panel_outer = pd.DataFrame(ret_dict).dropna(how="all")
    panel = panel_outer.dropna()  # complete-case
    overlap_len = len(panel)
    print(f"公共有效观测点总数：{overlap_len}")

    if overlap_len < 30:
        raise Exception(f"公共重叠观测仅{overlap_len}行，不足以求解协方差")
    return panel, valid_tickers


def solve_minvar_weights(ret_panel, beta_valid):
    tickers = beta_valid["ticker"].tolist()
    beta_vec = beta_valid["beta"].values.reshape(-1, 1)

    # ⚠️ C4未修：Sigma目前仍用load_hf_panel传入的全部区间估计，
    # 如果这段区间和Step3/4的检验窗口重叠，权重里的Sigma^{-1}会带入
    # look-ahead。需要你确认识别窗口和检验窗口的具体切分之后再改，
    # 这里先保留原逻辑，只是把它单独列出来提醒你别漏改。
    Sigma = ret_panel.cov().values
    try:
        Sigma_inv = np.linalg.inv(Sigma)
    except np.linalg.LinAlgError:
        raise Exception("协方差矩阵奇异不可逆，标的收益率线性相关")

    term1 = beta_vec.T @ Sigma_inv @ beta_vec
    term1_inv = np.linalg.inv(term1)
    term2 = Sigma_inv @ beta_vec
    w_raw = term1_inv * term2  # 解析解保证 w_raw' beta = 1

    # B2修复：先美元中性去均值，再重新缩放回单位选举暴露
    # （去均值不改变w对beta的方向，缩放也不改变sum(w)=0，两个约束能同时满足）
    w_demeaned = w_raw - np.mean(w_raw)
    exposure = (w_demeaned.T @ beta_vec).item()
    if abs(exposure) < 1e-12:
        raise Exception("去均值后对beta的暴露接近0，无法归一化，请检查beta向量")
    w_adj = w_demeaned / exposure

    result_df = pd.DataFrame({
        "ticker": tickers,
        "beta": beta_valid["beta"].values,
        "raw_minvar_weight": w_raw.flatten(),
        "final_dollar_neutral_weight": w_adj.flatten(),
    })
    return result_df


def main():
    root_path = find_project_root("regression")

    beta_df = load_beta_vector(root_path)
    all_tickers = beta_df["ticker"].tolist()
    print("待处理全部ETF：", all_tickers)

    # 重采样1分钟频度，可改为"5min"、"10min"
    ret_panel, valid_tickers = load_hf_panel(all_tickers, root_path, resample_freq="1min")

    beta_valid = beta_df[beta_df["ticker"].isin(valid_tickers)].copy()
    result_df = solve_minvar_weights(ret_panel, beta_valid)

    # E2修复：不再写进regression/（那是主pipeline的输入目录），
    # 单独开一个输出目录
    out_dir = os.path.join(root_path, "planc_output")
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, "etf_mimic_port_weights.csv")
    result_df.to_csv(out_csv, index=False)

    print("\n==== Plan C 最小方差权重计算完成（修正版）====")
    print(result_df.round(6))

    long_total = result_df[result_df["final_dollar_neutral_weight"] > 0]["final_dollar_neutral_weight"].sum()
    short_total = result_df[result_df["final_dollar_neutral_weight"] < 0]["final_dollar_neutral_weight"].sum()
    exposure_check = ((result_df["final_dollar_neutral_weight"].values.reshape(-1, 1)).T
                       @ result_df["beta"].values.reshape(-1, 1)).item()
    print(f"\n多头总权重：{long_total:.4f}")
    print(f"空头总权重：{short_total:.4f}")
    print(f"w' beta（应≈1，单位选举暴露检验）：{exposure_check:.6f}")
    print("输出文件：", out_csv)


if __name__ == "__main__":
    main()
