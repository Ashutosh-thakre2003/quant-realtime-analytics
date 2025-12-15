import pandas as pd
import statsmodels.api as sm


def compute_hedge_ratio(
    series_x: pd.Series,
    series_y: pd.Series,
    min_samples: int = 30
) -> dict:
    """
    Computes hedge ratio using OLS regression:
    X ~ alpha + beta * Y

    Returns structured result to handle insufficient data safely.
    """
    df = pd.concat([series_x, series_y], axis=1).dropna()

    if len(df) < min_samples:
        return {
            "status": "insufficient_data",
            "n_obs": len(df),
            "min_required": min_samples
        }

    y = df.iloc[:, 0]
    x = df.iloc[:, 1]

    x = sm.add_constant(x)

    model = sm.OLS(y, x).fit()

    # Expecting [const, beta]
    if len(model.params) < 2:
        return {
            "status": "regression_failed",
            "reason": "insufficient variance or rank deficiency",
            "n_obs": len(df)
        }

    return {
        "status": "ok",
        "hedge_ratio": model.params.iloc[1]
    }
