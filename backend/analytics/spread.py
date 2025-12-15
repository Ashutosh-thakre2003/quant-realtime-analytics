import pandas as pd


def compute_spread(
    series_x: pd.Series,
    series_y: pd.Series,
    hedge_ratio: float
) -> pd.Series:
    """
    Spread = X - hedge_ratio * Y
    """
    df = pd.concat([series_x, series_y], axis=1).dropna()

    spread = df.iloc[:, 0] - hedge_ratio * df.iloc[:, 1]
    spread.name = "spread"

    return spread
