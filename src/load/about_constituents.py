"""S&P 500 成分股名单的存储

只负责落盘, 不做任何抓取——成分股 DataFrame 由调用方自行提供(例如来自你
自己的 sources 包, 但 load 本身不依赖、不 import 任何抓取包)。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from load._parquet import write_parquet


def save_constituents(path: str | Path, df: pd.DataFrame) -> Path:
    """把成分股名单存成 parquet。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 待存储的成分股 DataFrame(如 [ticker, name] 两列), 由调用方提供。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(df, path)
