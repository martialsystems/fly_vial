# Copyright (c) 2026 Martial Systems LLC
"""Call sites for refuse laws."""

from __future__ import annotations

import re
from typing import Any

from vialforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError, require_law

from vialforge.graphs.claim_bans import build_graph as build_claims
from vialforge.graphs.closed_vial import build_graph as build_closed
from vialforge.graphs.engine_order import EVAL_N_MAX, build_graph as build_engine
from vialforge.graphs.load_required import build_graph as build_load
from vialforge.graphs.template_identity import (
    FLYWIRE_N,
    MALECNS_N,
    build_graph as build_templates,
)

UNIQUE_RE = re.compile(r"unique reconstructed|1,?000 unique", re.I)
SPIKE_RE = re.compile(
    r"(default|population).{0,40}(full[- ]cns|139k|167k|166k).{0,20}spike|"
    r"live (whole-cns|139k|167k|166k) LIF",
    re.I,
)
ANIM_RE = re.compile(r"\b(animation|renderer)\b.{0,40}\b(science|result|finding)\b", re.I)
DEFORM_RE = re.compile(r"deformed.{0,30}visual style|visual style.{0,30}deformed", re.I)
RESCUE_RE = re.compile(r"\b(with immigration|wild-type rescue|restock from template)\b", re.I)


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "vial_claims"))
    state = {
        "unique_brains": False,
        "population_spike_default": False,
        "animation_as_science": False,
        "deformed_visual": False,
        "immigration_or_rescue": False,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="vial.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_engine(
    *,
    eval_n: int = 0,
    eval_n_max: int = EVAL_N_MAX,
    eval_whole_population: bool = False,
    eval_as_default_engine: bool = False,
) -> None:
    require_law(
        build_engine(),
        {
            "eval_n": int(eval_n),
            "eval_n_max": int(eval_n_max),
            "eval_whole_population": bool(eval_whole_population),
            "eval_as_default_engine": bool(eval_as_default_engine),
        },
        allow_decisions=["allow"],
        law_id="vial.engine_order",
        thread_id="engine_order",
        raise_error=True,
    )


def require_closed_vial(
    *,
    immigration: bool = False,
    wildtype_injection: bool = False,
    restock_from_template: bool = False,
) -> None:
    require_law(
        build_closed(),
        {
            "immigration": bool(immigration),
            "wildtype_injection": bool(wildtype_injection),
            "restock_from_template": bool(restock_from_template),
        },
        allow_decisions=["allow"],
        law_id="vial.closed_vial",
        thread_id="closed_vial",
        raise_error=True,
    )


def require_load(
    *,
    n_load: int,
    s_let: float,
    beta: float,
    kappa: float,
) -> None:
    require_law(
        build_load(),
        {
            "n_load": int(n_load),
            "s_let": float(s_let),
            "beta": float(beta),
            "kappa": float(kappa),
        },
        allow_decisions=["allow"],
        law_id="vial.load_required",
        thread_id="load_required",
        raise_error=True,
    )


def require_templates(
    *,
    female_n: int = FLYWIRE_N,
    male_n: int = MALECNS_N,
    mixed_sex_template: bool = False,
    unique_reconstruction: bool = False,
) -> None:
    require_law(
        build_templates(),
        {
            "female_n": int(female_n),
            "male_n": int(male_n),
            "mixed_sex_template": bool(mixed_sex_template),
            "unique_reconstruction": bool(unique_reconstruction),
        },
        allow_decisions=["allow"],
        law_id="vial.template_identity",
        thread_id="template_identity",
        raise_error=True,
    )


def scan_text_flags(text: str) -> dict[str, bool]:
    t = text or ""
    return {
        "unique_brains": bool(UNIQUE_RE.search(t)),
        "population_spike_default": bool(SPIKE_RE.search(t)),
        "animation_as_science": bool(ANIM_RE.search(t)),
        "deformed_visual": bool(DEFORM_RE.search(t)),
        "immigration_or_rescue": bool(RESCUE_RE.search(t)),
    }


def require_readme_clean(text: str) -> None:
    require_claims(**scan_text_flags(text), thread_id="readme")


__all__ = [
    "EVAL_N_MAX",
    "FLYWIRE_N",
    "MALECNS_N",
    "LawBlockedError",
    "require_claims",
    "require_engine",
    "require_closed_vial",
    "require_load",
    "require_templates",
    "require_readme_clean",
    "scan_text_flags",
]
