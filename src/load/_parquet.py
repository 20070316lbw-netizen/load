"""通用 parquet 存储工具

仅负责"给定 DataFrame + 目标路径, 写成 parquet 文件"这一件事; 不做任何
数据清洗或格式转换, 那些留给各个 about_*.py 模块自己处理。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_parquet(df: pd.DataFrame, path: str | Path) -> Path:
    """把 df 写成 parquet 文件, 返回写入的路径。

    路径(含文件名)完全由调用方指定, 本函数不负责命名。若 df 的索引是
    具名索引或 MultiIndex(例如按 [date, ticker] 建索引), 索引会随数据一起
    写入; 普通 RangeIndex 的长表则不写索引, 避免产生无意义的列。

    Args:
        df: 待存储的 DataFrame, 应已是调用方期望的最终形态。
        path: 目标文件路径(自定义名称), 父目录不存在时会自动创建。

    Returns:
        实际写入的文件路径(即传入的 path, 转成 Path)。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    write_index = isinstance(df.index, pd.MultiIndex) or df.index.name is not None
    df.to_parquet(path, engine="pyarrow", index=write_index)

    return path
