# load

[![CI](https://github.com/20070316lbw-netizen/load/actions/workflows/ci.yml/badge.svg)](https://github.com/20070316lbw-netizen/load/actions/workflows/ci.yml)

个人量化数据存储包, 使用 `pyarrow` 对数据以 `.parquet` 文件形式存取。

**这个仓库只做一件事：把调用方传入的 DataFrame 存成 `.parquet` 文件, 或者把
它读回来**。不含任何数据清洗、也不做任何抓取。与抓取用的
[`sources`](https://github.com/20070316lbw-netizen/sources) 是平级关系而非
上下游——`load` 不依赖、不 import 它, 待存储的 DataFrame 可以来自任何地方。

## 安装

作为私有 GitHub 仓库，在其他项目里用 `uv add` 直接从 git 安装：

```bash
# 装最新 main
uv add "git+https://github.com/20070316lbw-netizen/load.git"
```

## 快速使用

```python
from load import (
    save_constituents,
    save_listings,
    save_prices_long,
    save_prices_multiindex,
    save_fundamentals_long,
    save_fundamentals_multiindex,
    save_riskfree_long,
    save_riskfree_multiindex,
    to_factors_long,
    save_factors_long,
    save_factors_multiindex,
    read_parquet,
)

# df 可以来自任何地方(比如你自己的 sources 包、一次性脚本、别的数据源),
# load 本身不关心来源, 只管按下面的格式存成 parquet。

# 成分股 / 交易所归属: 都是静态快照, 只有一种存法
save_constituents("data/constituents.parquet", constituents_df)
save_listings("data/listings.parquet", listings_df)

# 行情 / 基本面 / 无风险利率: 长表、MultiIndex 两种格式各存一份
save_prices_long("data/prices_long.parquet", prices_df)
save_prices_multiindex("data/prices_by_date_ticker.parquet", prices_df)

save_fundamentals_long("data/fundamentals_long.parquet", fundamentals_df)
save_fundamentals_multiindex("data/fundamentals_by_period_ticker.parquet", fundamentals_df)

save_riskfree_long("data/riskfree_long.parquet", riskfree_df)
save_riskfree_multiindex("data/riskfree_by_date_series.parquet", riskfree_df)

# 因子: 因子包(比如 momfactor)算出来的是一个 [date, ticker] MultiIndex
# Series, 不是长表, 所以先用 to_factors_long 转成 tidy long 格式
# [date, ticker, factor, value], 再存(同一 (date, ticker) 通常对应多个
# factor, 存法跟 fundamentals 一样不做透视/聚合)
momentum_long = to_factors_long(momentum_series, "mom_12_1")
save_factors_long("data/factors_long.parquet", momentum_long)
save_factors_multiindex("data/factors_by_date_ticker.parquet", momentum_long)

# 如果 df 里日期/代码列不叫 date/ticker(比如叫 dt/symbol), 不用现改列名,
# 传参覆盖就行:
save_prices_multiindex(
    "data/prices_by_dt_symbol.parquet",
    prices_df,
    date_col="dt",
    ticker_col="symbol",
)

# 读回来: 不管当初存的是长表还是 MultiIndex 版本, 都是同一个入口
prices_back = read_parquet("data/prices_long.parquet")
```

`save_*` 系列只负责落盘, 不会自动抓取; 拿到 `df` 后可以先自行检查/复用, 再
决定存长表还是 MultiIndex 版本(或者两个都存)。

## 各存储模块

| 模块 | 存储对象 | 函数 | 备注 |
| --- | --- | --- | --- |
| `_parquet` | 通用 parquet 读写, 所有模块共用的唯一入口 | `write_parquet(df, path)` / `read_parquet(path)` | 写入时自动创建父目录; 具名索引/MultiIndex 连同索引一起写, 普通 RangeIndex 长表只写数据列; 读取时按文件里实际存的内容自动恢复索引 |
| `about_constituents` | 成分股名单 | `save_constituents(path, df)` | 静态快照, 不区分长表/MultiIndex |
| `about_listings` | 交易所归属 | `save_listings(path, df)` | 静态快照, 同 constituents 一样不区分长表/MultiIndex |
| `about_prices` | 行情 | `to_prices_multiindex()` / `save_prices_long()` / `save_prices_multiindex()` | 长表 `[date, ticker, ...]`; MultiIndex 按 `[date, ticker]` 建索引; 列名不叫 `date`/`ticker` 时可用 `date_col`/`ticker_col` 覆盖 |
| `about_fundamentals` | 基本面 | `to_fundamentals_multiindex()` / `save_fundamentals_long()` / `save_fundamentals_multiindex()` | 长表 `[ticker, concept, period_end, ...]`; MultiIndex 按 `[period_end, ticker]` 建索引(同一 `(period_end, ticker)` 可能对应多个 `concept`, 索引不保证唯一); 列名不叫 `period_end`/`ticker` 时可用对应参数覆盖 |
| `about_riskfree` | 无风险利率 | `to_riskfree_multiindex()` / `save_riskfree_long()` / `save_riskfree_multiindex()` | 长表 `[date, series, value]`; MultiIndex 按 `[date, series]` 建索引; 列名不叫 `date`/`series` 时可用 `date_col`/`series_col` 覆盖 |
| `about_factors` | 因子(比如 momfactor 算出来的动量) | `to_factors_long()` / `to_factors_multiindex()` / `save_factors_long()` / `save_factors_multiindex()` | 唯一一个入口是 Series 而不是长表: `to_factors_long(s, factor)` 把因子包返回的 `[date, ticker]` MultiIndex Series 转成长表 `[date, ticker, factor, value]`(`factor` 参数就是因子名, 比如 `"mom_12_1"`); 之后跟其他模块一样有长表/MultiIndex 两种存法, `[date, ticker]` 索引同样不保证唯一(同一天同一只票可能有多个 factor) |

所有公开 API 也可直接从 `load` 顶层导入, 例如 `from load import save_prices_long`。

## 开发

```bash
uv sync
uv run ruff check .
uv run pytest -v
```

测试全部用手造的小 DataFrame 落盘到 `tmp_path` 再读回来验证, 不触发任何
网络请求；CI(见 `.github/workflows/ci.yml`)在 push/PR 到 `main`/`master`
时会跑同样这两步。
