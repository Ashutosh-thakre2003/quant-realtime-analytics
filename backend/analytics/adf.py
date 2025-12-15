from statsmodels.tsa.stattools import adfuller
import pandas as pd


def compute_adf(spread: pd.Series, min_samples: int = 50) -> dict:
    """
    Augmented Dickey-Fuller test on spread.
    Runs only if sufficient data is available.
    """
    spread = spread.dropna()

    if len(spread) < min_samples:
        return {
            "status": "insufficient_data",
            "n_obs": len(spread),
            "min_required": min_samples
        }

    result = adfuller(spread, regression="c")

    return {
        "status": "ok",
        "adf_stat": result[0],
        "p_value": result[1],
        "used_lag": result[2],
        "n_obs": result[3],
        "critical_values": result[4]
    }
