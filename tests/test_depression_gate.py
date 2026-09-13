# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_vial.config import RunConfig
from fly_vial.population import run_generations

REPO = Path(__file__).resolve().parents[1]


def test_short_assortative_run_raises_relatedness() -> None:
    cfg = RunConfig(n=40, generations=8, seed=1, k=3, arm="assortative")
    result = run_generations(cfg)
    gens = result["generations"]
    assert gens[0]["t"] == 0
    assert gens[-1]["t"] == 8
    assert gens[-1]["F"] > gens[0]["F"]
    assert all("n_accepted" in g for g in gens)
    assert all("cluster_count" in g for g in gens)
    assert result["n_eval_hook_total"] == 0
    for g in gens:
        assert abs(g["F"] + g["heterozygosity_qtl"] - 1.0) < 1e-9


def _load(name: str) -> dict:
    path = REPO / "logs" / name
    assert path.is_file()
    return json.loads(path.read_text(encoding="utf-8"))


def test_locked_g80_assortative_and_random_contrast() -> None:
    assort = _load("assort_80.json")
    rand = _load("random_80.json")
    assert assort["config"]["mating_mode"] == "assortative_knn"
    assert rand["config"]["mating_mode"] == "random"
    ag, rg = assort["generations"], rand["generations"]
    assert ag[0]["t"] == rg[0]["t"] == 0
    assert ag[-1]["t"] == rg[-1]["t"] == 80
    assert ag[-1]["n"] == rg[-1]["n"] == 1000
    for g in ag + rg:
        assert abs(g["F"] + g["heterozygosity_qtl"] - 1.0) < 1e-9
        assert g["n_eval_hook"] == 0
    assert ag[-1]["F"] > 0.5
    assert rg[-1]["F"] < 0.05
    assert ag[-1]["F"] > rg[-1]["F"]
    assert ag[-1]["fitness_components"]["viability"] < ag[0]["fitness_components"]["viability"]
    assert rg[-1]["fitness_components"]["viability"] < rg[0]["fitness_components"]["viability"]
    assert ag[-1]["fitness_components"]["viability"] < rg[-1]["fitness_components"]["viability"]
    assert ag[-1]["fitness_components"]["fertility"] < ag[0]["fitness_components"]["fertility"]
    assert ag[1]["fitness_components"]["courtship"] > 0.9
    assert ag[-1]["fitness_components"]["courtship"] < ag[1]["fitness_components"]["courtship"]
    assert rg[-1]["fitness_components"]["courtship"] < rg[1]["fitness_components"]["courtship"]
    assert abs(
        ag[-1]["fitness_components"]["courtship"] - rg[-1]["fitness_components"]["courtship"]
    ) < 0.02
    assert "mean_pairwise_phi" in ag[-1]


def test_seeds_2_and_3_pass_promotion_bar() -> None:
    wright = 0.04
    for seed in (2, 3):
        assort = _load(f"assort_80_s{seed}.json")
        rand = _load(f"random_80_s{seed}.json")
        assert assort["config"]["seed"] == seed
        assert rand["config"]["seed"] == seed
        assert assort["config"]["eval_connectome"] is True
        assert rand["config"]["eval_connectome"] is True
        af = assort["generations"][-1]["F"]
        rf = rand["generations"][-1]["F"]
        assert af > 0.2
        assert af > 5 * wright
        assert 0.03 <= rf <= 0.05
        ac = assort["generations"][1]["fitness_components"]["courtship"]
        rc = rand["generations"][1]["fitness_components"]["courtship"]
        ac80 = assort["generations"][-1]["fitness_components"]["courtship"]
        rc80 = rand["generations"][-1]["fitness_components"]["courtship"]
        assert ac80 < ac
        assert rc80 < rc
        assert assort["generations"][-1]["n"] == 1000
        assert rand["generations"][-1]["n"] == 1000


def test_seed1_lock_files_not_replaced() -> None:
    a = _load("assort_80.json")
    r = _load("random_80.json")
    assert a["config"]["seed"] == 1
    assert r["config"]["seed"] == 1
    assert a["config"]["eval_connectome"] is False
    assert r["config"]["eval_connectome"] is False
    assert abs(a["generations"][-1]["F"] - 0.5238) < 1e-4
    assert abs(r["generations"][-1]["F"] - 0.0341) < 1e-4
