# Copyright (c) 2026 Martial Systems LLC
"""Refuse banned scientific claims."""

from __future__ import annotations

from typing import Any

from vialforge.graphs._common import binary_graph

_FLAGS = (
    "unique_brains",
    "population_spike_default",
    "animation_as_science",
    "deformed_visual",
    "immigration_or_rescue",
)


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in _FLAGS if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="vial.claim_bans", evaluate=_evaluate, extra=list(_FLAGS))
