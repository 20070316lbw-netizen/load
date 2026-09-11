"""通用函数结果缓存: 给任意返回 DataFrame 的函数包一层 parquet 缓存。

不特定于任何抓取包——不 import sources 或任何其他抓取库, 只认"一个返回
DataFrame 的可调用对象 + 一个由调用方指定的缓存文件路径", 与 load 里其余
模块"不依赖任何抓取包"的原则保持一致。典型用法是直接传 sources 里的函数:

    from load import cached_call
    from sources import get_prices

    prices = cached_call(
        get_prices, "data/cache/prices.parquet",
        ["AAPL", "MSFT"], start="2020-01-01", end="2024-01-01",
    )

但 fetch_fn 可以是任何返回 DataFrame 的可调用对象, load 不关心它具体来自
哪里。缓存文件本身仍然通过 write_parquet/read_parquet 落盘/读取, 跟其余
模块用的是同一套存储逻辑。
"""
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd

from load._parquet import read_parquet, write_parquet

logger = logging.getLogger(__name__)


def cached_call(
    fetch_fn: Callable[..., pd.DataFrame],
    path: str | Path,
    *args: Any,
    ttl: float | None = None,
    force_refresh: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """缓存命中则直接读盘返回, 否则调用 fetch_fn(*args, **kwargs) 落盘后返回。

    "命中"的定义: path 处的文件存在, 且 (ttl 为 None, 或文件 mtime 距今
    不超过 ttl 秒)。ttl=None 表示"只要文件存在就一直有效", 适合成分股/
    交易所归属这类静态快照, 或者调用方自己确定不会再变的历史区间数据;
    传一个具体秒数则按时间失效, 适合会随时间推移变化的抓取(比如包含
    "今天"的行情、还在更新的无风险利率序列)。

    单个标的/参数抓取失败时是否重试、是否跳过, 是 fetch_fn 自己的事——
    这里不做任何异常处理, fetch_fn 抛出的异常原样往外抛, 缓存文件也不会
    被写入或覆盖。

    Args:
        fetch_fn: 缓存未命中时用于实际抓取的可调用对象, 返回 DataFrame,
            不限来源(常见用法是直接传 sources.get_prices 之类的函数, 但
            load 本身不 import 也不关心它具体是什么)。
        path: 缓存文件路径, 由调用方指定; 父目录不存在时会自动创建。
        *args: 缓存未命中时透传给 fetch_fn 的位置参数。
        ttl: 缓存有效期, 单位秒。None(默认)表示永不过期, 直到调用方手动
            删除文件、或传 force_refresh=True。
        force_refresh: True 时无视现有缓存, 强制重新抓取并覆盖旧文件。
        **kwargs: 缓存未命中时透传给 fetch_fn 的关键字参数。

    Returns:
        缓存命中时是从 path 读出的 DataFrame; 否则是 fetch_fn 的返回值
        (已经落盘到 path)。
    """
    path = Path(path)

    if not force_refresh and path.exists():
        age = _age_seconds(path)
        if ttl is None or age <= ttl:
            logger.debug(f"cache hit: {path} (age={age:.0f}s, ttl={ttl})")
            return read_parquet(path)
        logger.debug(f"cache expired: {path} (age={age:.0f}s > ttl={ttl}s)")

    df = fetch_fn(*args, **kwargs)
    write_parquet(df, path)
    return df


def invalidate(path: str | Path) -> bool:
    """删除 path 处的缓存文件(如果存在)。

    是 force_refresh=True 的另一种触发方式: 想要"下次调用时重新抓"而不是
    "现在立刻重新抓"就用这个, 比如在别的脚本里根据某个条件预先清缓存。

    Args:
        path: 待删除的缓存文件路径。

    Returns:
        True 表示文件存在且已删除, False 表示文件本来就不存在。
    """
    path = Path(path)
    if path.exists():
        path.unlink()
        return True
    return False


def _age_seconds(path: Path) -> float:
    return time.time() - path.stat().st_mtime
