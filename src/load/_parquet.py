"""通用 parquet 存储工具

仅负责"给定 DataFrame + 目标路径, 写成/读出 parquet 文件"这两件事; 不做
任何数据清洗或格式转换, 那些留给各个 about_*.py 模块自己处理。
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


def read_parquet(path: str | Path) -> pd.DataFrame:
    """从 parquet 文件读出 DataFrame, 是 write_parquet 的对应读取入口。

    索引怎么读出来完全由文件里实际存了什么决定: write_parquet 写入时带了
    索引(具名索引或 MultiIndex)的话, 这里原样恢复; 普通 RangeIndex 长表
    读出来同样是 RangeIndex, 不做额外转换。

    Args:
        path: 待读取的 parquet 文件路径。

    Returns:
        读出的 DataFrame。

    Raises:
        FileNotFoundError: path 不存在。
    """
    return pd.read_parquet(Path(path), engine="pyarrow") # type: ignore
