"""因子数据的存储

只负责落盘, 不做任何因子计算——因子函数(比如 momfactor 这样的因子包)在
[date, ticker] MultiIndex 价格表上跑 groupby(level="ticker").transform(...),
产出一个同样以 [date, ticker] 为 MultiIndex 的 pd.Series; to_factors_long
负责把这样一个 Series 转成 tidy long 格式 [date, ticker, factor, value]
(factor 列存因子名, 比如 "mom_12_1", 参数编码在这个字符串里, 不额外拆
列), 这是所有因子包共用的落盘格式——load 本身不依赖、不 import 任何因子
包。这里额外提供一份按 [date, ticker] 建 MultiIndex 的版本(数据本身不
变, 只是换一种索引方式)。注意同一个 (date, ticker) 通常对应多个 factor
(不同因子在同一天同一只票各有一行), 因此这个 MultiIndex 不保证唯一, 长
表和 MultiIndex 版本可以分别单独落盘。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from load._parquet import write_parquet


def to_factors_long(
    s: pd.Series,
    factor: str,
    *,
    date_col: str = "date",
    ticker_col: str = "ticker",
    value_col: str = "value",
) -> pd.DataFrame:
    """把因子函数算出来的 [date, ticker] MultiIndex Series 转成 tidy long
    格式, 数据本身不变(只是换一种形状), 不做任何计算或清洗。

    Args:
        s: 因子值, 索引必须是两层 MultiIndex(通常来自某个因子包对
            [date, ticker] MultiIndex 价格表做 groupby(level="ticker")
            .transform(...) 的结果), 第一层对应日期、第二层对应代码,
            索引本身叫什么名字不重要, 按位置取。
        factor: 因子名, 会整个填进输出的 factor 列, 比如 "mom_12_1"。
        date_col: 输出的日期列名, 默认 "date"。
        ticker_col: 输出的代码列名, 默认 "ticker"。
        value_col: 输出的因子值列名, 默认 "value"。

    Returns:
        长表 DataFrame, 列为 [date_col, ticker_col, "factor", value_col]。

    Raises:
        ValueError: s 的索引不是两层的 MultiIndex。
    """
    if not isinstance(s.index, pd.MultiIndex) or s.index.nlevels != 2:
        raise ValueError("s 的索引必须是两层 MultiIndex(如 [date, ticker])")

    df = s.rename(value_col).reset_index()
    df = df.rename(columns={df.columns[0]: date_col, df.columns[1]: ticker_col})
    df["factor"] = factor
    return df[[date_col, ticker_col, "factor", value_col]]


def to_factors_multiindex(
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    ticker_col: str = "ticker",
) -> pd.DataFrame:
    """把因子长表重建为按 [date_col, ticker_col] 排序的 MultiIndex 版本,
    数据本身不变(只是把这两列从普通列挪成索引)。

    Args:
        df: 长表 DataFrame, 必须包含 date_col、ticker_col 两列(默认对应
            to_factors_long 的输出; 列名不同就用这两个参数覆盖)。
        date_col: 日期列名, 默认 "date"。
        ticker_col: 代码列名, 默认 "ticker"。

    Returns:
        以 [date_col, ticker_col] 为 MultiIndex、按索引排序的 DataFrame,
        其余列(factor、value 等)保持不变。同一 (date, ticker) 可能对应
        多个 factor, 索引因此不保证唯一(这里不做透视/聚合)。
    """
    return df.set_index([date_col, ticker_col]).sort_index()


def save_factors_long(path: str | Path, df: pd.DataFrame) -> Path:
    """把因子长表存成 parquet, 原样落盘、不做任何转换。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 典型列为 [date, ticker, factor, value](具体
            列由调用方决定, 这里不做校验; 一般来自 to_factors_long)。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(df, path)


def save_factors_multiindex(
    path: str | Path,
    df: pd.DataFrame,
    *,
    date_col: str = "date",
    ticker_col: str = "ticker",
) -> Path:
    """把因子长表转成 [date_col, ticker_col] MultiIndex 后存成 parquet。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 长表 DataFrame, 必须包含 date_col、ticker_col 两列(见
            to_factors_multiindex)。
        date_col: 日期列名, 默认 "date"。
        ticker_col: 代码列名, 默认 "ticker"。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(to_factors_multiindex(df, date_col=date_col, ticker_col=ticker_col), path)
