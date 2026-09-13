# Copyright (c) 2026 Martial Systems LLC
"""Inbreeding depression must be expressible: recessive load and/or template penalty."""

from __future__ import annotations

from typing import Any

from vialforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    n_load = int(state.get("n_load") or 0)
    s_let = float(state.get("s_let") or 0.0)
    beta = float(state.get("beta") or 0.0)
    kappa = float(state.get("kappa") or 0.0)
    has_load = n_load > 0 and s_let > 0.0
    has_template = beta > 0.0 or kappa > 0.0
    v = [] if (has_load or has_template) else ["no_inbreeding_mechanism"]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="vial.load_required",
        evaluate=_evaluate,
        extra=["n_load", "s_let", "beta", "kappa"],
    )
