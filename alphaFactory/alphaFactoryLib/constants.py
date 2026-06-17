# good

from .robustness import HardGates, RobustWeights


BACKTEST_COST_BPS = 5
BACKTEST_SLIPPAGE_BPS = 2
DEFAULT_COMPLEXITY_LAMBDA = 0.02
DATA_WINDOW_LENGTH = 200
DEFAULT_OPERATORS = ["+", "-", "*", "/"]

DEFAULT_SEGMENT_COUNT = 12
DEFAULT_OOS_PROXY_FRACTION = 1.0 / 12.0

DEFAULT_ROBUST_WEIGHTS = RobustWeights(
	train=0.35,
	validation=0.45,
	oos_proxy_a=0.10,
	oos_proxy_b=0.10,
)

DEFAULT_HARD_GATES = HardGates(
	min_final_value=1000.0,
	max_turnover_ratio=0.65,
	min_validation_fitness=0.01,
	min_oos_proxy_final_value=1000.0,
	max_train_validation_gap=0.12,
	max_validation_oos_gap=0.12,
)
