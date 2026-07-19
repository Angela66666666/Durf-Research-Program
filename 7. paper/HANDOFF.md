# 项目交接文档

**最后更新**:2026-07-11(用户换电脑前)
**项目**:Do Prediction Markets Lead Stock Markets — Evidence from Information Shock(NYU)

---

## ★★★ 一眼看清:进度到哪了 + 现在该做什么(TL;DR)

> **当前主线 = Hasbrouck / VECM 子项目**(在 `Hasbrouck methodology/` 文件夹里)。
>
> - **Step 1 + Step 2 已完成**,而且导师(2026-07-10)**已拍板用 "Version B"**。
>   Version B = 用 **Polymarket** 的「Trump 当选」合约估 β,构造出选举因子模拟组合(篮子)。
> - **下一步 = Step 3 + Step 4**,代码还没开始写,但设计已经全部想清楚(见下面第三节)。
>
> **另一条线(lead-lag / Granger)已基本收尾**,只剩一个 Pull Request 等导师 review,见第五节。那条线现在不用动。

**换电脑后,新的聊天框可以直接说「继续做 Hasbrouck 的 Step 3」,我会接着往下。**

---

## ⚠️ 换电脑后先做这几件事

1. **两个工作目录**:
   - **优盘**:`/Volumes/PHILIPS/Durf/`(exFAT,随身带,装全部原始数据 ~73G)。
   - **本地**:上一台是 `/Users/liu/Desktop/Durf/`(跑代码在这)。**Hasbrouck 文件夹 + 代码都已于 2026-07-11 从本地同步到优盘,两边一致。**
   - 优盘会生成 `._*` / `.DS_Store` 垃圾,glob 一律用精确模式(如 `trades_*.parquet`,别用 `*.parquet`)。
2. **找可用 Python**:上一台是 anaconda 的 `python`(跑时加 `-W ignore`),装了 duckdb / pandas / statsmodels / matplotlib / yfinance。新电脑 `python -c "import duckdb,pandas,statsmodels,matplotlib,yfinance"` 能过即可。
3. **Step 3/4 需要的大数据优盘上已经有了**:Kalshi 成交(`prediction-market-analysis/data/kalshi/trades/` 7000+ parquet)、ETF 高频(`leadlag/etf_hf/` 11 个 parquet)。不用重下。

---

## 一、必须遵守的规则(导师抓过包)

1. **不查证不下笔**:任何「现实世界发生过什么」(日期 / 谁讲话 / 什么公告 / 经济数据)必须先 WebSearch/WebFetch 验证附 URL,搜不到写「待验证」,绝不编造。
2. **样本选择必须服务研究问题**:选 event window / 合约 / ETF 前先问「跟要测的关系对得上吗」。
3. **方法论一次定死、全项目统一**:时区(ET)、单位(ETF log return、Δprob)、bar、变量定义定一次就全脚本统一。lead-lag 口径集中在 `leadlag/pipeline/leadlag_common.py`。
4. **对外文件里不出现任何人**:发给导师 / 组员的文件(代码注释、docstring、print、报告 txt/md)一律**英文**,**不写任何人名、不写谁做错了什么**,只中性陈述事实。(聊天用中文没关系。)交付前 grep 一遍人名和中文字符。

---

## 二、Hasbrouck 子项目:已完成的 Step 1 + Step 2

**文件夹**:`Hasbrouck methodology/`

### 目标(导师给的四步法)
把 11 只 Vanguard 行业 ETF 组成一个「选举因子篮子」,让它像一个「Trump 当选概率」的合成资产,再和 Kalshi 的真实概率做 **Hasbrouck 信息份额 / VECM 误差修正**,看谁领先。

- **Step 1**:估每只 ETF 对「P(Trump 当选) 变化」的敏感度 β。
- **Step 2**:把 β 变成篮子权重(三种配权:符号等权 / β 加权 / 最小方差)。
- **Step 3**:用篮子权重,在高频因果网格上造出「篮子价格 / 隐含概率」曲线。← 下一步
- **Step 4**:篮子隐含概率 vs Kalshi 真实概率,做协整 + VECM + Hasbrouck。← 下一步

### Version B(导师已选定)—— 关键决定
- **β 来自 Polymarket** 的合约 "Will Donald Trump win the 2024 US Presidential Election?"
  (YES token `21742633143463906290569050155826241533067272736897614950488156847949938836455`;
  CLOB 接口只吃 `interval=max&fidelity=1440`,且必须带 `User-Agent` header 否则 403)。
- **β 窗口**:2024-06-20 → 07-31(29 个交易日),覆盖三个盘外外生事件,其 ETF 反应日为
  06-28(辩论)、07-15(枪击)、07-22(拜登退选)。
- **结果**:联合 F 检验 p = 0.0022;符号符合「Trump 交易」直觉(金融/能源 ↑,公用事业/材料 ↓);
  样本内 R² 0.75,但**样本外 R² ≈ 0**(只有最小方差篮子 +0.03)→ 11 只行业 ETF 只能**部分**张成选举因子,论文要写明。
- **为什么不用 Kalshi 估 β**:Kalshi 的「Trump 当选」合约 `PRES-2024-DJT` 第一笔成交是 **2024-10-04**
  (CFTC 禁令,直到 2024-10-02 D.C. 巡回法院驳回其 stay 申请才上线);三个事件日全在禁令期内。
  纯 Kalshi 十月版试过 → F p=0.35、样本外 R²=−2.52,识别不出来。选举人票计数合约(`KXECDJT270` 等)对 P(Trump) **非单调**,不能用。

### Step 1+2 的产出文件(都在 `Hasbrouck methodology/`)
| 文件 | 是什么 |
|---|---|
| `step1_step2_polymarket_beta_and_weights.py` | **主脚本**(全英文,无人名)。Step 1 估 β + Step 2 三种权重 + 稳健性 |
| `etf_election_beta_polymarket.csv` | **篮子**:11 个 β + 三组权重(`weight_plan_{a,b,c}`)。**Step 3/4 读这个** |
| `step1_basket_report_EN.txt` | 可发的英文报告(篮子表、三 plan 对比、R²、稳健性、数据来源) |
| `step1_polymarket_diagnostics.txt` | 技术附录(三套样本设定的完整输出) |
| `polymarket_trump_2024_daily.csv` | 缓存的 P(Trump) 日线(只下一次) |
| `etf_data/vanguard_sector_etf_total_returns_2024h1.csv` | 今天新下的 1–8 月 ETF 日频总收益(β 用) |
| `step1_election_beta.py` + `etf_mimic_diagnostics.txt` | 纯 Kalshi 版(证明此路不通,论文附录用) |
| `regression_screen_results(1).csv`、`plan{a,b}(1).py`、`planc_fixed.py`、`archive/` | 组员那版的输入/脚本(**别改别当自己的**);archive 里是早期迭代 |

---

## 三、下一步:Step 3 + Step 4 的设计(已想清,未写代码)

**检验窗口**:`PRES-2024-DJT` on Kalshi,2024-10-04 → 11-05(23 个 ETF 交易日)。
11/6 之后概率钉在 0.97,没信息量。可考虑再切一个 10-21 → 11-05 的高流动性子窗口做稳健性。

**一个必须报告的坑**:Kalshi 流动性从 10 月初约 **0.5 笔/分钟** 涨到 11/5 的 **64 笔/分钟**。
早期 bar 大量是 ffill 出来的陈旧价格,这会**系统性地让 Hasbrouck 偏向「ETF 领先」**。
所以要么加流动性子窗口,要么把「Kalshi 真正更新过的 bar 占比」报出来。

**两边对称构造**:在同一条因果 RTH(盘内)网格上采样。
- Kalshi 侧:每个网格点取 ≤ 该点的最后一笔成交(**含隔夜/周末成交**),使隔夜跳动落在当天第一根 bar。
- ETF 侧:同样处理,隔夜跳空 = 当天第一根 bar vs 前一天最后一根 bar。两条序列对称。
- 复用 `leadlag/pipeline/leadlag_common.py` 的 `causal_bars` / 盘内过滤 / ET 口径。

**隐含概率不用另外校准**:因为篮子 `w'β = 1`,篮子累计收益本身就是概率单位。
`implied_prob_t = p0 + cumsum(篮子收益)`,起点 p0 锚在第一根 bar 的 Kalshi 概率上。

**Step 4**:在 `(kalshi_prob, implied_prob)` 上:
Engle-Granger / Johansen 协整 → VECM → 看 α 误差修正载荷 → Hasbrouck information share(两种 Cholesky 排序给上下界)+ Gonzalo-Granger component share 做稳健性。

---

## 四、Step 1+2 已解决 / 已确认的点(避免重复踩)

- Polymarket 三个事件日全部**盘外**(辩论 6/27 21:00、枪击 7/13 18:11、退选 7/21 13:54),反应落在下一交易日 —— 已 WebSearch 核实。
- 三种配权只有 **plan A(符号等权)** 权重符号严格跟 β 走;plan B 去均值会把两只小 |β| 的推过零点;plan C 因对冲相关性差得更多。
- headline 用 `window`(29 天)而非 `event`(19 天):后者 F p=0.076,前者 F p=0.0022,且 plan C 样本外由负转正。
- circularity 已彻底排除:β 在 Polymarket 6–7 月,检验在 Kalshi(10/04 起),**时间和交易场所都不相交**。

---

## 五、另一条线(lead-lag / Granger)——已收尾,只等一个 PR

> 这条线现在**不用动**,除非导师对 PR 提意见。

- 主 pipeline(calendar/event/probit)、merge(合并相似合约)、标准 Granger 联合因果检验 **全部完成**,三份报告已产出。主战场 `leadlag/pipeline/`,共享引擎 `leadlag_common.py`。
- **在途**:PR **#2** `https://github.com/Angela66666666/Durf-Research-Program/pull/2`(base `main` ← compare `granger`)。里面 = 用户的 10 个 Granger 文件 + 组员的 8 个 benchmark 文件。已发导师,**等 review**。
- 导师若提意见 → 在 `granger` 分支改完 push,PR 自动更新 → 导师 OK 后合并进 `main`。
- 关键发现(写论文用):加固方法后**没有干净的单向领先**,可靠组反略偏「ETF 领先」;数据不对称(Kalshi=成交、ETF=NBBO mid 刷新勤)可能让 ETF 显得先动。

---

## 六、关键文件位置

```
GitHub(lead-lag 那条线的最新真相):git@github.com:Angela66666666/Durf-Research-Program.git
  分支:angela(草稿)/ main(干净)/ granger(= PR #2)
  注意:Hasbrouck 文件夹目前只在本地 + 优盘,还没进 git。

本地 / 优盘工作副本:
├── Hasbrouck methodology/            ← ★当前主战场(Step 1+2 done,Step 3+4 待做)
│   ├── step1_step2_polymarket_beta_and_weights.py   ← 主脚本
│   ├── etf_election_beta_polymarket.csv             ← 篮子(Step 3/4 读它)
│   ├── step1_basket_report_EN.txt / step1_polymarket_diagnostics.txt
│   ├── polymarket_trump_2024_daily.csv
│   ├── step1_election_beta.py / etf_mimic_diagnostics.txt   ← 纯 Kalshi 版(附录)
│   └── archive/ , plan*.py , regression_screen_results(1).csv  ← 组员那版 + 早期迭代
├── leadlag/
│   ├── GRANGER_TEST.md
│   ├── etf_hf/ *.parquet             ← ETF NBBO 高频(Step 3/4 要用;大,仅优盘)
│   └── pipeline/                     ← lead-lag 主战场,leadlag_common.py 是共享引擎
├── etf_data/
│   ├── vanguard_sector_etf_total_returns.csv         ← 9–12 月日频(旧)
│   └── vanguard_sector_etf_total_returns_2024h1.csv  ← 1–8 月日频(新,β 用)
├── prediction-market-analysis/data/kalshi/trades/trades_*.parquet  ← Kalshi 成交(大,仅优盘)
└── regression/significant_pairs.csv  ← lead-lag 的 48 对主输入

优盘 /Volumes/PHILIPS/Durf/:全部原始数据(~73G) + 全部工作文件(2026-07-11 同步) + .git(旧,以 GitHub 为准)
```

环境:anaconda `python`(跑加 `-W ignore`)。Kalshi glob 用 `trades_*.parquet`。时区一律 `America/New_York`。
