"""Alpha Factory library package.

This package is designed for incremental migration from the notebook.
The notebook can import selected helpers without removing existing cells.
"""

from .constants import (
    BACKTEST_COST_BPS,
    BACKTEST_SLIPPAGE_BPS,
    DATA_WINDOW_LENGTH,
    DEFAULT_OPERATORS,
    DEFAULT_COMPLEXITY_LAMBDA,
    DEFAULT_HARD_GATES,
    DEFAULT_OOS_PROXY_FRACTION,
    DEFAULT_ROBUST_WEIGHTS,
    DEFAULT_SEGMENT_COUNT,
)
from .robustness import HardGates, RobustWeights, run_robust_evolution, score_robust_candidate
from .segmentation import compute_decay_summary, split_equal_segments
from .experiment_log import append_experiment_log
from .processing_handlers import (
    evaluate_program,
    equity_curve_for_program,
    max_drawdown_pct,
    split_df_segments,
    summarize_segment_results,
    tree_size,
)
from .preprocessing import (
    PreparedDataset,
    load_numeric_frame,
    normalize_external_frame,
    prepare_dataset_from_csv,
    prepare_train_test_frame,
)
from .semantic_tree import build_tree, crossover, generate_random_tree, mutate, node, tournament_selection
from .signals import program_sigmoid_framework, sigmoid, sigmoid_framework, simple_framework, simple_signal_evaluator

__all__ = [
    "BACKTEST_COST_BPS",
    "BACKTEST_SLIPPAGE_BPS",
    "DATA_WINDOW_LENGTH",
    "DEFAULT_OPERATORS",
    "DEFAULT_COMPLEXITY_LAMBDA",
    "DEFAULT_HARD_GATES",
    "DEFAULT_OOS_PROXY_FRACTION",
    "DEFAULT_ROBUST_WEIGHTS",
    "DEFAULT_SEGMENT_COUNT",
    "HardGates",
    "RobustWeights",
    "run_robust_evolution",
    "score_robust_candidate",
    "split_equal_segments",
    "compute_decay_summary",
    "append_experiment_log",
    "evaluate_program",
    "equity_curve_for_program",
    "max_drawdown_pct",
    "split_df_segments",
    "summarize_segment_results",
    "tree_size",
    "PreparedDataset",
    "load_numeric_frame",
    "normalize_external_frame",
    "prepare_dataset_from_csv",
    "prepare_train_test_frame",
    "node",
    "build_tree",
    "generate_random_tree",
    "tournament_selection",
    "crossover",
    "mutate",
    "sigmoid",
    "sigmoid_framework",
    "program_sigmoid_framework",
    "simple_framework",
    "simple_signal_evaluator",
]
