"""落盘逻辑的单元测试, 全部使用手造的小 DataFrame, 不触发任何网络请求。"""
from __future__ import annotations

import pandas as pd

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


def _sample_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-02", "2024-01-03"]),
            "ticker": ["AAPL", "MSFT", "AAPL"],
            "open": [1.0, 2.0, 1.1],
            "high": [1.5, 2.5, 1.6],
            "low": [0.9, 1.9, 1.0],
            "close": [1.2, 2.2, 1.3],
            "adj_close": [1.2, 2.2, 1.3],
            "volume": [100, 200, 150],
        }
    )


def _sample_fundamentals() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "AAPL"],
            "concept": ["StockholdersEquity", "CommonStockSharesOutstanding"],
            "period_start": pd.to_datetime(["2023-01-01", "2023-01-01"]),
            "period_end": pd.to_datetime(["2023-12-31", "2023-12-31"]),
            "duration_days": [365, 365],
            "numeric_value": [1000.0, 500.0],
            "fiscal_period": ["FY", "FY"],
            "fiscal_year": [2023, 2023],
        }
    )


def test_write_parquet_long_roundtrip(tmp_path):
    df = _sample_prices()
    path = write_parquet(df, tmp_path / "prices.parquet")

    assert path.exists()
    result = pd.read_parquet(path)
    assert isinstance(result.index, pd.RangeIndex)
    pd.testing.assert_frame_equal(result, df)


def test_write_parquet_multiindex_roundtrip(tmp_path):
    df = to_prices_multiindex(_sample_prices())
    path = write_parquet(df, tmp_path / "prices_mi.parquet")

    result = pd.read_parquet(path)
    assert isinstance(result.index, pd.MultiIndex)
    assert result.index.names == ["date", "ticker"]
    pd.testing.assert_frame_equal(result, df)


def test_to_prices_multiindex_preserves_data():
    df = _sample_prices()
    mi = to_prices_multiindex(df)

    assert mi.index.names == ["date", "ticker"]
    assert len(mi) == len(df)
    assert set(mi.columns) == set(df.columns) - {"date", "ticker"}


def test_save_prices_long_and_multiindex(tmp_path):
    df = _sample_prices()

    long_path = save_prices_long(tmp_path / "long.parquet", df)
    mi_path = save_prices_multiindex(tmp_path / "mi.parquet", df)

    pd.testing.assert_frame_equal(pd.read_parquet(long_path), df)
    assert isinstance(pd.read_parquet(mi_path).index, pd.MultiIndex)


def test_to_fundamentals_multiindex_allows_duplicate_index():
    df = _sample_fundamentals()
    mi = to_fundamentals_multiindex(df)

    assert mi.index.names == ["period_end", "ticker"]
    # 同一 (period_end, ticker) 对应两条不同 concept 的记录, 索引允许重复
    assert mi.index.duplicated().any()


def test_save_fundamentals_long_and_multiindex(tmp_path):
    df = _sample_fundamentals()

    long_path = save_fundamentals_long(tmp_path / "fund_long.parquet", df)
    mi_path = save_fundamentals_multiindex(tmp_path / "fund_mi.parquet", df)

    pd.testing.assert_frame_equal(pd.read_parquet(long_path), df)
    assert isinstance(pd.read_parquet(mi_path).index, pd.MultiIndex)


def test_to_prices_multiindex_custom_columns():
    df = _sample_prices().rename(columns={"date": "dt", "ticker": "symbol"})
    mi = to_prices_multiindex(df, date_col="dt", ticker_col="symbol")

    assert mi.index.names == ["dt", "symbol"]
    assert len(mi) == len(df)


def test_to_fundamentals_multiindex_custom_columns():
    df = _sample_fundamentals().rename(columns={"period_end": "asof", "ticker": "symbol"})
    mi = to_fundamentals_multiindex(df, period_end_col="asof", ticker_col="symbol")

    assert mi.index.names == ["asof", "symbol"]
    assert len(mi) == len(df)


def test_save_constituents(tmp_path):
    df = pd.DataFrame({"ticker": ["AAPL", "MSFT"], "name": ["Apple Inc.", "Microsoft Corp."]})
    path = save_constituents(tmp_path / "constituents.parquet", df)

    pd.testing.assert_frame_equal(pd.read_parquet(path), df)
