"""基本面数据的存储

只负责落盘, 不做任何抓取——长表 DataFrame 由调用方自行提供(例如来自你
自己的 sources 包, 但 load 本身不依赖、不 import 任何抓取包)。这里额外
提供一份按 [period_end, ticker] 建 MultiIndex 的版本(数据本身不变, 只是
换一种索引方式)。注意同一个 (period_end, ticker) 通常对应多个 concept,
因此这个 MultiIndex 不保证唯一, 这里不做透视/聚合, 长表和 MultiIndex 版本
可以分别单独落盘。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from load._parquet import write_parquet


def to_fundamentals_multiindex(
    df: pd.DataFrame,
    *,
    period_end_col: str = "period_end",
    ticker_col: str = "ticker",
) -> pd.DataFrame:
    """把长表重建为按 [period_end_col, ticker_col] 排序的 MultiIndex 版本,
    数据本身不变(只是把这两列从普通列挪成索引)。

    Args:
        df: 长表 DataFrame, 必须包含 period_end_col、ticker_col 两列(默认
            对应 sources.get_fundamentals 长表输出里的 "period_end"/
            "ticker"; 列名不同就用这两个参数覆盖, 不需要提前改列名)。
        period_end_col: 报告期结束日列名, 默认 "period_end"。
        ticker_col: 代码列名, 默认 "ticker"。

    Returns:
        以 [period_end_col, ticker_col] 为 MultiIndex、按索引排序的
        DataFrame, 其余列保持不变。同一 (period_end, ticker) 可能对应多个
        concept, 索引因此不保证唯一(这里不做透视/聚合)。
    """
    return df.set_index([period_end_col, ticker_col]).sort_index()


def save_fundamentals_long(path: str | Path, df: pd.DataFrame) -> Path:
    """把基本面长表存成 parquet, 原样落盘、不做任何转换。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 典型列为 [ticker, concept, period_start,
            period_end, duration_days, numeric_value, fiscal_period,
            fiscal_year](具体列由调用方决定, 这里不做校验)。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(df, path)


def save_fundamentals_multiindex(
    path: str | Path,
    df: pd.DataFrame,
    *,
    period_end_col: str = "period_end",
    ticker_col: str = "ticker",
) -> Path:
    """把基本面长表转成 [period_end_col, ticker_col] MultiIndex 后存成
    parquet。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 必须包含 period_end_col、ticker_col 两列(见
            to_fundamentals_multiindex)。
        period_end_col: 报告期结束日列名, 默认 "period_end"。
        ticker_col: 代码列名, 默认 "ticker"。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(
        to_fundamentals_multiindex(df, period_end_col=period_end_col, ticker_col=ticker_col), path
    )
