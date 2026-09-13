#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Refuse paths for vialforge laws."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from vialforge.gate import (
    FLYWIRE_N,
    MALECNS_N,
    LawBlockedError,
    require_claims,
    require_closed_vial,
    require_engine,
    require_load,
    require_templates,
)


def main() -> None:
    require_claims()
    try:
        require_claims(unique_brains=True)
        raise SystemExit("expected unique_brains block")
    except LawBlockedError:
        pass

    require_engine(eval_n=0)
    try:
        require_engine(eval_n=9)
        raise SystemExit("expected eval_n cap block")
    except LawBlockedError:
        pass
    try:
        require_engine(eval_whole_population=True)
        raise SystemExit("expected whole-population eval block")
    except LawBlockedError:
        pass

    require_closed_vial()
    try:
        require_closed_vial(immigration=True)
        raise SystemExit("expected immigration block")
    except LawBlockedError:
        pass

    require_load(n_load=64, s_let=1.0, beta=0.15, kappa=0.5)
    try:
        require_load(n_load=0, s_let=0.0, beta=0.0, kappa=0.0)
        raise SystemExit("expected empty-load block")
    except LawBlockedError:
        pass

    require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N)
    try:
        require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N, unique_reconstruction=True)
        raise SystemExit("expected unique reconstruction block")
    except LawBlockedError:
        pass
    try:
        require_templates(female_n=1, male_n=MALECNS_N)
        raise SystemExit("expected female count block")
    except LawBlockedError:
        pass

    print("vialforge sanity pass")


if __name__ == "__main__":
    main()
