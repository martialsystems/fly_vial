# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import pytest

from vialforge.gate import (
    FLYWIRE_N,
    MALECNS_N,
    LawBlockedError,
    require_claims,
    require_load,
    require_templates,
    scan_text_flags,
)
from vialforge.product_laws import laws


def test_laws_catalog_has_five() -> None:
    ids = [row["id"] for row in laws()]
    assert ids == [
        "vial.claim_bans",
        "vial.engine_order",
        "vial.closed_vial",
        "vial.load_required",
        "vial.template_identity",
    ]


def test_claims_refuse_unique_brains() -> None:
    with pytest.raises(LawBlockedError):
        require_claims(unique_brains=True)


def test_claims_allow_clean() -> None:
    require_claims()


def test_load_required_refuses_empty() -> None:
    with pytest.raises(LawBlockedError):
        require_load(n_load=0, s_let=0.0, beta=0.0, kappa=0.0)


def test_load_required_allows_recessives() -> None:
    require_load(n_load=64, s_let=1.0, beta=0.0, kappa=0.0)


def test_template_identity() -> None:
    require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N)
    with pytest.raises(LawBlockedError):
        require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, unique_reconstruction=True)
    with pytest.raises(LawBlockedError):
        require_templates(female_n=12, male_n=MALECNS_N)


def test_scan_readme_current_is_clean() -> None:
    from pathlib import Path

    text = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
    flags = scan_text_flags(text)
    assert not any(flags.values()), flags
