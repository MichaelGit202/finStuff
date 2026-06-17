"""Reusable processing helpers for Alpha Factory notebook cells."""

from typing import Any, Callable, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd


def tree_size(node: Any) -> int:
    if node is None:
        return 0
    if getattr(node, "is_leaf", lambda: True)():
        return 1
    return 1 + tree_size(getattr(node, "left", None)) + tree_size(getattr(node, "right", None))


def evaluate_program(
    program: Any,
    data: pd.DataFrame,
    signal_fn: Callable[[Any, pd.Series], float],
    *,
    price_col: str = "price",
    cost_bps: float = 5.0,
    slippage_bps: float = 2.0,
    complexity_lambda: float = 1e-4,
    initial_value: float = 1000.0,
) -> Dict[str, float]:
    portfolio_value = float(initial_value)
    prev_portfolio = portfolio_value
    prev_price = float(data.iloc[0][price_col]) if len(data) > 0 else 0.0
    prev_row = None

    position = 0.0
    moves = 0
    returns: List[float] = []

    for _, row in data.iterrows():
        price = float(row[price_col])

        if prev_row is None:
            signal = 0.0
        else:
            try:
                signal = float(signal_fn(program, prev_row))
            except Exception:
                signal = 0.0

        signal = max(0.0, min(1.0, signal))
        trade_size = abs(signal - position)
        if trade_size > 1e-12:
            moves += 1

        total_trade_cost_rate = (cost_bps + slippage_bps) / 10000.0
        trade_cost = portfolio_value * trade_size * total_trade_cost_rate

        if prev_price > 0:
            asset_return = (price / prev_price) - 1.0
        else:
            asset_return = 0.0

        step_pnl = portfolio_value * position * asset_return
        portfolio_value += step_pnl
        portfolio_value -= trade_cost

        if portfolio_value <= 0:
            returns.append(-1.0)
            break

        if prev_portfolio > 0:
            r = float(np.log(portfolio_value / prev_portfolio))
        else:
            r = 0.0
        returns.append(r)

        prev_portfolio = portfolio_value
        prev_price = price
        prev_row = row
        position = signal

    returns_arr = np.array(returns, dtype=float)
    if len(returns_arr) == 0:
        raw_fitness = -1.0
    else:
        mean_return = np.mean(returns_arr)
        std_return = np.std(returns_arr) + 1e-12
        sharpe = (mean_return / std_return) * np.sqrt(252)
        equity_curve = np.exp(np.cumsum(returns_arr))
        peak = np.maximum.accumulate(equity_curve)
        max_dd = np.max((peak - equity_curve) / np.maximum(peak, 1e-12))
        total_return = (portfolio_value / initial_value) - 1.0
        raw_fitness = 0.6 * sharpe + 0.3 * total_return - 0.4 * max_dd

    turnover = moves / max(1, len(returns_arr))
    penalty = complexity_lambda * tree_size(program)
    fitness = raw_fitness - penalty - 0.15 * turnover

    return {
        "fitness": float(fitness),
        "raw_fitness": float(raw_fitness),
        "penalty": float(penalty),
        "moves": int(moves),
        "final_value": float(portfolio_value),
        "num_steps": int(len(returns_arr)),
    }


def equity_curve_for_program(
    program: Any,
    data: pd.DataFrame,
    signal_fn: Callable[[Any, pd.Series], float],
    *,
    price_col: str = "price",
    cost_bps: float = 5.0,
    slippage_bps: float = 2.0,
    initial_value: float = 1000.0,
) -> np.ndarray:
    portfolio_value = float(initial_value)
    prev_price = float(data.iloc[0][price_col]) if len(data) > 0 else 0.0
    prev_row = None
    position = 0.0

    curve = [portfolio_value]
    for _, row in data.iterrows():
        price = float(row[price_col])

        if prev_row is None:
            signal = 0.0
        else:
            try:
                signal = float(signal_fn(program, prev_row))
            except Exception:
                signal = 0.0

        signal = max(0.0, min(1.0, signal))

        trade_size = abs(signal - position)
        total_trade_cost_rate = (cost_bps + slippage_bps) / 10000.0
        trade_cost = portfolio_value * trade_size * total_trade_cost_rate

        if prev_price > 0:
            asset_return = (price / prev_price) - 1.0
        else:
            asset_return = 0.0

        step_pnl = portfolio_value * position * asset_return
        portfolio_value = portfolio_value + step_pnl - trade_cost
        portfolio_value = max(portfolio_value, 0.0)

        curve.append(portfolio_value)

        prev_price = price
        prev_row = row
        position = signal

    return np.array(curve, dtype=float)


def max_drawdown_pct(equity_curve: Sequence[float]) -> float:
    curve = np.asarray(equity_curve, dtype=float)
    if len(curve) == 0:
        return float("nan")
    peak = np.maximum.accumulate(curve)
    dd = (peak - curve) / np.maximum(peak, 1e-12)
    return float(np.max(dd) * 100.0)


def split_df_segments(df: pd.DataFrame, n_segments: int) -> List[Tuple[int, pd.DataFrame]]:
    idx_splits = np.array_split(np.arange(len(df)), n_segments)
    segments: List[Tuple[int, pd.DataFrame]] = []
    for i, idxs in enumerate(idx_splits, start=1):
        if len(idxs) == 0:
            continue
        segments.append((i, df.iloc[idxs].copy()))
    return segments


def summarize_segment_results(segment_rows: List[Dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(segment_rows)
