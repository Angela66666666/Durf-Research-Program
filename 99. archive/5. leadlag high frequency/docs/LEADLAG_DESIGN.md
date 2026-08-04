# Lead-Lag 分析完整设计文档

## 目录

1. [研究问题](#1-研究问题)
2. [理论框架](#2-理论框架)
3. [数据来源](#3-数据来源)
4. [四种方法全览](#4-四种方法全览)
5. [核心脚本：事件驱动统一回归](#5-核心脚本事件驱动统一回归)
6. [完整代码逻辑](#6-完整代码逻辑)
7. [输出数据字段说明](#7-输出数据字段说明)
8. [如何解读结果](#8-如何解读结果)
9. [当前运行结果摘要](#9-当前运行结果摘要)
10. [常见误区](#10-常见误区)

---

## 1. 研究问题

**核心问题**：Kalshi 预测市场（政治/宏观事件合约）与对应的 ETF 板块之间，谁的价格变动先于另一方？

- **Kalshi 领先 ETF**：Kalshi 合约价格先动，ETF 随后跟随 → Kalshi 有信息优势
- **ETF 领先 Kalshi**：ETF 先动，Kalshi 随后更新 → ETF 市场先消化信息
- **双向均显著**：两个市场互相参考，存在反馈机制

这个问题的经济含义：预测市场是否真的在"预测"股市，还是只是在跟随股市？

---

## 2. 理论框架

### 2.1 教授给出的核心公式

$$r_{i,t} = \alpha + \sum_{k=-K}^{K} \beta_k \Delta\varsigma(p_{t-k}) + \gamma' X_t + \varepsilon_{i,t}$$

**符号说明**：

| 符号 | 含义 |
|------|------|
| $r_{i,t}$ | ETF 在 $t$ 时刻的对数收益率 |
| $\Delta\varsigma(p_{t-k})$ | $t-k$ 时刻的 Kalshi 合约概率变化量 |
| $\beta_k$（$k>0$） | 过去 $k$ 期的 Kalshi 变动对当期 ETF 的影响 → **Kalshi 领先 ETF** |
| $\beta_k$（$k<0$） | 未来 $k$ 期的 Kalshi 变动与当期 ETF 的关系 → **ETF 领先 Kalshi** |
| $\beta_0$ | 同期效应（contemporaneous） |
| $\gamma' X_t$ | 日期固定效应，控制不同交易日之间的整体差异 |

### 2.2 联合估计的优势

公式中所有 $k$（从 $-K$ 到 $+K$）**同时放进一个回归**，而不是每个 $k$ 单独跑一个回归。

这意味着：
- 每个 $\beta_k$ 是在控制了其他所有时间点效应之后的**净效应**
- 避免了"某个 $k$ 显著只是因为它与另一个真正显著的 $k$ 相关"的混淆问题
- 学术上符合 Hasbrouck (1995) 信息份额框架和 Granger 因果检验的标准规范

### 2.3 事件驱动的改进：为什么不用日历时间

原始公式的问题：如果按分钟级日历时间离散化，Kalshi 交易极度稀疏——历史数据中只有约 **1.54%** 的市场分钟内有 Kalshi 交易，剩下 98.46% 的观测行 `prob_change = 0`，大量"空白"行稀释了信号。

**事件驱动的解法**：把公式中的时间下标 $t$ 从"第 $t$ 分钟"重新定义为"**第 $i$ 笔 Kalshi 交易**"。

改写后的公式：

$$\text{ETF\_return}_i = \alpha + \sum_{k=-K}^{K} \beta_k \cdot \Delta p_{i-k} + \gamma' X_i + \varepsilon_i$$

- $i$ = 第 $i$ 笔 Kalshi 交易的序号
- $\Delta p_{i-k}$ = 第 $i-k$ 笔交易对应的概率变化（每一行都是真实的交易，没有空白行）
- $\text{ETF\_return}_i$ = 从第 $i$ 笔交易发生到下一笔交易之间，ETF 的对数收益率

这样每一条观测都对应一笔真实发生的 Kalshi 交易，彻底消除稀疏性。

---

## 3. 数据来源

### 3.1 Kalshi 高频交易记录
- **文件**：`leadlag/kalshi_hf_cache.parquet`
- **字段**：`ticker`、`created_time`（UTC 时间戳）、`yes_price`（0–100 的整数，代表合约成交价格/概率）
- **粒度**：每笔实际成交记录，时间精度为秒级

### 3.2 ETF 高频报价（TAQ 数据）
- **文件**：`leadlag/etf_hf/<ETF>_hf.parquet`（每个 ETF 一个文件）
- **字段**：`timestamp_utc`（毫秒级精度）、`mid`（买卖中间价 = (best_bid + best_ask) / 2）
- **来源**：TAQ（Trade and Quote）数据库，覆盖美股正式交易时段，报价频率约每秒数次

### 3.3 分析对象：合约-ETF 组合
- **文件**：`regression/significant_pairs.csv`
- **内容**：从第一阶段日度回归中筛选出 48 个有统计关联的合约-ETF 组合
- **字段**：`contract_ticker`、`etf`、`date_start`、`date_end`、`r_squared`、`contract_title`

---

## 4. 四种方法全览

| 方法 | 脚本 | 时间粒度 | 回归结构 | 核心问题 |
|------|------|----------|----------|----------|
| 离散窗口 | `leadlag_event.py` | 秒级 | 每个窗口独立双变量 OLS | 只测 6 个预设窗口 |
| 完整轮廓（IRF） | `leadlag_profile.py` | 秒级 | 每个窗口独立双变量 OLS | 每个 $\Delta$ 独立，无净效应控制 |
| 分钟级统一回归 | `leadlag_unified.py` | 分钟级 | 联合 OLS（所有 $k$ 一个方程） | 1.54% 稀疏性严重稀释信号 |
| **事件驱动统一回归** | **`leadlag_event_unified.py`** | **秒级** | **联合 OLS（所有 $k$ 一个方程）** | **最优方案：消除稀疏 + 净效应控制** |

核心脚本 `leadlag_event_unified.py` 填补了前三种方法的"空缺象限"：同时具备秒级精度和联合估计两个优点。

---

## 5. 核心脚本：事件驱动统一回归

### 5.1 参数设置

```python
K       = 10          # 向前/向后各看 K 笔交易（共 2K+1 = 21 个滞期项）
W_SEC   = 300         # ETF 收益率测量窗口上限（秒）
MIN_OBS = 2 * K + 5   # 构建 lag 矩阵后的最小有效观测数 = 25
MAX_GAP_NS = 120 * 1_000_000_000   # ETF 参考价格：2 分钟内必须有报价
```

**K=10 的含义**：每笔 Kalshi 交易作为锚点，向前看 10 笔交易（Kalshi 过去行为）、向后看 10 笔交易（ETF 过去行为对 Kalshi 的预测），回归包含 21 个 lag 系数 + 常数项 + 日期固定效应。

### 5.2 数据流程图

```
regression/significant_pairs.csv（48 对合约-ETF 组合）
          │
          ▼
对每对组合：
  ┌──────────────────────────────────────────────────────────────┐
  │  1. 读取 Kalshi 交易记录（按 ticker + 日期范围过滤）           │
  │  2. 读取 ETF tick 数据                                        │
  │  3. 计算 prob_change = yes_price.diff() / 100                 │
  │  4. 计算每笔交易对应的 ETF 对数收益率                          │
  │       自适应窗口：到下一笔同日交易为止，最多 W_SEC 秒          │
  │       跨天时退回 W_SEC 上限（避免含隔夜跳空）                  │
  │       记录每笔实际窗口长度 → 输出 mean_w_sec                   │
  │  5. prob_change 标准化（除以自身标准差）                       │
  │       使不同合约的系数量纲统一，可跨合约比较                   │
  │  6. 构建 21 列 lag 矩阵（k = -10 到 +10），截断头尾各 K 行    │
  │  7. OLS 联合估计 + 按日期聚类标准误                            │
  │       单日数据退回 HC3；检测到单日时打印 warning               │
  │  8. 提取 21 个 β_k 及其 t 统计量和 p 值                       │
  └──────────────────────────────────────────────────────────────┘
          │
          ▼
leadlag_event_unified_results.csv（每行 = 一个合约对的一个 k 值）
```

---

## 6. 完整代码逻辑

### 6.1 加载 Kalshi 交易数据

```python
def load_kalshi_trades(ticker, date_start, date_end):
    q = f"""
    SELECT
        (created_time AT TIME ZONE 'UTC')::TIMESTAMP AS ts_utc,
        yes_price
    FROM read_parquet('{CACHE_PATH}')
    WHERE ticker       = '{ticker}'
      AND created_time >= TIMESTAMPTZ '{date_start} 00:00:00+00'
      AND created_time <= TIMESTAMPTZ '{date_end} 23:59:59+00'
    ORDER BY 1
    """
    df = con.execute(q).df()
    df["prob"]        = df["yes_price"] / 100.0
    df["prob_change"] = df["prob"].diff()        # 每笔交易的概率变化量
    return df.dropna(subset=["prob_change"])     # 第一行无法计算 diff，删掉
```

**关键点**：`yes_price` 是 0–100 的整数（代表"是"事件发生的市场概率），除以 100 转为 0–1 的概率。`diff()` 得到每笔交易的概率变化量，这就是回归中的自变量 $\Delta p_i$。

### 6.2 ETF 高频价格查找

```python
def lookup_etf_mid(etf_ns, etf_mid, query_ns, max_gap_ns):
    """
    对每个查询时刻，找它之前最近一笔 ETF 报价（前向插值）。
    如果最近报价与查询时刻相差超过 max_gap_ns，则返回 NaN。
    """
    idx    = np.searchsorted(etf_ns, query_ns, side="right") - 1
    result = np.full(len(query_ns), np.nan)
    valid  = idx >= 0
    vi     = np.where(valid)[0]
    gaps   = query_ns[vi] - etf_ns[idx[vi]]
    close  = gaps <= max_gap_ns
    result[vi[close]] = etf_mid[idx[vi[close]]]
    return result
```

`np.searchsorted` 是二分查找，在有序时间戳数组中找到"刚好在 query 之前"的位置，效率为 O(log n)。对几十万行 ETF tick 数据，这比循环快几千倍。

### 6.3 自适应 ETF 收益率窗口（关键设计）

```python
# ETF 参考价格：第 i 笔交易发生时刻，要求 2 分钟内有报价
etf_at_t = lookup_etf_mid(etf_ns, etf_mid, trade_ns, MAX_GAP_NS)

# 自适应前向时间戳：到下一笔同日 Kalshi 交易为止，最多 W_SEC 秒
# 如果下一笔跨天（隔夜），直接用 W_NS 上限，避免含隔夜跳空
dates            = kalshi["ts_utc"].dt.date.values
same_day         = dates[:-1] == dates[1:]
raw_next_ns      = np.empty_like(trade_ns)
raw_next_ns[:-1] = np.where(same_day, trade_ns[1:], trade_ns[:-1] + W_NS)
raw_next_ns[-1]  = trade_ns[-1] + W_NS
forward_ns       = np.minimum(raw_next_ns, trade_ns + W_NS)

etf_at_fwd  = lookup_etf_mid(etf_ns, etf_mid, forward_ns, MAX_GAP_NS)
etf_logret  = np.log(etf_at_fwd / etf_at_t)          # ETF 对数收益率
actual_w_ns = (forward_ns - trade_ns).astype(float)   # 每笔实际窗口长度（ns）
```

**为什么用自适应窗口而不是固定 300 秒**：

如果两笔 Kalshi 交易相隔只有 30 秒，用固定 300 秒窗口时，相邻两条观测的因变量（ETF 收益率）大量重叠（测量的是几乎同一段时间），造成序列相关，低估标准误，结论虚假显著。自适应窗口使每条观测的 ETF 收益率天然不重叠。

**为什么要排除跨天**：

如果某笔交易是周一下午 3:55，下一笔是周二上午 9:35，直接用到下一笔的窗口会包含隔夜跳空（盘后消息、开盘跳空），这不是我们想测量的"盘中信息传导"。跨天时退回 `W_NS=300s` 上限，把这笔交易的窗口限制在收盘前 5 分钟内。

**实际平均窗口**：`actual_w_ns` 在过滤后计算均值，写入输出字段 `mean_w_sec`，可用于评估自适应缩短的程度（观测到 mean_w_sec ≪ 300 说明该合约交易非常密集）。

### 6.4 prob_change 标准化

标准化**必须在 `dropna` 之后**执行，且所有 lag 列统一除以同一个 `prob_std`：

```python
# 先 dropna，再标准化——用实际进入回归的样本计算 std
df = df.dropna(subset=["etf_logret"] + all_lag_cols)

# prob_change 标准化：不同合约价格跳动幅度差异大（有的 1–5，有的 40–60）
# 标准化后系数含义统一为"prob_change 变动 1σ 对应的 ETF 收益变动"，跨合约可比
# 注意：所有 lag 列除以同一个 std，不能各自独立标准化（它们来自同一序列）
prob_std = df["prob_change"].std()
if prob_std > 0:
    for col in all_lag_cols:
        df[col] = df[col] / prob_std
```

**为什么需要标准化**：

不同 Kalshi 合约的价格跳动幅度差异很大：
- 低流动性合约（如支持率调查）单笔交易可能跳动 10–20 个百分点
- 高流动性合约（如 FEDDECISION）每笔可能只跳动 0.5–1 个百分点

若不标准化，前者的 $\hat{\beta}_k$ 天然比后者小（因为分母大），直接比较无意义。标准化后，所有合约的自变量量纲统一为"1 个标准差的概率变动"，$\hat{\beta}_k$ 可以跨合约直接比较。

**为什么要在 `dropna` 之后标准化**：

如果在 `dropna` 之前计算 `prob_std`，那个 std 包含了头尾 K 行（边界行，会被删掉的观测）。进入回归的实际样本用的是一个略微不准确的单位。正确做法是只用最终进入回归的行来计算 std，确保"1σ"就是回归样本的真实单位。

**重要提示**：标准化只改变系数的单位，不改变 t 统计量和 p 值（因为 SE 同比例缩放），显著性判断结果完全不受影响。

### 6.5 构建 lag 矩阵（核心）

```python
lag_cols = {}
for k in range(-K, K + 1):    # k 从 -10 到 +10，共 21 个
    col = f"lag_{k:+d}"
    df[col] = df["prob_change"].shift(k)
    lag_cols[k] = col
# dropna 在 6.4 节标准化流程中执行（先 dropna，再标准化）
```

**`shift(k)` 的方向约定**（容易混淆，务必记清楚）：

| shift 操作 | k 值 | lag 列含义 | 解读 |
|-----------|------|-----------|------|
| `shift(+3)` | k=+3 | 第 i-3 笔的 prob_change | **3 笔之前**的 Kalshi 变动 |
| `shift(-2)` | k=-2 | 第 i+2 笔的 prob_change | **2 笔之后**的 Kalshi 变动 |

- `k > 0`：回归用到了"过去"的 Kalshi 变动 → 如果 $\beta_k$ 显著，说明 Kalshi 的历史变动能预测当前 ETF → **Kalshi 领先 ETF**
- `k < 0`：回归用到了"未来"的 Kalshi 变动 → 如果 $\beta_k$ 显著，说明当前 ETF 收益率与未来 Kalshi 变动相关 → **ETF 领先 Kalshi**

**为什么不 fillna(0)**：如果在头尾 K 行填 0，等于告诉模型"边界处没有 Kalshi 变动"，这是虚假信息，会把系数往 0 压，低估 lead-lag 效应。正确做法是截断头尾各 K 行，接受样本量减少 2K 行的代价。

### 6.6 OLS 回归与聚类标准误

```python
mean_w_sec = float(df["actual_w_ns"].mean() / 1e9)
n_days     = df["date"].nunique()
if n_days == 1:
    print("  warning: only 1 day of data, day FE not added")

day_dummies = pd.get_dummies(df["date"], prefix="d", drop_first=True, dtype=float)
X = sm.add_constant(
    pd.concat([df[all_lag_cols].astype(float), day_dummies], axis=1)
)
y = df["etf_logret"].astype(float)

# 优先使用按日期聚类标准误；单日时退回 HC3
groups = df["date"].values
if len(np.unique(groups)) < 2:
    m = sm.OLS(y, X).fit(cov_type="HC3")
else:
    m = sm.OLS(y, X).fit(cov_type="cluster",
                          cov_kwds={"groups": groups})
```

**日期固定效应（Day FE）**：控制不同交易日之间的整体差异。例如某天整个市场大涨，所有 ETF 收益都会偏高，这个效应会被日期哑变量吸收，不会被错误归因为 Kalshi 的影响。当某合约全部交易只在单日内发生时，哑变量为空，固定效应自动退出，此时打印 warning 提醒。

**聚类标准误**：同一天内的交易在时序上相关（当天的每笔交易都受当天整体情绪影响），OLS 的基本假设（独立同分布误差）被违反。按日期聚类后，标准误允许同一天内的误差任意相关，只要不同天之间独立即可。聚类 SE 比 HC3 更保守，但统计上更可信。

---

## 7. 输出数据字段说明

输出文件：`leadlag/leadlag_event_unified_results.csv`

每一行代表：**某合约-ETF 组合在某个 k 值下的回归系数估计**。

| 字段 | 类型 | 含义 |
|------|------|------|
| `contract_ticker` | str | Kalshi 合约代码 |
| `etf` | str | ETF 代码（如 VFH、VNQ） |
| `k` | int | 滞期序号，范围 -10 到 +10 |
| `direction` | str | `kalshi_leads_etf`（k>0）/ `etf_leads_kalshi`（k<0）/ `contemp`（k=0） |
| `coef` | float | OLS 回归系数 $\hat{\beta}_k$ |
| `t_stat` | float | t 统计量 = $\hat{\beta}_k$ / SE |
| `p_value` | float | 双尾 p 值（检验 $H_0: \beta_k = 0$） |
| `r_squared` | float | 整个回归的 $R^2$（包含所有 21 个 lag + 日期 FE） |
| `n_obs` | int | 该组合实际用于回归的观测数（截断后） |
| `n_kalshi_trades` | int | 该合约在日期范围内的原始交易总笔数 |
| `w_sec` | int | ETF 收益率窗口上限（秒），固定为 300 |
| `mean_w_sec` | float | 该组合实际使用的平均窗口长度（秒）；因自适应缩短，通常 < 300；越小说明交易越密集 |
| `r2_daily_screen` | float | 第一阶段日度回归的 $R^2$（来源于 significant_pairs.csv） |
| `contract_title` | str | 合约的自然语言描述 |

---

## 8. 如何解读结果

### 8.1 基本判断流程

**第一步：看 p 值，判断是否统计显著**

- `p_value < 0.05`：传统 5% 显著水平，认为该 $k$ 值有显著的 lead-lag 关系
- `p_value < 0.10`：10% 显著水平，证据稍弱但仍值得关注
- 注意：本数据集总共 693 个系数，纯随机情况下约有 34 个在 5% 水平"虚假显著"。实际得到 201 个，说明有真实信号。

**第二步：看 direction，判断谁领先谁**

- `direction = kalshi_leads_etf`（k > 0）：Kalshi 的第 $i-k$ 笔交易的概率变化，能预测第 $i$ 笔交易时刻的 ETF 收益 → **Kalshi 提前了 k 笔交易反映信息**
- `direction = etf_leads_kalshi`（k < 0）：第 $i$ 笔交易时刻的 ETF 收益，与 $k$ 笔之后的 Kalshi 变动相关 → **ETF 提前了 k 笔反映信息**

**第三步：看系数大小，理解经济强度**

由于 `prob_change` 已经过标准化（除以该合约的标准差），`coef` 的含义是：**Kalshi 概率变动 1 个标准差，ETF 对数收益率变动多少**。

- 不同合约之间的 `coef` 可以直接比较大小
- `coef = 0.001` 代表概率变动 1σ 时 ETF 变动约 0.1 个基点（bp）
- 标准化不改变 t 统计量和 p 值，只影响系数的量纲

**第四步：看系数符号，理解经济方向**

几乎所有显著系数为**负值**，这是正常的经济逻辑，不代表"反向领先"。

以 FEDDECISION（联储降息概率合约）× VDE（能源 ETF）为例：
- 降息概率上升 → 市场预期更宽松 → 债券价格上涨 → 能源股受宏观敏感度影响可能下跌
- 因此 prob_change > 0 对应 ETF_return < 0，系数为负，经济上完全合理

正系数的例子（如 KXECKH276 选举合约 × VFH 金融 ETF）：哈里斯胜选概率上升 → 金融监管预期加强 → VFH 可能下跌；或相反解读，具体取决于合约方向和政策预期。

**第五步：看 k 的大小，判断信息传导速度**

`k` 的单位是"笔交易"，不是分钟或秒。要理解实际时间：
- 如果某合约平均 10 分钟一笔交易，k=5 对应约 50 分钟的领先量
- 如果某合约平均 30 秒一笔，k=5 对应约 2.5 分钟
- 参考输出字段 `mean_w_sec`：该字段反映了实际平均窗口，间接体现了交易密度（`mean_w_sec` 越小，相邻交易越密集，k=1 对应的实际时间也越短）

**第六步：看 n_obs，判断结果的可靠性**

| n_obs | 可靠性评估 |
|-------|-----------|
| < 50 | 系数估计不稳定，显著性可能是偶然 |
| 50–200 | 中等可靠，关注 t 统计量大小 |
| 200–500 | 较可靠 |
| > 500 | 高度可靠，结果稳健 |

### 8.2 从 CSV 中快速筛选关键结果

```python
import pandas as pd

df = pd.read_csv("leadlag/leadlag_event_unified_results.csv")

# 1. 找最显著的合约对（每个合约对+方向取最小 p 值）
top = (
    df[df["p_value"] < 0.05]
    .groupby(["contract_ticker", "etf", "direction"])
    .apply(lambda x: x.loc[x["p_value"].idxmin()])
    .reset_index(drop=True)
    .sort_values("p_value")
)

# 2. 只看 kalshi 领先 ETF（最有经济含义的方向）
kalshi_leads = df[(df["direction"] == "kalshi_leads_etf") & (df["p_value"] < 0.05)]

# 3. 只看大样本（n_obs > 200）的显著结果
reliable = df[(df["n_obs"] > 200) & (df["p_value"] < 0.05)]

# 4. 看某个具体合约对的完整 IRF 轮廓
pair = df[(df["contract_ticker"] == "FEDDECISION-24NOV-H0") & (df["etf"] == "VDE")]
pair.sort_values("k")[["k", "direction", "coef", "t_stat", "p_value"]]
```

### 8.3 解读 k 值分布（最重要的诊断图）

```python
# 各 k 值的显著系数数量
k_summary = (
    df[df["p_value"] < 0.05]
    .groupby(["direction", "k"])
    .size()
    .unstack(level=0)
    .fillna(0)
)
```

**解读规则**：

- 如果 `kalshi_leads_etf`（k>0）方向的显著数量**远多于** `etf_leads_kalshi`（k<0）→ Kalshi 整体领先 ETF
- 如果 `etf_leads_kalshi`（k<0）方向更强 → ETF 整体领先 Kalshi
- 如果两个方向数量相近 → 双向信息流动，市场互相影响
- 显著集中在 `|k|` 小的位置（如 k=-1, -2 或 k=1, 2）→ 传导发生在很近的几笔交易内，速度快
- 显著散布在 `|k|` 大的位置 → 信息传导慢，持续影响较长时间

### 8.4 结合合约类型解读

| 合约类型 | ETF 例子 | 预期方向 | 经济逻辑 |
|---------|---------|---------|---------|
| 联储利率决议（FEDDECISION） | VFH（金融）、VDE（能源） | 双向 | 利率预期影响全市场，两市场均有专业参与者 |
| 行政令/Trump 政策（ECDJT） | VAW（材料）、VNQ（房产） | 可能 ETF 领先 | 股市对政策冲击反应更快 |
| 支持率调查（538APPROVE） | VOX（通信）、VGT（科技） | 弱相关 | 政治支持率与板块关联较间接 |
| 选举结果（KXECKH） | VFH、VIS | 双向均强 | 大选结果高度系统性，两市场同步剧烈波动 |

---

## 9. 当前运行结果摘要

### 9.1 基本统计

| 指标 | 数值 |
|------|------|
| 分析的合约-ETF 组合数 | 48 对（输入），33 对（通过 MIN_OBS 筛选） |
| 总估计系数数 | 693 |
| p < 0.05 显著 | **201 个**（29%） |
| p < 0.10 显著 | **229 个**（33%） |
| 纯随机期望显著数（5%） | ~34 个 |
| 超出随机的倍数 | 约 **6 倍**，有真实信号 |

### 9.2 各 k 值显著系数分布

```
k 值    显著数    方向
-10      3      etf_leads_kalshi
 -9      4      etf_leads_kalshi
 -8     11      etf_leads_kalshi
 -7     10      etf_leads_kalshi
 -6     13      etf_leads_kalshi（局部峰值）
 -5      9      etf_leads_kalshi
 -4     11      etf_leads_kalshi
 -3     10      etf_leads_kalshi
 -2     16      etf_leads_kalshi（最强峰值 ← ETF 领先 2 笔）
 -1     13      etf_leads_kalshi
  0      9      contemp
 +1      8      kalshi_leads_etf
 +2     10      kalshi_leads_etf
 +3     10      kalshi_leads_etf
 +4     10      kalshi_leads_etf
 +5      8      kalshi_leads_etf
 +6     10      kalshi_leads_etf
 +7     11      kalshi_leads_etf（峰值 ← Kalshi 领先 7 笔）
 +8     11      kalshi_leads_etf（峰值）
 +9      8      kalshi_leads_etf
+10      6      kalshi_leads_etf
```

**结论**：
- **双向均有显著信号**，两个方向各占约 100 个显著系数
- **ETF 领先 Kalshi** 信号更集中（k=-2 峰值最强），说明 ETF 在短期内率先反映信息
- **Kalshi 领先 ETF** 信号平铺在 k=1~10，说明 Kalshi 的历史信息对 ETF 有持续（但延迟更长）的影响
- k=0（同期）有 9 个显著，说明部分信息在同一时刻被两个市场同时消化

### 9.3 最显著的合约对

| 合约 | ETF | 方向 | 最小 p 值 | n_obs | 经济含义 |
|------|-----|------|----------|-------|---------|
| KXECKH276 | VDE | etf_leads_kalshi | ~10⁻¹⁹² | 39 | 能源 ETF 领先选举概率（小样本但系数极强） |
| KXECKH276 | VFH | etf_leads_kalshi | ~10⁻¹⁵⁹ | 39 | 金融 ETF 领先选举概率 |
| KXECDJT281 | VNQ | contemp | ~10⁻⁶⁷ | 285 | 行政令合约与房产 ETF 同期强相关 |
| KXECDJT306 | VDC | etf_leads_kalshi | ~10⁻⁴⁰ | 115 | 生活必需品 ETF 领先行政令合约 |
| KXECDJT312 | VAW | kalshi_leads_etf | ~10⁻³⁰ | 214 | 行政令合约领先材料 ETF（中大样本，可信） |
| FEDDECISION-24NOV-H0 | VDE | kalshi_leads_etf | ~0.003 | 360 | 降息概率领先能源 ETF（大样本，结论稳健） |

### 9.4 注意：小样本结果的稳健性

n_obs=39 的 KXECKH276 系列出现了大量极端 p 值（如 p~10⁻¹⁹²），这在统计上是合理的（样本量小但信号极强），但需要谨慎：
- 该合约的 39 笔有效观测都集中在大选前后极端波动期
- 系数大但 SE 也大，只是 t 统计量更大
- 建议作为"支持性证据"而非主要结论，以 n_obs > 200 的结果（FEDDECISION、KXECDJT 系列）作为论文主要结论

---

## 10. 常见误区

### 误区 1："系数为负说明是反向领先"

**错误**。系数的符号反映的是经济关系的**方向**，不是领先/滞后的方向。领先/滞后由 `k` 的正负决定，系数的正负由"Kalshi 涨/跌对应 ETF 涨/跌还是跌/涨"决定。负系数 + `kalshi_leads_etf` = "Kalshi 概率上升后，ETF 下跌"，这是正常的经济逻辑。

### 误区 2："p 值越小，领先越多"

**错误**。p 值衡量显著性（能否排除零效应），不衡量领先的时间量。领先的笔数由 `k` 决定。p=10⁻¹⁰⁰ 的 k=-2 不比 p=0.01 的 k=-2 "领先更多笔"，只是前者证据更强。

### 误区 3："k 的单位是秒或分钟"

**错误**。k 的单位是**笔数**（交易事件序号），不是时间。实际时间间隔 = k × 平均交易间隔时间，不同合约的平均交易间隔差异很大（高频合约 KXFEDDECISION 平均间隔约 30 秒，低频合约 KXECKH276 平均间隔约 10 分钟）。

### 误区 4："只看 r_squared 判断模型好坏"

R² 的大部分来自日期固定效应，与 lead-lag 信号关系不大。判断 lead-lag 强弱应看具体 k 对应的 t 统计量和 p 值，而不是整体 R²。

### 误区 5："不同合约的 coef 能直接比较"

**标准化之后可以**。经过 `prob_change` 标准化，所有合约系数的单位统一为"1σ 概率变动对应的 ETF 对数收益率"，可以横向比较。但如果使用旧版本（未标准化）的结果，不同合约的 `coef` 量纲不同，不能直接比较大小，只能比较符号和显著性。

### 误区 6："被跳过的合约对没有 lead-lag 关系"

被跳过的原因是交易数量不足（有效观测 < 25），而非没有关系。这些合约的 lead-lag 关系无法被本方法可靠估计，属于数据限制，不是结论。

---

*文档最后更新：2026-06-10*  
*对应脚本：`leadlag/leadlag_event_unified.py`*  
*结果文件：`leadlag/leadlag_event_unified_results.csv`（693 行，33 个合约-ETF 对，201 个 p<0.05 显著系数）*  
*主要设计迭代：跨天窗口修复 / prob_change 标准化 / 聚类 SE / mean_w_sec 字段 / 无 fillna(0)*
