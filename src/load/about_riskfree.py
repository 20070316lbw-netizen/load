"""无风险利率数据的存储

只负责落盘, 不做任何抓取——长表 DataFrame 由调用方自行提供(例如来自你
自己的 sources 包, 但 load 本身不依赖、不 import 任何抓取包)。这里额外
提供一份按 [date, series] 建 MultiIndex 的版本(数据本身不变, 只是换一种
索引方式), 长表和 MultiIndex 版本可以分别单独落盘。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from load._parquet import write_parquet


def to_riskfree_multiindex(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    series_col: str = "series",
) -> pd.DataFrame:
    """把长表重建为按 [date_col, series_col] 排序的 MultiIndex 版本, 数据
    本身不变(只是把这两列从普通列挪成索引)。

    Args:
        df: 长表 DataFrame, 必须包含 date_col、series_col 两列(默认对应
            sources.get_risk_free_rate 长表输出里的 "date"/"series"; 列名
            不同就用这两个参数覆盖, 不需要提前改列名)。
        date_col: 日期列名, 默认 "date"。
        series_col: FRED series id 列名, 默认 "series"。

    Returns:
        以 [date_col, series_col] 为 MultiIndex、按索引排序的 DataFrame,
        其余列保持不变。
    """
    return df.set_index([date_col, series_col]).sort_index()


def save_riskfree_long(path: str | Path, df: pd.DataFrame) -> Path:
    """把无风险利率长表存成 parquet, 原样落盘、不做任何转换。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 典型列为 [date, series, value](具体列由调用方
            决定, 这里不做校验)。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(df, path)


def save_riskfree_multiindex(
    path: str | Path,
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    series_col: str = "series",
) -> Path:
    """把无风险利率长表转成 [date_col, series_col] MultiIndex 后存成
    parquet。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 必须包含 date_col、series_col 两列(见
            to_riskfree_multiindex)。
        date_col: 日期列名, 默认 "date"。
        series_col: FRED series id 列名, 默认 "series"。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(
        to_riskfree_multiindex(df, date_col=date_col, series_col=series_col), path
    )
