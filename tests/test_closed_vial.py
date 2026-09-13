# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import inspect

from fly_vial import population
from fly_vial.config import RunConfig
from fly_vial.population import run_generations
from vialforge.gate import LawBlockedError, require_closed_vial


def test_no_immigration_api() -> None:
    src = inspect.getsource(population)
    assert "immigrat" not in src.lower()
    assert "wildtype" not in src.lower()
    assert "restock" not in src.lower()


def test_matrilines_are_founders_only() -> None:
    cfg = RunConfig(n=24, generations=3, seed=13, k=2)
    result = run_generations(cfg)
    assert result["generations"][0]["matriline_count"] <= 24
    last = result["generations"][-1]
    assert last["matriline_count"] <= result["generations"][0]["matriline_count"]


def test_closed_vial_law_refuses_immigration() -> None:
    require_closed_vial()
    try:
        require_closed_vial(immigration=True)
        raise AssertionError("expected block")
    except LawBlockedError:
        pass
