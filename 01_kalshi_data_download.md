# Kalshi 预测市场数据下载指南

## 研究背景

本项目研究**Kalshi预测市场合约**与**行业股票ETF**之间的领先滞后关系。
具体以2024年美国大选为事件，分析预测市场和股票市场谁先反映信息。

### 数据需求
- **Kalshi数据**：2024年9月1日～11月5日，大选相关合约的每日价格
- **ETF数据**：同期各行业Vanguard Sector ETF的每日收益率

---

## 环境准备

### 系统要求
- Mac 或 Windows 电脑
- Python 3.9+
- 网络连接

### 第一步：安装 uv（Python包管理工具）

**什么是uv？** 专门管理Python项目依赖的工具，类似于"帮你把所有需要的库装好"。

**Mac：**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

**验证安装成功：**
```bash
uv --version
# 应该显示类似：uv 0.11.15
```

---

## 下载项目代码

### 第二步：克隆GitHub项目

```bash
git clone https://github.com/Jon-Becker/prediction-market-analysis
cd prediction-market-analysis
```

**什么是git clone？** 把GitHub上的项目代码完整复制到你的电脑上。

### 第三步：安装项目依赖

```bash
uv sync
```

**什么是依赖？** 这个项目运行需要的所有Python库（如pandas、duckdb等），`uv sync`会自动全部安装好。

安装完成后你会看到类似：
```
Installed 84 packages in 151ms
```

---

## 下载Kalshi数据

### 第四步：运行数据收集工具

```bash
make index
```

这会打开一个交互式菜单：
```
> Kalshi Markets: Backfills Kalshi markets data to parquet files
  Kalshi Trades: Backfills Kalshi trades data to parquet files
  ...
```

### 第五步：先下载Markets数据（合约基本信息）

用**上下箭头**选择 `Kalshi Markets`，按**回车**确认。

**Kalshi Markets vs Kalshi Trades的区别：**

| | Kalshi Markets | Kalshi Trades |
|---|---|---|
| 每行是什么 | 一个合约的基本信息 | 一笔成交记录 |
| 包含什么 | ticker、合约名称、开始/结束时间 | 成交时间、价格、数量 |
| 数据量 | 小（几百MB） | 大 |
| 用途 | 找到大选合约的ticker名称 | 计算每日价格变动Δp |

**注意：** 数据从最新合约开始下载，2024年数据在约350,000条之后出现。
当显示到约350,000条时，按 `Control + C` 暂停，检查是否有2024年数据。

数据保存在：
```
data/kalshi/markets/
```

格式为Parquet文件（可用pandas读取）。

---

## 筛选大选合约

### 第六步：搜索大选相关合约

新建文件 `find_election_contracts.py`，内容如下：

```python
import duckdb
from pathlib import Path

base_dir = Path("/你的电脑路径/prediction-market-analysis")
markets_dir = base_dir / "data" / "kalshi" / "markets"

con = duckdb.connect()

df = con.execute(f"""
    SELECT ticker, title, status, close_time, volume
    FROM '{markets_dir}/*.parquet'
    WHERE (
        title ILIKE '%president%' OR
        title ILIKE '%trump%' OR
        title ILIKE '%harris%' OR
        title ILIKE '%election%'
    )
    AND close_time >= '2024-09-01'
    AND close_time <= '2024-11-30'
    ORDER BY volume DESC NULLS LAST
""").df()

print(f"找到 {len(df)} 个相关合约\n")
print(df.to_string())
```

运行：
```bash
uv run find_election_contracts.py
```

从结果中找到**交易量最大**的主合约，记下它的`ticker`。
通常是类似 `KXPRES-2024-TRUMP` 这样的格式。

---

## 下载Trades数据（价格历史）

### 第七步：下载目标合约的成交数据

找到ticker之后，重新运行：
```bash
make index
```

这次选择 `Kalshi Trades`，程序会下载所有合约的成交记录。
找到目标合约的数据后按 `Control + C` 停止。

或者用以下脚本直接通过API下载（需要知道正确的ticker）：

```python
import requests
import pandas as pd

TICKER = "你找到的ticker"  # 例如 KXPRES-2024-TRUMP

response = requests.get(
    "https://api.elections.kalshi.com/trade-api/v2/markets/trades",
    params={
        "ticker": TICKER,
        "limit": 1000,
    }
)

data = response.json()
trades = data.get("trades", [])
df = pd.DataFrame(trades)
print(df.head())
```

---

## 数据处理

### 第八步：计算每日价格变动 Δp

```python
import pandas as pd

# 读取trades数据
df = pd.read_parquet("data/kalshi/trades/你的文件.parquet")

# 筛选目标合约和时间范围
df = df[df["ticker"] == "KXPRES-2024-TRUMP"]
df["date"] = pd.to_datetime(df["created_time"]).dt.date
df = df[(df["date"] >= pd.to_datetime("2024-09-01").date()) &
        (df["date"] <= pd.to_datetime("2024-11-05").date())]

# 每天取最后一笔成交价作为收盘价
daily_price = df.groupby("date")["yes_price"].last()

# 差分得到每日价格变动 Δp
delta_p = daily_price.diff()
delta_p.name = "delta_p_kalshi"

# 保存为CSV
delta_p.to_csv("kalshi_daily_delta_p.csv")
print(delta_p)
```

**价格说明：** `yes_price`的单位是分（cents），65表示隐含概率65%。

---

## 文件结构说明

```
prediction-market-analysis/
├── README.md                    # 项目说明
├── Makefile                     # 定义make命令
├── pyproject.toml               # 依赖列表
├── src/
│   ├── indexers/kalshi/         # 数据收集代码
│   └── analysis/kalshi/        # 分析脚本
├── data/
│   └── kalshi/
│       ├── markets/             # 合约基本信息（Parquet）
│       └── trades/              # 成交记录（Parquet）
├── find_election_contracts.py   # 我们写的搜索脚本
└── get_kalshi_data.py           # 我们写的API脚本
```

---

## 常用命令速查

| 命令 | 作用 |
|---|---|
| `cd 路径` | 进入某个文件夹 |
| `ls` | 查看当前文件夹内容 |
| `pwd` | 查看当前在哪个文件夹 |
| `uv sync` | 安装项目依赖 |
| `make index` | 启动数据收集菜单 |
| `uv run 文件名.py` | 运行Python脚本 |
| `Control + C` | 停止当前运行的程序 |
| `rm -rf 文件夹/` | 删除文件夹及其内容 |

---

## 注意事项

1. **数据从最新往旧下载**，2024年数据需要等待较长时间才出现
2. **按Control+C停止**不会损坏已下载的数据，进度自动保存
3. **Parquet文件**需要用pandas或duckdb读取，不能直接用Excel打开
4. **yes_price单位是分**，需要除以100得到概率（0-1之间）
5. Kalshi公开API**只返回当前active的合约**，历史合约需通过本地数据获取
