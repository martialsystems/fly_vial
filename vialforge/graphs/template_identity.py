# Copyright (c) 2026 Martial Systems LLC
"""Female FlyWire 139255; male MaleCNS 166691; templates are not unique reconstructions."""

from __future__ import annotations

from typing import Any

from vialforge.graphs._common import binary_graph

FLYWIRE_N = 139_255
MALECNS_N = 166_691


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if int(state.get("female_n") or 0) != FLYWIRE_N:
        v.append("female_count")
    if int(state.get("male_n") or 0) != MALECNS_N:
        v.append("male_count")
    if bool(state.get("mixed_sex_template")):
        v.append("mixed_sex_template")
    if bool(state.get("unique_reconstruction")):
        v.append("unique_reconstruction")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="vial.template_identity",
        evaluate=_evaluate,
        extra=["female_n", "male_n", "mixed_sex_template", "unique_reconstruction"],
    )
