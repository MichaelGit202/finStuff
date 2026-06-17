# good

import math
from typing import Any


def sigmoid(x: float, scale: float = 1.0) -> float:
    if scale <= 0:
        raise ValueError("scale must be > 0")
    z = max(-60.0, min(60.0, x / scale))
    return 1.0 / (1.0 + math.exp(-z))


def sigmoid_framework(raw_signal: float, *, scale: float = 1.0, deadband: float = 0.0) -> float:
    centered = (sigmoid(raw_signal, scale=scale) * 2.0) - 1.0
    if abs(centered) < deadband:
        return 0.0
    return float(max(-1.0, min(1.0, centered)))


def simple_framework(program: Any, data: Any) -> float:
    result = float(program.calculate(data))
    if result > 0:
        return 1.0
    if result < 0:
        return -1.0
    return 0.0


def program_sigmoid_framework(
    program: Any,
    data: Any,
    *,
    scale: float = 25.0,
    deadband_low: float = 0.45,
    deadband_high: float = 0.55,
) -> float:
    try:
        result = float(program.calculate(data))
    except Exception:
        return 0.0

    result = result / scale
    if result > 10:
        sigmoid_result = 1.0
    elif result < -10:
        sigmoid_result = 0.0
    else:
        sigmoid_result = 1.0 / (1.0 + math.exp(-result))

    if deadband_low <= sigmoid_result <= deadband_high:
        return 0.5
    return float(sigmoid_result)


def simple_signal_evaluator(signal: float) -> int:
    return 1 if signal == 1 else 0
