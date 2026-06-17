# Alpha Factory GP Work Summary

## Executive Summary
- Built a full GP alpha-search pipeline for JPM with expression trees over 10 technical indicators and a signal-to-position framework.
- Fixed a key evaluator bug so PnL and transaction costs are both computed consistently on portfolio-fraction exposure.
- Replaced fragile fitness logic with a risk-aware objective and added penalties for complexity and turnover.
- Added anti-overfit controls: validation split, patience-based early stopping, robust ranking, and hard gates.
- Expanded robustness ranking to include two OOS proxy windows and deduplicated Hall-of-Fame formulas.
- Added segment-level diagnostics (train vs OOS equity curves) to inspect regime sensitivity and alpha decay timing.
- Added a persistent run log so each experiment appends comparable metrics and selected formula output.
- Latest run remains profitable in train/test and positive in OOS final value, but OOS risk-adjusted fitness is slightly negative and segment returns show meaningful decay vs train.

## Scope
This summary documents, in sequence, what was changed in the JPM genetic-programming workflow, why each change was made, and what the latest results show.

## Sequential Changes And Rationale
1. Baseline GP and indicator pipeline was established.
- What was done: Built expression-tree GP over technical indicators (SMA, ADX, RSI, stochastic oscillator, ATR, Bollinger width, OBV, CMF, z-score, Donchian position), with crossover/mutation/tournament selection.
- Why: Create an end-to-end search process for alpha formulas and position sizing.

2. Signal shaping was hardened.
- What was done: Increased sigmoid scaling and added deadband around neutral signal.
- Why: Reduce noisy mid-range signal oscillation and overtrading from tiny output changes.

3. Fitness objective was redesigned.
- What was done: Replaced weak expectancy-style objective with Sharpe/return/drawdown blend, then subtracted complexity and turnover penalties.
- Why: Old objective had tiny magnitude and encouraged premature convergence/penalty dominance.

4. Diversity pressure was improved.
- What was done: Increased mutation rate, reduced tournament pressure, added immigrant injection, randomized tree depth in initialization/immigration.
- Why: Prevent early population collapse and improve exploration.

5. Complexity penalty usage was made consistent.
- What was done: Centralized complexity lambda use in evaluation-only paths.
- Why: Ensure objective consistency and avoid function-signature errors in tree builders/mutation.

6. Out-of-sample quick ranking was added.
- What was done: Added a cell to evaluate top train-ranked programs on 2021 OOS data with train-derived normalization.
- Why: Fast sanity check for generalization and immediate overfit detection.

7. Train/OOS segment alpha-decay analysis was added.
- What was done: Split train and OOS into equal segments, evaluated top programs by segment, and computed immediate regime gap plus average decay.
- Why: Identify whether failure is instant on regime change or gradual over time.

8. Critical PnL accounting bug was fixed.
- What was done: Updated evaluator PnL from raw price-delta style to portfolio-fraction return accounting (`portfolio * position * return`) while keeping trade costs portfolio-consistent.
- Why: Previous mismatch could bias outcomes and make strategies appear systematically worse.

9. Validation-aware early stopping was introduced.
- What was done: Split train into inner-train/validation, selected via blended score, used patience-based early stop.
- Why: Reduce overcooking and choose programs with better expected robustness.

10. Robust gating and anti-churn selection were introduced.
- What was done: Added hard gates for profitability and turnover, Hall-of-Fame ranking by robust score, and dedup by expression.
- Why: Prevent selecting unstable/high-churn formulas that only look good in-sample.

11. Robust objective was expanded to two OOS proxy windows.
- What was done: Included both first and second OOS proxy segments in selection score.
- Why: Reduce single-window luck and improve regime-transition resilience.

12. Segment equity diagnostics were added.
- What was done: Added per-segment equity-curve cell for train and OOS 2021.
- Why: Visualize where decay occurs, not just aggregate stats.

13. Persistent experiment logging was added.
- What was done: Added run-log cell that appends timestamped run metrics and selected program expression.
- Why: Make experiment comparisons reproducible across reruns.

## Detailed Explanation: What The Robustness Score Is
The robustness score in this project is a custom model-selection score. It is a real and standard idea in quant research to use a composite "robustness" objective, but there is no single universal formula used by everyone. This implementation is tailored to this pipeline.

### Core idea
Instead of selecting formulas only by in-sample train fitness, the pipeline ranks formulas by a blend of:

1. Inner-train fitness
2. Validation fitness
3. OOS proxy A fitness (early OOS slice)
4. OOS proxy B fitness (next OOS slice)
5. Turnover penalty
6. Hard-gate pass/fail adjustment

This pushes selection toward formulas that survive regime transition and avoid overtrading.

### Formula used
Let:

- f_train = inner-train fitness
- f_val = validation fitness
- f_oos_a = OOS proxy A fitness
- f_oos_b = OOS proxy B fitness
- t_train, t_val, t_oos_a, t_oos_b = turnover ratios for each slice

Base blend:

base_score = w_train*f_train + w_val*f_val + w_oos_a*f_oos_a + w_oos_b*f_oos_b

Turnover penalty:

turn_penalty = lambda_turn*(t_train + t_val + t_oos_a + t_oos_b)

Gate-adjusted robust score:

- if gates pass: robust_score = base_score - turn_penalty
- if gates fail: robust_score = base_score - turn_penalty + failed_gate_penalty

In current settings, failed_gate_penalty is strongly negative (demotion behavior), so non-robust formulas are ranked near the bottom.

### Current default weights and controls
From the current library defaults:

- w_train = 0.35
- w_val = 0.45
- w_oos_a = 0.10
- w_oos_b = 0.10
- lambda_turn = 0.08
- failed_gate_penalty = -10.0

This places the largest emphasis on validation stability, then train quality, with additional pressure from early OOS behavior.

### Hard gates (must pass)
A formula must satisfy all of the following to avoid demotion:

1. Train final value >= minimum final value threshold
2. Validation final value >= minimum final value threshold
3. Validation fitness > minimum validation fitness threshold
4. Turnover ratio <= max turnover ratio on train, validation, OOS proxy A, and OOS proxy B

Intuition:

- Profitability gates prevent selecting formulas that "win" only by noisy objective artifacts.
- Validation gate reduces overfit carry-through.
- Turnover gates prevent churn-heavy formulas that are fragile after costs/slippage.

### Why this is useful
If you pick only by train fitness, GP tends to overfit and produce brittle formulas. This robust score is a practical ranking layer to trade off:

- return quality
- generalization
- regime-transition durability
- operational realism (turnover)

### How to interpret robust score in practice
The absolute value is less important than relative ranking under the same configuration.

1. Compare formulas within the same run and same settings.
2. Track whether top robust formulas also keep acceptable OOS segment behavior.
3. If robust score is high but OOS decays fast, rebalance weights/gates rather than optimizing train objective harder.

### Important caveat
Because this is a custom score, changing weights, penalties, or gate thresholds changes the meaning of the number. Treat it as a selection criterion tied to configuration, not an absolute cross-project metric.

## Latest Results Snapshot (Current Notebook State)
Source: latest executed robust cell + segment equity cell + experiment log.

1. Selected robust program (latest run)
- `(((bollinger_band_width - (RSI / stochastic_oscillator)) - ((stochastic_oscillator - SMA) + ((stochastic_oscillator * SMA) * SMA))) * (((ADX * RSI) + (bollinger_band_width * stochastic_oscillator)) + ((z_score - RSI) - (ADX / donchian_channel_position))))`

2. Robust run metrics
- Best robust generation: `12`
- Best robust score: `0.766179`

3. Portfolio outcomes
- Train: fitness `0.752096`, final value `2667.87`
- Test: fitness `0.532692`, final value `1635.63`
- OOS 2021: fitness `-0.042358`, final value `1266.45`

4. Segment-decay diagnostics
- Mean train segment return: `9.448%`
- Mean OOS 2021 segment return: `2.042%`
- Segment decay (OOS - train): `-7.406%`

5. Experiment log status
- Logged runs currently in notebook memory: `2`

## Interpretation
- The pipeline is now materially more robust than baseline and no longer purely in-sample.
- Test remains positive and strong in the latest run.
- OOS still profits in absolute dollars, but risk-adjusted OOS fitness is slightly negative and segment returns show clear decay vs train.
- Next tuning should focus on reducing OOS churn and narrowing train-to-OOS decay rather than maximizing train return.
