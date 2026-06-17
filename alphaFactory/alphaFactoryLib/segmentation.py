from typing import Dict, List, Sequence, Tuple

import pandas as pd


def split_equal_segments(df: pd.DataFrame, segment_count: int) -> List[pd.DataFrame]:
    if segment_count <= 0:
        raise ValueError("segment_count must be > 0")
    if len(df) == 0:
        return []

    # Use integer boundaries so segment logic stays deterministic across reruns.
    boundaries = [int(i * len(df) / segment_count) for i in range(segment_count + 1)]
    segments = [df.iloc[boundaries[i] : boundaries[i + 1]].copy() for i in range(segment_count)]
    return [seg for seg in segments if len(seg) > 0]


def summarize_segment_equity(equity_curve: Sequence[float]) -> Dict[str, float]:
    if len(equity_curve) == 0:
        return {"start": 0.0, "end": 0.0, "ret_pct": 0.0}

    start = float(equity_curve[0])
    end = float(equity_curve[-1])
    ret_pct = 0.0 if start == 0.0 else ((end / start) - 1.0) * 100.0

    return {"start": start, "end": end, "ret_pct": float(ret_pct)}


#strategy decay/alpha decay
def compute_decay_summary(train_returns: Sequence[float], oos_returns: Sequence[float]) -> Dict[str, float]:
    train_mean = float(sum(train_returns) / len(train_returns)) if train_returns else 0.0
    oos_mean = float(sum(oos_returns) / len(oos_returns)) if oos_returns else 0.0

    return {
        "train_mean_ret_pct": train_mean,
        "oos_mean_ret_pct": oos_mean,
        "segment_decay_pct": float(oos_mean - train_mean),
    }


def make_segment_table(rows: Sequence[Tuple[str, int, float, float]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, columns=["sample", "segment", "start", "end"])
    if len(frame) == 0:
        frame["ret_pct"] = []
        return frame

    frame["ret_pct"] = ((frame["end"] / frame["start"]) - 1.0) * 100.0
    return frame
