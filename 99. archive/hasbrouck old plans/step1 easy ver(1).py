import pandas as pd
import os

def find_project_root(target_folder="regression"):
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        if target_folder in os.listdir(current):
            return current
        current = os.path.dirname(current)
    raise FileNotFoundError("未找到regression文件夹")

root_path = find_project_root("regression")
csv_path = os.path.join(root_path, "regression", "regression_screen_results.csv")

screen_df = pd.read_csv(csv_path)
print("CSV内全部列名：", screen_df.columns.tolist())

# 直接填文件里真实存在的列名，不再占位符
p_col = "p_value"
beta_col = "std_coef"
ticker_col = "etf"

# 筛选p<0.05显著的ETF
screen_df["significant"] = screen_df[p_col] < 0.05

# 提取etf名称、std_coef并重命名为beta
beta_df = screen_df[screen_df["significant"] == 1][[ticker_col, beta_col]].copy()
beta_df.rename(
    columns={
        ticker_col: "ticker",
        beta_col: "beta"
    },
    inplace=True
)

# 输出文件，给Step2读取
beta_df.to_csv("etf_beta_significant_june_july.csv", index=False)
print("==== Step1简易版β提取完成 ====")
print(beta_df)