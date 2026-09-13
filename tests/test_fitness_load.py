# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import phenotype
from fly_vial.genome import FEMALE, MALE
from tests.helpers import one_fly


def test_lethal_homozygote_zeroes_viability() -> None:
    cfg = RunConfig(n=1)
    pop = one_fly(sex=FEMALE, load_hom_lethal=True, cfg=cfg)
    ph = phenotype(pop, cfg)
    assert ph.v_load[0] == 0.0
    assert ph.viability[0] == 0.0
    assert ph.fertility[0] == 0.0
    assert bool(ph.deformed[0])


def test_heterozygote_lethal_does_not_bite() -> None:
    cfg = RunConfig(n=1)
    pop = one_fly(sex=MALE, cfg=cfg)
    pop.load[0, 0, 0] = 1
    pop.load[0, 0, 1] = 0
    ph = phenotype(pop, cfg)
    assert ph.v_load[0] == 1.0


def test_sublethal_homozygote_multiplies() -> None:
    cfg = RunConfig(n=1, s_sub=0.25)
    pop = one_fly(sex=FEMALE, cfg=cfg)
    pop.load[0, cfg.n_lethal, :] = 1
    ph = phenotype(pop, cfg)
    assert abs(ph.v_load[0] - 0.75) < 1e-12


def test_template_origin_is_near_unit_competence() -> None:
    cfg = RunConfig(n=1)
    pop = one_fly(sex=MALE, cfg=cfg)
    ph = phenotype(pop, cfg)
    assert ph.song[0] > 0.9
    assert ph.d_template[0] == 0.0
