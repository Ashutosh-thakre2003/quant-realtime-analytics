import pandas as pd


def compute_zscore(
    spread: pd.Series,
    window: int
) -> pd.Series:
    """
    Rolling Z-score of the spread.
    """
    mean = spread.rolling(window).mean()
    std = spread.rolling(window).std()

    z = (spread - mean) / std
    z.name = "zscore"

    return z
