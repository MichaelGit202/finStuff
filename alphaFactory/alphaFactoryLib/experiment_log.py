# fine

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def append_experiment_log(
    log_df: Optional[pd.DataFrame],
    *,
    run_label: str,
    selected_expression: str,
    train_stats: Dict[str, Any],
    test_stats: Dict[str, Any],
    oos_stats: Dict[str, Any],
    best_generation: Optional[int] = None,
    best_robust_score: Optional[float] = None,
) -> pd.DataFrame:
    row = {
        "timestamp_utc": utc_timestamp(),
        "run_label": run_label,
        "selected_expression": selected_expression,
        "best_generation": best_generation,
        "best_robust_score": best_robust_score,
        "train_fitness": float(train_stats.get("fitness", 0.0)),
        "train_final_value": float(train_stats.get("final_value", 0.0)),
        "test_fitness": float(test_stats.get("fitness", 0.0)),
        "test_final_value": float(test_stats.get("final_value", 0.0)),
        "oos_fitness": float(oos_stats.get("fitness", 0.0)),
        "oos_final_value": float(oos_stats.get("final_value", 0.0)),
    }

    if log_df is None or len(log_df) == 0:
        return pd.DataFrame([row])

    return pd.concat([log_df, pd.DataFrame([row])], ignore_index=True)


def to_records(log_df: pd.DataFrame) -> List[Dict[str, Any]]:
    if len(log_df) == 0:
        return []
    return log_df.to_dict(orient="records")
