# Copyright (c) 2026 Martial Systems LLC
"""Refuse immigration, wild-type injection, template restock."""

from __future__ import annotations

from typing import Any

from vialforge.graphs._common import binary_graph

_FLAGS = ("immigration", "wildtype_injection", "restock_from_template")


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in _FLAGS if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="vial.closed_vial", evaluate=_evaluate, extra=list(_FLAGS))
