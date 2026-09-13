# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from fly_vial.config import RunConfig
from fly_vial.failure import RULE_N0, RULE_PAIRS0, RULE_SMALL, time_to_failure
from fly_vial.population import run_generations

REPO = Path(__file__).resolve().parents[1]
LOCKED_ASSORT = "92a328278e62c4c607749c9358cdc733e1f06424a4b7f13c97c352ce4f4f759b"
LOCKED_RANDOM = "3c4606204cdf5516ddf7bbf371a59111473c944510fff4f87f8599b1171e8e61"


def _sha(name: str) -> str:
    return hashlib.sha256((REPO / "logs" / name).read_bytes()).hexdigest()


def test_locked_sha256_unchanged() -> None:
    assert _sha("assort_80.json") == LOCKED_ASSORT
    assert _sha("random_80.json") == LOCKED_RANDOM


def test_t_fail_n0_on_fixture() -> None:
    recs = [
        {"t": 0, "n": 100, "n_accepted": 0, "fitness_components": {"viability": 1.0}},
        {"t": 1, "n": 0, "n_accepted": 0, "fitness_components": {"viability": 0.0}},
    ]
    t_fail, rule = time_to_failure(recs)
    assert t_fail == 1
    assert rule == RULE_N0


def test_t_fail_pairs0_skips_t0() -> None:
    recs = [
        {"t": 0, "n": 100, "n_accepted": 0, "fitness_components": {"viability": 0.9}},
        {"t": 1, "n": 80, "n_accepted": 0, "fitness_components": {"viability": 0.9}},
    ]
    t_fail, rule = time_to_failure(recs)
    assert t_fail == 1
    assert rule == RULE_PAIRS0


def test_t_fail_small_vial() -> None:
    recs = [
        {"t": 0, "n": 1000, "n_accepted": 0, "fitness_components": {"viability": 0.9}},
        {"t": 4, "n": 40, "n_accepted": 12, "fitness_components": {"viability": 0.1}},
    ]
    t_fail, rule = time_to_failure(recs)
    assert t_fail == 4
    assert rule == RULE_SMALL


def test_t_fail_survives_to_horizon() -> None:
    recs = [
        {"t": t, "n": 1000, "n_accepted": 400, "fitness_components": {"viability": 0.8}}
        for t in range(0, 81)
    ]
    t_fail, rule = time_to_failure(recs)
    assert t_fail == 200
    assert rule is None


def test_cap_off_t0_is_n1000() -> None:
    cfg = RunConfig(n=40, generations=1, seed=7, k=3, cap="off", n_ceiling=40)
    result = run_generations(cfg)
    assert result["generations"][0]["n"] == 40
    assert result["cap"] == "off"


def test_cap_off_can_leave_target_n() -> None:
    cfg = RunConfig(
        n=20,
        generations=4,
        seed=8,
        k=2,
        cap="off",
        n_ceiling=20,
        c0=1.0,
        lambda_init=8.0,
    )
    result = run_generations(cfg)
    ns = [g["n"] for g in result["generations"] if g["t"] > 0]
    assert ns
    assert any(n != 20 for n in ns)


def test_blocks_refused_until_capoff_logged() -> None:
    cfg = RunConfig(n=10, generations=1, seed=1, blocks=True)
    with pytest.raises(ValueError, match="blocks"):
        run_generations(cfg)


def test_capoff_logs_define_t_fail() -> None:
    knn = []
    rand = []
    for s in (1, 2, 3):
        k = json.loads((REPO / "logs" / f"fail_capoff_knn_s{s}.json").read_text())
        r = json.loads((REPO / "logs" / f"fail_capoff_rand_s{s}.json").read_text())
        assert k["T_fail"] is not None
        assert r["T_fail"] is not None
        assert k["cap"] == "off"
        assert r["cap"] == "off"
        knn.append(k["T_fail"])
        rand.append(r["T_fail"])
        c1 = k["courtship"][1]
        cL = k["courtship"][-1]
        assert c1 is not None and cL is not None
    from statistics import median

    assert median(knn) == median(rand) == 200


def test_capon_knn_f_still_above_wright() -> None:
    for s in (1, 2, 3):
        k = json.loads((REPO / "logs" / f"fail_capon_knn_s{s}.json").read_text())
        r = json.loads((REPO / "logs" / f"fail_capon_rand_s{s}.json").read_text())
        assert k["generations"][-1]["F"] > 0.2
        assert r["generations"][-1]["F"] < 0.05
