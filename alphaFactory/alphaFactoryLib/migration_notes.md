# AlphaFactory Notebook-to-Library Migration Notes

This folder now includes migration-safe helpers that match notebook behavior:

- `robustness.py`: robust score weighting, turnover ratios, hard-gate evaluation.
- `segmentation.py`: equal-size data segmentation and alpha-decay summary helpers.
- `experiment_log.py`: append-only experiment log helpers with UTC timestamps.

## Why this is safe

- Existing notebook cells can remain unchanged.
- You can import one helper at a time and compare outputs.
- No notebook code needs to be deleted during migration.

## Suggested import order in notebook

1. `score_robust_candidate` from `robustness.py`
2. `split_equal_segments` / `compute_decay_summary` from `segmentation.py`
3. `append_experiment_log` from `experiment_log.py`

## Next migration steps

1. Add GP tree/operator module wrappers with notebook-parity signatures.
2. Move evaluator/backtest into library and verify portfolio accounting parity.
3. Move robust-evolution loop into reusable function while preserving notebook display output.
