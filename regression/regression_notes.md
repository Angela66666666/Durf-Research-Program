# Regression Screening Notes

记录这个回归筛选脚本（`regression.py`）的基本思路、关键决策、以及每次核心修改和理由。

---

## 1. 目标（Why）

整个项目研究 **Kalshi 预测市场合约** 与 **行业 ETF** 之间的领先滞后（lead-lag）关系，事件背景是 2024 美国大选。

这个脚本是**第一步筛选工具**：在 295 个合约 × 11 个 Vanguard 行业 ETF 里，找出哪些 (合约 × ETF) 组合的**共动关系强**，从而筛掉无关合约、留下值得深入分析的"有用"合约。

## 2. 数据（What）

| 文件 | 关键列 | 说明 |
|---|---|---|
| `contract_daily_prices.csv` | `ticker`, `trade_date`, `close_yes_price`, `sector_relevance` | 295 个合约的日度数据；`close_yes_price` 是 0–100 美分，即概率×100 |
| `../etf_data/vanguard_sector_etf_total_returns.csv` | `ticker`, `date`, `daily_total_return` | 11 个 Vanguard 行业 ETF 的日度总收益 |

两份数据都从 2024-09 起，按日期对齐。

## 3. 方法（How）

对每个 (合约 × ETF) 组合跑 OLS：

- **自变量 X** = 合约的日度概率变化 `Δ(close_yes_price / 100)`（在每个合约内部按日期 diff）
- **因变量 Y** = ETF 当日 `daily_total_return`
- 设定（仅同期）：`etf_return(t) ~ prob_change(t)`
- 记录：`coef`、`abs_coef`、`std_coef`（标准化系数）、`t_stat`、`p_value`、`r_squared`、`n_obs`
- **排序：按 `r_squared`（共振强度）降序**，打印摘要先按 p<0.05 过滤

### 关键参数
- `MIN_OBS = 10`：重叠交易日少于 10 天的组合直接跳过。
- `P_THRESHOLD = 0.05`：打印摘要时只看显著的组合。

## 4. 重要方法论决策

### 不能只按裸 |系数| 排序
每个合约的 `prob_change` 方差不同。一个**概率几乎不动**的合约，为解释 ETF 同样的波动，回归会机械地给它一个**很大的系数**，但其实没有解释力（典型表现：coef 大但 p 值不显著）。

**对策：**
1. 增加 **标准化系数 `std_coef = coef × std(X)/std(Y)`**，让不同合约之间可比。
2. **按 `r_squared` 排序**衡量共振强度（单自变量 OLS 里 `R² = std_coef² = 相关系数²`），不要用裸 |coef|。
3. 打印摘要时**先按 `p_value < 0.05` 过滤**，把噪声组合踢掉。
4. 完整结果（含不显著的）仍全部写入 `regression_screen_results.csv`，方便自行复筛。

### 最少观测天数门槛
原始数据里很多合约只有 2–5 天数据。不设门槛会跑出一堆只有两三个点、系数虚高的假结果。故设 `MIN_OBS = 10`。

---

## 5. 修改日志（Changelog）

### v1 — 初始占位脚本（继承自仓库）
- 读取不存在的 `merged_data.csv`，用不存在的列 `trump_prob_change` / `xle_return`（XLE 是 SPDR 能源 ETF，本数据里没有；本项目能源 ETF 是 Vanguard 的 **VDE**）。
- **状态：跑不了，纯占位。**

### v2 — 改为全配对同期筛选
- **改动：** 直接用 `contract_daily_prices.csv` + ETF 收益；对 295 合约 × 11 ETF 全部组合跑同期 OLS；按 |coef| 排序，输出 `regression_screen_results.csv`。
- **理由：** 真正目标是"筛选系数高的合约"，不是跑单条回归。
- **加入 `MIN_OBS = 10`：** 排除数据点过少的虚高结果。
- **发现的问题：** 排序榜首被 Fed 加息合约等占据，但它们 p 值不显著——说明单看 |coef| 会被噪声误导。

### v3 — 加标准化系数、显著性过滤、lag-1
- **改动 1：** 新增 `std_coef`（标准化系数），让不同合约的系数可比。
- **改动 2：** 打印摘要先按 `p_value < 0.05` 过滤再排序；完整结果仍全部入 CSV。
- **改动 3：** 新增 `lag1` 设定（`etf_return(t) ~ prob_change(t-1)`），与同期并列输出，检验"预测市场是否领先 ETF"。
- **发现：** lag1 显著对子（12/550）比纯随机预期（~27）还少，日度上几乎无领先信号；而同期共振真实且强。

### v4 — 聚焦同期筛选、改按 R² 排序（当前版本）
- **明确定位：** 这个回归就是"同期共振筛选器"。先用日度同期回归筛出共振强的 (合约 × ETF) 对子，之后**只对这些对子下载高频数据**去研究真正的先后关系。先后关系不在本脚本里判断。
- **改动 1：删掉 lag1。** 先后关系交给高频数据，这一步留着只是干扰。
- **改动 2：排序从 `abs_coef` 改为 `r_squared`。** 理由：单自变量 OLS 里 `|std_coef| = √R² = |相关系数|`，所以"共振强度"应由 R²（= std_coef²）衡量，而裸 |coef| 还混入了各合约概率波动幅度的差异，是错误的排序维度。
- **保留短命合约（MIN_OBS=10 不变）：** 事件前后只有 10 天左右的合约也保留——只有那几天的话，对应高频数据通常也只有那几天，仍可用。

---

## 6. 怎么跑

```bash
cd /Users/hongxinliu/Durf-Research-Program/prediction-market-analysis
python regression.py
```

约几秒钟。结果：终端按设定分别打印显著组合 Top N；完整结果存 `regression_screen_results.csv`。
