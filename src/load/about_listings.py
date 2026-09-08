"""交易所归属信息(ticker -> exchange)的存储

只负责落盘, 不做任何抓取——DataFrame 由调用方自行提供(例如来自你自己的
sources 包, 但 load 本身不依赖、不 import 任何抓取包)。跟成分股一样是
静态快照而非时间序列, 不区分长表/MultiIndex。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from load._parquet import write_parquet


def save_listings(path: str | Path, df: pd.DataFrame) -> Path:
    """把交易所归属信息存成 parquet。

    Args:
        path: 目标文件路径(自定义名称)。
        df: 待存储的交易所归属 DataFrame(如 [ticker, cik, name, exchange]
            四列), 由调用方提供。

    Returns:
        实际写入的文件路径。
    """
    return write_parquet(df, path)
