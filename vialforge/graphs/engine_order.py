# Copyright (c) 2026 Martial Systems LLC
"""G2P parameter map is the default engine; connectome eval is a capped hook."""

from __future__ import annotations

from typing import Any

from vialforge.graphs._common import binary_graph

EVAL_N_MAX = 8


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if bool(state.get("eval_whole_population")):
        v.append("eval_whole_population")
    if bool(state.get("eval_as_default_engine")):
        v.append("eval_as_default_engine")
    n = int(state.get("eval_n") or 0)
    cap = int(state.get("eval_n_max") or EVAL_N_MAX)
    if n > cap:
        v.append("eval_n_over_cap")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="vial.engine_order",
        evaluate=_evaluate,
        extra=["eval_whole_population", "eval_as_default_engine", "eval_n", "eval_n_max"],
    )
