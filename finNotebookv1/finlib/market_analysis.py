import numpy as np
import math

# These functions need to be reworked or somehow worked into the sim because what this is expecting is a 
# pandas like dataframe or series to calculate the returns but rn the sim is using lists

def log_returns_10(returns):
    """Calculate log returns from a series of prices using base 10."""
    return np.log10(returns / returns.shift(1)).dropna()    

def log_returns_e(returns):
    """Calculate log returns from a series of prices using natural base e."""
    return np.log(returns / returns.shift(1)).dropna()

def calc_log_returns(returns, base='e'):
    """ just applying log to the already calculated return"""
    sign = 1 if returns > 0 else -1
    returns = abs(returns)

    if base == 'e':
        return sign * math.log(returns)
    elif base == '10':
        return sign * math.log(returns, 10)
    else:
        raise ValueError("Base must be 'e' or '10'.")


def drawdown(returns):
    """Calculate the drawdown from a series of returns."""
    cumulative_returns = (1 + returns).cumprod()
    peak = cumulative_returns.cummax()
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.dropna()


def sharpe_ratio(Ra, Rb, SIGa):
    """ reward-to-variability-ratio Ra: return of asset, Rb: Risk-free rate, SIGa: standard deviation of asset's returns """
    if SIGa == 0:
        return np.inf  # Avoid division by zero; infinite Sharpe Ratio if no volatility
    return (Ra - Rb) / SIGa