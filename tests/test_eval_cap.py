# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import pytest

from fly_vial.config import RunConfig
from fly_vial.population import run_generations
from vialforge.gate import LawBlockedError, require_engine


def test_eval_n_over_cap_blocked() -> None:
    with pytest.raises(LawBlockedError):
        require_engine(eval_n=9, eval_n_max=8)


def test_whole_population_eval_blocked() -> None:
    with pytest.raises(LawBlockedError):
        require_engine(eval_whole_population=True)


def test_default_run_does_not_eval() -> None:
    cfg = RunConfig(n=16, generations=2, seed=14, k=2)
    result = run_generations(cfg)
    assert result["n_eval_hook_total"] == 0
    assert result["eval_hook"] == []


def test_eval_hook_respects_cap() -> None:
    cfg = RunConfig(n=16, generations=1, seed=15, k=2, eval_connectome=True, eval_pairs=4)
    result = run_generations(cfg)
    assert result["n_eval_hook_total"] <= 8
    assert len(result["eval_hook"]) <= 4
