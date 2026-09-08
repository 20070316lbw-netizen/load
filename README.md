# load

个人量化数据存储包, 使用 `pyarrow` 对数据以 `.parquet` 文件形式进行存储。
仓库只做: 将传入的 DataFrame 存储并按调用方指定的路径返回对应的 `.parquet` 文件,
不含任何数据清洗、也不做任何抓取。与抓取用的 [`sources`](https://github.com/20070316lbw-netizen/sources)
是平级关系而非上下游——`load` 不依赖、不 import 它, 待存储的 DataFrame 可以
来自任何地方。

## 结构

- `load._parquet.write_parquet(df, path)`: 唯一的落盘入口, 自动创建父目录;
  若 `df` 使用具名索引/`MultiIndex` 会连同索引一起写入, 普通 `RangeIndex` 长表
  则只写数据列。
- `load.about_constituents`: 成分股名单存储(静态名单, 不区分长表/MultiIndex)。
  - `save_constituents(path, df)`
- `load.about_prices`: 行情数据存储, 长表 `[date, ticker, ...]` 和按
  `[date, ticker]` 建索引的 MultiIndex 版本可分别存储; 列名不叫 `date`/
  `ticker` 时可用 `date_col`/`ticker_col` 覆盖(默认值就是 `"date"`/
  `"ticker"`)。
  - `to_prices_multiindex(df, *, date_col="date", ticker_col="ticker")`
  - `save_prices_long(path, df)`
  - `save_prices_multiindex(path, df, *, date_col="date", ticker_col="ticker")`
- `load.about_fundamentals`: 基本面数据存储, 长表 `[ticker, concept,
  period_end, ...]` 和按 `[period_end, ticker]` 建索引的 MultiIndex 版本可
  分别存储(同一 `(period_end, ticker)` 可能对应多个 `concept`, 索引不保证
  唯一); 列名不叫 `period_end`/`ticker` 时可用 `period_end_col`/`ticker_col`
  覆盖(默认值就是 `"period_end"`/`"ticker"`)。
  - `to_fundamentals_multiindex(df, *, period_end_col="period_end", ticker_col="ticker")`
  - `save_fundamentals_long(path, df)`
  - `save_fundamentals_multiindex(path, df, *, period_end_col="period_end", ticker_col="ticker")`

所有公开 API 也可直接从 `load` 顶层导入, 例如 `from load import save_prices_long`。

## 快速使用

```python
from load import (
    save_constituents,
    save_prices_long,
    save_prices_multiindex,
    save_fundamentals_long,
    save_fundamentals_multiindex,
)

# df 可以来自任何地方(比如你自己的 sources 包、一次性脚本、别的数据源),
# load 本身不关心来源, 只管按下面的格式存成 parquet。

# 成分股: 长表 [ticker, name]
save_constituents("data/constituents.parquet", constituents_df)

# 行情: 长表 / MultiIndex 两种格式各存一份
save_prices_long("data/prices_long.parquet", prices_df)
save_prices_multiindex("data/prices_by_date_ticker.parquet", prices_df)

# 基本面: 长表 / MultiIndex 两种格式各存一份
save_fundamentals_long("data/fundamentals_long.parquet", fundamentals_df)
save_fundamentals_multiindex("data/fundamentals_by_period_ticker.parquet", fundamentals_df)

# 如果 df 里日期/代码列不叫 date/ticker(比如叫 dt/symbol), 不用现改列名,
# 传参覆盖就行:
save_prices_multiindex(
    "data/prices_by_dt_symbol.parquet",
    prices_df,
    date_col="dt",
    ticker_col="symbol",
)
```

`save_*` 系列只负责落盘, 不会自动抓取; 拿到 `df` 后可以先自行检查/复用, 再
决定存长表还是 MultiIndex 版本(或者两个都存)。

## 开发

```bash
uv sync
uv run ruff check .
uv run pytest -v
```
