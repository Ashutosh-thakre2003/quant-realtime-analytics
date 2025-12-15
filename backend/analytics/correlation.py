import pandas as pd


def compute_rolling_correlation(
    series_x: pd.Series,
    series_y: pd.Series,
    window: int
) -> pd.Series:
    """
    Rolling correlation between two series.
    """
    df = pd.concat([series_x, series_y], axis=1).dropna()
    corr = df.iloc[:, 0].rolling(window).corr(df.iloc[:, 1])
    corr.name = "rolling_corr"

    return corr
