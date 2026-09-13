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
    assert gens[-1]["mean_pairwise_phi"] > gens[0]["mean_pairwise_phi"]
    assert gens[-1]["heterozygosity_qtl"] < gens[0]["heterozygosity_qtl"]
    assert gens[-1]["F"] > gens[0]["F"]
    assert all("n_accepted" in g for g in gens)
    assert all("cluster_count" in g for g in gens)
    assert result["n_eval_hook_total"] == 0


def test_locked_g80_shows_inbreeding_depression() -> None:
    path = REPO / "logs" / "assort_80.json"
    assert path.is_file()
    data = json.loads(path.read_text(encoding="utf-8"))
    gens = data["generations"]
    assert gens[0]["t"] == 0
    last = gens[-1]
    assert last["t"] == 80
    assert last["mean_pairwise_phi"] > gens[0]["mean_pairwise_phi"]
    assert last["heterozygosity_qtl"] < gens[0]["heterozygosity_qtl"]
    assert last["fitness_components"]["viability"] < gens[0]["fitness_components"]["viability"]
    assert last["fitness_components"]["fertility"] < gens[0]["fitness_components"]["fertility"]
    g0_court = gens[1]["fitness_components"]["courtship"]
    last_court = last["fitness_components"]["courtship"]
    assert last_court < g0_court
    assert last["n_eval_hook"] == 0
