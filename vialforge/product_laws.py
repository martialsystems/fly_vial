# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any

from vialforge.graphs.template_identity import FLYWIRE_N, MALECNS_N


def laws() -> list[dict[str, Any]]:
    from vialforge.graphs.claim_bans import build_graph as claim_bans
    from vialforge.graphs.closed_vial import build_graph as closed_vial
    from vialforge.graphs.engine_order import build_graph as engine_order
    from vialforge.graphs.load_required import build_graph as load_required
    from vialforge.graphs.template_identity import build_graph as template_identity

    return [
        {
            "id": "vial.claim_bans",
            "build": claim_bans,
            "state": {
                "unique_brains": False,
                "population_spike_default": False,
                "animation_as_science": False,
                "deformed_visual": False,
                "immigration_or_rescue": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "vial.engine_order",
            "build": engine_order,
            "state": {
                "eval_whole_population": False,
                "eval_as_default_engine": False,
                "eval_n": 0,
                "eval_n_max": 8,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "vial.closed_vial",
            "build": closed_vial,
            "state": {
                "immigration": False,
                "wildtype_injection": False,
                "restock_from_template": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "vial.load_required",
            "build": load_required,
            "state": {"n_load": 64, "s_let": 1.0, "beta": 0.15, "kappa": 0.5},
            "allow_decisions": ["allow"],
        },
        {
            "id": "vial.template_identity",
            "build": template_identity,
            "state": {
                "female_n": FLYWIRE_N,
                "male_n": MALECNS_N,
                "mixed_sex_template": False,
                "unique_reconstruction": False,
            },
            "allow_decisions": ["allow"],
        },
    ]
