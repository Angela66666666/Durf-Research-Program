# Granger 联合因果检验 (Granger joint causality test)

高频 lead-lag 的 **headline 统计量**：每个方向一条单向回归 + 一个联合 Wald 检验，给**一个 p 值**。
取代旧 pipeline「对称大方程逐个系数数显著个数」的做法。这是本项目**日频** `Var.py` 里
`results.test_causality(...)`（VAR Granger Wald）在高频上的还原，也是导师反馈直接要求的对象。

生成脚本：`pipeline/leadlag_granger.py`（单合约）、`pipeline/merge/merge_granger.py`（合并超信号）。
引擎函数：`leadlag_common.run_granger_direction`（linear）、`run_granger_probit`（probit）。

---

## 1. 模型设定 (Specification)

对每个 pair，跑两个方向（各一条独立回归，**只放对方的过去** + 自身的过去）：

**方向 1 — Kalshi 是否 Granger-导致 ETF**
```
etfret_t = a + Σ_{i=1..p} φ_i·etfret_{t-i}   ← ETF 自身过去(自相关控制, p 由 BIC 选)
             + Σ_{j=1..K} b_j·Δprob_{t-j}     ← 只放「过去的」Δprob
             + 日固定效应 + ε
H0 : b_1 = b_2 = … = b_K = 0     ← 一个联合 Wald → 一个 p 值
```
拒绝 H0 ⟹ 在 ETF 自身历史之外，过去的合约变动能帮预测 ETF ⟹ **Kalshi 领先**。

**方向 2 — ETF 是否 Granger-导致 Kalshi**（把 cause/effect 对调）
```
Δprob_t = c + Σ_{i=1..q} ψ_i·Δprob_{t-i} + Σ_{j=1..K} d_j·etfret_{t-j} + 日FE
H0 : d_1 = … = d_K = 0
```

两方向 p 一比即得结论：一边显著=单向领先；都显著=双向；都不显著=无。判定阈值 **p < 0.05**
（Granger 是单个联合检验，用 0.05 惯例；与逐系数报告里的分级 p<0.15 是不同对象）。

**与旧「对称大方程」的关键区别（这才是教科书 Granger）：**
- 只放 cause 的**过去**（j ≥ 1）；剔除**同期** j=0（瞬时相关，判不了方向）与**未来** j<0（那是反方向）。
- 用一个 **Wald 联合检验**取代逐系数计数，避免 2K+1 个 t 检验的多重检验散点。

---

## 2. 标准误：面板 Newey-West (hac-panel)，不用按日聚类

联合 Wald 需要一个**满秩**的稳健协方差。按日聚类的协方差**秩 ≤ 交易日数**；本项目很多事件合约
（选举、FOMC）**只有 1~几天**数据，联合检验 K 个约束、当 K ≥ 天数时就**秩亏** → Wald χ²/p **失效**
（会算出 p=0、1e-200 之类的假显著——实测确实如此）。

改用 **`hac-panel`（面板 Newey-West，带宽=K，按交易日分块）**：
- **满秩** → 单日/少数天的合约也能给出有效联合 p；
- 在**每个交易日块内**算 Newey-West，**不跨隔夜**串扰（比普通 HAC 更干净）；
- 是高频日内 lead-lag 的**微观结构标准**协方差。

日固定效应仍保留（去掉各日均值），滞后仍按交易日 shift、不跨隔夜。

> **口径说明（项目一致性）**：只有 **Granger 联合检验**用 hac-panel——因为联合检验数学上必须要满秩
> 协方差，聚类在少天数下给不了。其余**逐系数** pipeline（calendar/event/probit）仍用**按日聚类**，
> 保持不变。不同统计量各用最合适的 SE，属有意为之。

---

## 3. 平稳性 → 无需协整 (Stationarity)

Granger 要求平稳。本项目 x=Δprob、y=log-return **都是差分后**的序列，天然平稳 ⟹ 直接用
VAR-式 Granger 即可，**不需要**协整/VECM。（协整/Hasbrouck 是另一条独立路线：需要先把 ETF
构造成与 Kalshi 概率同量纲的可交易篮子，才谈得上共同基本面价值与误差修正。）

---

## 4. Probit 版（方向-only 的对应检验）

被解释变量换成「ETF 涨/跌」离散方向（导师建议的 probit 对应版）：
```
Pr(ETF↑_t) = Φ( α + Σ_{i=1..p} φ_i·↑_{t-i} + Σ_{j=1..K} b_j·Δprob_{t-j} )
H0 : b_1 = … = b_K = 0     ← 对 forward Δprob 那组系数做联合 Wald(hac-panel)
```
只做 Kalshi→ETF 方向（因变量离散）；自身方向滞后阶 p 由 **probit-BIC** 选；up=1[y>0]，剔除 y==0。

---

## 5. 合并超信号版 (`merge_granger.py`)

把每个超信号当「一个合成合约」，对其 ETF 并集里每个 ETF 做同样的双向 linear + probit Granger。
沿用 `merge_leadlag` 的池化范式：成员 Δprob **符号对齐后堆叠**（不拼价格）、shift 在 (成员×日) 内、
linear 用**成员固定效应**、probit 不放 FE；标准误用 **hac-panel（按 成员×日 分块）**。

---

## 6. 输出 (Outputs)

- `pipeline/leadlag_granger_pairs.csv` —— 每行 = pair × mode(calendar/event) × spec(linear/probit) × direction
- `pipeline/merge/leadlag_merged_granger.csv` —— 每行 = group × etf × mode × spec × direction

列：`K, n_ylags(自身滞后阶), wald_chi2, wald_df(=K), p_value, n_obs, n_days, n_active` 等。
