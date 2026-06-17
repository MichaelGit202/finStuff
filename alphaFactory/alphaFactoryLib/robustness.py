# fine for everything except run_robust_evolution, holy crap
# 

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RobustWeights:
    train: float = 0.35
    validation: float = 0.45
    oos_proxy_a: float = 0.10
    oos_proxy_b: float = 0.10


@dataclass(frozen=True)
class HardGates:
    min_final_value: float = 1000.0
    max_turnover_ratio: float = 0.65
    min_validation_fitness: float = 0.0
    min_oos_proxy_final_value: float = 1000.0
    max_train_validation_gap: float = 0.20
    max_validation_oos_gap: float = 0.20


def turnover_ratio(stats: Dict[str, float]) -> float:
    return float(stats.get("moves", 0.0)) / max(1.0, float(stats.get("num_steps", 1.0)))


def hard_gate_fail_reasons(
    train_stats: Dict[str, float],
    val_stats: Dict[str, float],
    oos_a_stats: Dict[str, float],
    oos_b_stats: Dict[str, float],
    gates: HardGates,
) -> Dict[str, bool]:
    ratios = [
        turnover_ratio(train_stats),
        turnover_ratio(val_stats),
        turnover_ratio(oos_a_stats),
        turnover_ratio(oos_b_stats),
    ]

    train_fit = float(train_stats.get("fitness", -1e9))
    val_fit = float(val_stats.get("fitness", -1e9))
    oos_a_fit = float(oos_a_stats.get("fitness", -1e9))
    oos_b_fit = float(oos_b_stats.get("fitness", -1e9))

    train_val_gap = max(0.0, train_fit - val_fit)
    val_oos_gap = max(0.0, val_fit - min(oos_a_fit, oos_b_fit))

    return {
        "min_train_final_value": float(train_stats.get("final_value", 0.0)) < gates.min_final_value,
        "min_validation_final_value": float(val_stats.get("final_value", 0.0)) < gates.min_final_value,
        "min_oos_proxy_a_final_value": float(oos_a_stats.get("final_value", 0.0)) < gates.min_oos_proxy_final_value,
        "min_oos_proxy_b_final_value": float(oos_b_stats.get("final_value", 0.0)) < gates.min_oos_proxy_final_value,
        "min_validation_fitness": float(val_stats.get("fitness", -1e9)) <= gates.min_validation_fitness,
        "max_train_validation_gap": train_val_gap > gates.max_train_validation_gap,
        "max_validation_oos_gap": val_oos_gap > gates.max_validation_oos_gap,
        "max_turnover_ratio_train": ratios[0] > gates.max_turnover_ratio,
        "max_turnover_ratio_validation": ratios[1] > gates.max_turnover_ratio,
        "max_turnover_ratio_oos_proxy_a": ratios[2] > gates.max_turnover_ratio,
        "max_turnover_ratio_oos_proxy_b": ratios[3] > gates.max_turnover_ratio,
    }


def passes_hard_gates(
    train_stats: Dict[str, float],
    val_stats: Dict[str, float],
    oos_a_stats: Dict[str, float],
    oos_b_stats: Dict[str, float],
    gates: HardGates,
) -> bool:
    reasons = hard_gate_fail_reasons(train_stats, val_stats, oos_a_stats, oos_b_stats, gates)
    return not any(reasons.values())


def score_robust_candidate(
    train_stats: Dict[str, float],
    val_stats: Dict[str, float],
    oos_a_stats: Dict[str, float],
    oos_b_stats: Dict[str, float],
    *,
    weights: RobustWeights,
    gates: HardGates,
    extra_turnover_penalty: float = 0.08,
    failed_gate_penalty: float = -10.0,
) -> Dict[str, float]:
    train_turn = turnover_ratio(train_stats)
    val_turn = turnover_ratio(val_stats)
    oos_a_turn = turnover_ratio(oos_a_stats)
    oos_b_turn = turnover_ratio(oos_b_stats)

    base = (
        weights.train * float(train_stats.get("fitness", 0.0))
        + weights.validation * float(val_stats.get("fitness", 0.0))
        + weights.oos_proxy_a * float(oos_a_stats.get("fitness", 0.0))
        + weights.oos_proxy_b * float(oos_b_stats.get("fitness", 0.0))
    )

    # Penalize models that lose performance immediately outside train.
    train_fit = float(train_stats.get("fitness", 0.0))
    val_fit = float(val_stats.get("fitness", 0.0))
    oos_a_fit = float(oos_a_stats.get("fitness", 0.0))
    oos_b_fit = float(oos_b_stats.get("fitness", 0.0))
    train_val_gap = max(0.0, train_fit - val_fit)
    val_oos_gap = max(0.0, val_fit - min(oos_a_fit, oos_b_fit))
    decay_penalty = 0.35 * train_val_gap + 0.45 * val_oos_gap

    # Reward keeping proxy windows above breakeven by using portfolio value edge.
    val_value_edge = float(val_stats.get("final_value", 1000.0)) / 1000.0 - 1.0
    oos_a_value_edge = float(oos_a_stats.get("final_value", 1000.0)) / 1000.0 - 1.0
    oos_b_value_edge = float(oos_b_stats.get("final_value", 1000.0)) / 1000.0 - 1.0
    value_bonus = 0.20 * (val_value_edge + oos_a_value_edge + oos_b_value_edge) / 3.0

    turn_penalty = extra_turnover_penalty * (train_turn + val_turn + oos_a_turn + oos_b_turn)
    gate_fail_reasons = hard_gate_fail_reasons(train_stats, val_stats, oos_a_stats, oos_b_stats, gates)
    gate_pass = not any(gate_fail_reasons.values())

    robust_score = base + value_bonus - decay_penalty - turn_penalty
    if not gate_pass:
        robust_score += failed_gate_penalty

    return {
        "robust_score": float(robust_score),
        "gate_pass": float(1.0 if gate_pass else 0.0),
        "train_turnover": float(train_turn),
        "validation_turnover": float(val_turn),
        "oos_proxy_a_turnover": float(oos_a_turn),
        "oos_proxy_b_turnover": float(oos_b_turn),
        "turnover_penalty": float(turn_penalty),
        "train_validation_gap": float(train_val_gap),
        "validation_oos_gap": float(val_oos_gap),
        "decay_penalty": float(decay_penalty),
        "value_bonus": float(value_bonus),
        "gate_fail_reasons": gate_fail_reasons,
    }


def run_robust_evolution(
    *,
    programs: List[Any],
    evaluate_program_fn: Callable[..., Dict[str, float]],
    signal_fn: Callable[..., float],
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    oos_df: pd.DataFrame,
    inner_train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    oos_proxy_a_df: pd.DataFrame,
    oos_proxy_b_df: pd.DataFrame,
    tournament_selection_fn: Callable[[List[Any], int], Any],
    crossover_fn: Callable[[Any, Any], Any],
    mutate_fn: Callable[..., Any],
    build_tree_fn: Callable[..., Any],
    functions_dict: Dict[Any, Any],
    operators_list: List[str],
    mutation_rate: float,
    tournament_size: int,
    immigrant_frac: float,
    min_depth: int,
    max_depth: int,
    generations: int,
    patience: int,
    hall_of_fame_size: int,
    complexity_lambda: float,
    cost_bps: float,
    slippage_bps: float,
    weights: RobustWeights,
    gates: HardGates,
    extra_turnover_penalty: float = 0.08,
    failed_gate_penalty: float = -10.0,
    verbose: bool = True,
) -> Dict[str, Any]:
    es_programs = list(programs)
    es_history: List[Dict[str, float]] = []
    hall_of_fame: List[Dict[str, Any]] = []

    best_robust_seen = -1e18
    best_gen = -1
    best_program = None
    patience_left = patience

    for gen in range(generations):
        robust_scores = []
        train_fit_list = []
        val_fit_list = []
        valid_count = 0
        move_list = []
        expr_set = set()
        gate_fail_counts: Dict[str, int] = {}

        for program in es_programs:
            st_train = evaluate_program_fn(
                program,
                inner_train_df,
                signal_fn=signal_fn,
                cost_bps=cost_bps,
                slippage_bps=slippage_bps,
                complexity_lambda=complexity_lambda,
            )
            st_val = evaluate_program_fn(
                program,
                validation_df,
                signal_fn=signal_fn,
                cost_bps=cost_bps,
                slippage_bps=slippage_bps,
                complexity_lambda=complexity_lambda,
            )
            st_oos_a = evaluate_program_fn(
                program,
                oos_proxy_a_df,
                signal_fn=signal_fn,
                cost_bps=cost_bps,
                slippage_bps=slippage_bps,
                complexity_lambda=complexity_lambda,
            )
            st_oos_b = evaluate_program_fn(
                program,
                oos_proxy_b_df,
                signal_fn=signal_fn,
                cost_bps=cost_bps,
                slippage_bps=slippage_bps,
                complexity_lambda=complexity_lambda,
            )

            robust = score_robust_candidate(
                st_train,
                st_val,
                st_oos_a,
                st_oos_b,
                weights=weights,
                gates=gates,
                extra_turnover_penalty=extra_turnover_penalty,
                failed_gate_penalty=failed_gate_penalty,
            )
            robust_score = float(robust["robust_score"])
            gate_pass = bool(robust["gate_pass"])
            fail_reasons = robust.get("gate_fail_reasons", {})

            program.train_fitness = float(st_train["fitness"])
            program.val_fitness = float(st_val["fitness"])
            program.oos_proxy_a_fitness = float(st_oos_a["fitness"])
            program.oos_proxy_b_fitness = float(st_oos_b["fitness"])
            program.robust_fitness = robust_score
            program.passes_gate = gate_pass
            program.moves = int(st_train["moves"])
            program.set_fitness(robust_score)

            if gate_pass:
                valid_count += 1
            else:
                for reason_name, failed in fail_reasons.items():
                    if failed:
                        gate_fail_counts[reason_name] = gate_fail_counts.get(reason_name, 0) + 1

            robust_scores.append(robust_score)
            train_fit_list.append(program.train_fitness)
            val_fit_list.append(program.val_fitness)
            move_list.append(program.moves)
            expr_set.add(str(program))

        robust_arr = np.array(robust_scores, dtype=float)
        train_arr = np.array(train_fit_list, dtype=float)
        val_arr = np.array(val_fit_list, dtype=float)

        gen_sorted = sorted(
            es_programs,
            key=lambda x: (x.passes_gate, x.robust_fitness, x.val_fitness),
            reverse=True,
        )
        gen_best = gen_sorted[0]

        es_history.append(
            {
                "generation": gen,
                "best_robust": float(np.max(robust_arr)),
                "best_train": float(np.max(train_arr)),
                "best_val": float(np.max(val_arr)),
                "median_train": float(np.median(train_arr)),
                "median_val": float(np.median(val_arr)),
                "mean_robust": float(np.mean(robust_arr)),
                "valid_ratio": float(valid_count / len(es_programs)),
                "mean_moves": float(np.mean(move_list)),
                "unique_expr_ratio": float(len(expr_set) / len(es_programs)),
                "gate_fail_counts": gate_fail_counts,
            }
        )

        for cand in gen_sorted[:4]:
            hall_of_fame.append(
                {
                    "program": cand.copy(),
                    "expr": str(cand),
                    "robust_fitness": float(cand.robust_fitness),
                    "val_fitness": float(cand.val_fitness),
                    "train_fitness": float(cand.train_fitness),
                    "oos_proxy_a_fitness": float(cand.oos_proxy_a_fitness),
                    "oos_proxy_b_fitness": float(cand.oos_proxy_b_fitness),
                    "passes_gate": bool(cand.passes_gate),
                    "generation": gen,
                }
            )

        hall_of_fame_sorted = sorted(
            hall_of_fame,
            key=lambda x: (
                x["passes_gate"],
                x["robust_fitness"],
                x["val_fitness"],
                x["train_fitness"],
            ),
            reverse=True,
        )

        dedup_hof = []
        seen_expr = set()
        for item in hall_of_fame_sorted:
            if item["expr"] in seen_expr:
                continue
            seen_expr.add(item["expr"])
            dedup_hof.append(item)
            if len(dedup_hof) >= hall_of_fame_size:
                break
        hall_of_fame = dedup_hof

        this_best_robust = float(gen_best.robust_fitness)
        if this_best_robust > best_robust_seen + 1e-12:
            best_robust_seen = this_best_robust
            best_gen = gen
            best_program = gen_best.copy()
            patience_left = patience
        else:
            patience_left -= 1

        if verbose:
            g = es_history[-1]
            print(
                f"ROB Gen {gen:03d} | best_rob={g['best_robust']:.6f} "
                f"best_val={g['best_val']:.6f} valid={g['valid_ratio']:.2f} "
                f"moves={g['mean_moves']:.1f} div={g['unique_expr_ratio']:.2f} "
                f"pat={patience_left}"
            )

        if patience_left <= 0:
            if verbose:
                print(f"Early stop triggered at generation {gen} (best robust at gen {best_gen}).")
            break

        n_imm = int(len(es_programs) * immigrant_frac)
        survivors = gen_sorted[:-n_imm] if n_imm > 0 else gen_sorted

        immigrants = []
        for _ in range(n_imm):
            d = np.random.randint(min_depth, max_depth + 1)
            m = "full" if np.random.random() < 0.5 else "grow"
            immigrants.append(build_tree_fn(current_depth=0, max_depth=d, method=m))

        es_programs = survivors + immigrants

        next_gen = []
        elite = max(es_programs, key=lambda x: x.fitness)
        next_gen.append(elite.copy())

        while len(next_gen) < len(es_programs):
            p1 = tournament_selection_fn(es_programs, tournament_size=tournament_size)
            p2 = tournament_selection_fn(es_programs, tournament_size=tournament_size)

            c1, c2 = crossover_fn(p1, p2)

            if np.random.random() < mutation_rate:
                c1 = mutate_fn(c1, functions_dict, operators_list)
            if np.random.random() < mutation_rate:
                c2 = mutate_fn(c2, functions_dict, operators_list)

            next_gen.append(c1)
            if len(next_gen) < len(es_programs):
                next_gen.append(c2)

        es_programs = next_gen

    if best_program is None and len(hall_of_fame) > 0:
        best_program = hall_of_fame[0]["program"].copy()

    if best_program is None:
        raise RuntimeError("No best program found in robust evolution run.")

    selected_train_stats = evaluate_program_fn(
        best_program,
        train_df,
        signal_fn=signal_fn,
        cost_bps=cost_bps,
        slippage_bps=slippage_bps,
        complexity_lambda=complexity_lambda,
    )
    selected_test_stats = evaluate_program_fn(
        best_program,
        test_df,
        signal_fn=signal_fn,
        cost_bps=cost_bps,
        slippage_bps=slippage_bps,
        complexity_lambda=complexity_lambda,
    )
    selected_oos_stats = evaluate_program_fn(
        best_program,
        oos_df,
        signal_fn=signal_fn,
        cost_bps=cost_bps,
        slippage_bps=slippage_bps,
        complexity_lambda=complexity_lambda,
    )

    return {
        "best_program": best_program,
        "best_generation": int(best_gen),
        "best_robust_score": float(best_robust_seen),
        "es_history_df": pd.DataFrame(es_history),
        "hall_of_fame": hall_of_fame,
        "selected_train_stats": selected_train_stats,
        "selected_test_stats": selected_test_stats,
        "selected_oos_stats": selected_oos_stats,
    }
