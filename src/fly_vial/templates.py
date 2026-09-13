# Copyright (c) 2026 Martial Systems LLC
"""Published template identifiers and circuit type-name lists."""

from __future__ import annotations

import json

from fly_vial.genome import FEMALE, MALE
from fly_vial.paths import TEMPLATES
from vialforge.graphs.template_identity import FLYWIRE_N, MALECNS_N

FEMALE_TEMPLATE = "flywire_female"
MALE_TEMPLATE = "malecns_male"


def template_id_for_sex(sex: int) -> str:
    if sex == FEMALE:
        return FEMALE_TEMPLATE
    if sex == MALE:
        return MALE_TEMPLATE
    raise ValueError(f"unknown sex {sex}")


def load_template(name: str) -> dict:
    path = TEMPLATES / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def counts() -> tuple[int, int]:
    female = load_template(FEMALE_TEMPLATE)
    male = load_template(MALE_TEMPLATE)
    return int(female["n_neurons"]), int(male["n_neurons"])


def assert_template_counts() -> None:
    fn, mn = counts()
    if fn != FLYWIRE_N or mn != MALECNS_N:
        raise ValueError(f"template counts {fn}, {mn} != {FLYWIRE_N}, {MALECNS_N}")
