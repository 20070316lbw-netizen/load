"""load: 个人量化数据存储包

只负责把已经准备好的数据以 parquet 格式落盘到调用方指定的自定义路径; 不做
任何抓取、不做任何清洗、不做跨来源合并。与 sources 等抓取包是平级关系而非
上下游——不依赖、不 import 任何抓取包, 传入 save_* 的 DataFrame 可以来自
任何地方。prices/fundamentals 各自额外提供一份按 [date/period_end, ticker]
建 MultiIndex 的版本, 长表和 MultiIndex 版本可以分别单独存储。

公开 API:
    write_parquet                  -- 通用 parquet 存储

    save_constituents               -- 存成分股

    to_prices_multiindex            -- 长表 -> [date, ticker] MultiIndex
    save_prices_long                -- 存长表
    save_prices_multiindex          -- 存 MultiIndex 版本

    to_fundamentals_multiindex      -- 长表 -> [period_end, ticker] MultiIndex
    save_fundamentals_long          -- 存长表
    save_fundamentals_multiindex    -- 存 MultiIndex 版本
"""
from __future__ import annotations

from load._parquet import write_parquet
from load.about_constituents import save_constituents
from load.about_fundamentals import (
    save_fundamentals_long,
    save_fundamentals_multiindex,
    to_fundamentals_multiindex,
)
from load.about_prices import (
    save_prices_long,
    save_prices_multiindex,
    to_prices_multiindex,
)

__all__ = [
    "save_constituents",
    "save_fundamentals_long",
    "save_fundamentals_multiindex",
    "save_prices_long",
    "save_prices_multiindex",
    "to_fundamentals_multiindex",
    "to_prices_multiindex",
    "write_parquet",
]


def main() -> None:
    print("Hello from load!")
