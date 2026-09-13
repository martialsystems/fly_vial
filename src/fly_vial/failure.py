# Copyright (c) 2026 Martial Systems LLC
"""Pre-registered failure rules. Do not fit thresholds after a run."""

from __future__ import annotations

from typing import Any

FAIL_N_MIN = 50
FAIL_VIABILITY = 0.20
FAIL_T_MAX = 200

RULE_N0 = "n==0"
RULE_PAIRS0 = "accepted_pairs==0"
RULE_SMALL = "n<50_and_viability<0.20"


def failure_rule(rec: dict[str, Any], *, fail_n_min: int = FAIL_N_MIN, fail_viability: float = FAIL_VIABILITY) -> str | None:
    """Return the first matching rule, or None. t=0 never uses accepted_pairs==0."""
    n = int(rec.get("n") or 0)
    if n == 0:
        return RULE_N0
    t = int(rec.get("t") or 0)
    if t > 0 and int(rec.get("n_accepted") or 0) == 0:
        return RULE_PAIRS0
    viab = float((rec.get("fitness_components") or {}).get("viability") or 0.0)
    if n < fail_n_min and viab < fail_viability:
        return RULE_SMALL
    return None


def time_to_failure(
    records: list[dict[str, Any]],
    *,
    fail_t_max: int = FAIL_T_MAX,
    fail_n_min: int = FAIL_N_MIN,
    fail_viability: float = FAIL_VIABILITY,
) -> tuple[int, str | None]:
    for rec in records:
        rule = failure_rule(rec, fail_n_min=fail_n_min, fail_viability=fail_viability)
        if rule is not None:
            return int(rec["t"]), rule
    return int(fail_t_max), None


def series_from_records(records: list[dict[str, Any]]) -> dict[str, list]:
    n = [int(r["n"]) for r in records]
    f = [float(r["F"]) for r in records]
    phi = [float(r["mean_pairwise_phi"]) for r in records]
    viab = [float(r["fitness_components"]["viability"]) for r in records]
    fert = [float(r["fitness_components"]["fertility"]) for r in records]
    court = [
        None if int(r["t"]) == 0 else float(r["fitness_components"]["courtship"])
        for r in records
    ]
    pairs = [int(r["n_accepted"]) for r in records]
    return {
        "n": n,
        "F": f,
        "phi": phi,
        "egg_viability": viab,
        "fertility": fert,
        "courtship": court,
        "accepted_pairs": pairs,
    }
