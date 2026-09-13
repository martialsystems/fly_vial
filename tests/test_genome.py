# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.genome import FEMALE, MALE, QTL_AUTO, additive_z, init_population


def test_qtl_layout_matches_k_a() -> None:
    assert len(QTL_AUTO) == 16
    cfg = RunConfig(n=20, seed=1)
    pop = init_population(cfg, np.random.default_rng(1))
    assert pop.qtl_auto.shape == (20, 16, 2)
    assert pop.qtl_x.shape == (20, 4, 2)
    assert pop.load.shape == (20, 64, 2)
    assert np.all(np.abs(pop.qtl_auto) <= cfg.z_max)


def test_male_x_slot1_unused() -> None:
    cfg = RunConfig(n=40, seed=2)
    pop = init_population(cfg, np.random.default_rng(2))
    males = pop.sex == MALE
    assert np.all(pop.qtl_x[males, :, 1] == 0.0)
    assert np.all(pop.founder_qtl_x[males, :, 1] == 0)


def test_additive_z_x_hemizygous() -> None:
    cfg = RunConfig(n=2, seed=3, lambda_init=0.0, sigma_init=0.0)
    pop = init_population(cfg, np.random.default_rng(3))
    pop.sex[:] = np.array([FEMALE, MALE], dtype=np.uint8)
    pop.qtl_x[0, :, 0] = 1.0
    pop.qtl_x[0, :, 1] = -1.0
    pop.qtl_x[1, :, 0] = 0.4
    pop.qtl_x[1, :, 1] = 9.0
    z = additive_z(pop)
    assert abs(z[0, 16] - 0.0) < 1e-12
    assert abs(z[1, 16] - 0.4) < 1e-12


def test_founders_have_unique_qtl_ids() -> None:
    cfg = RunConfig(n=10, seed=4)
    pop = init_population(cfg, np.random.default_rng(4))
    ids = pop.founder_qtl_auto.reshape(-1)
    assert len(set(int(x) for x in ids)) == ids.size


def test_sex_ratio_roughly_equal() -> None:
    cfg = RunConfig(n=200, seed=5, sex_imbalance_max=50)
    pop = init_population(cfg, np.random.default_rng(5))
    nf = int(np.sum(pop.sex == FEMALE))
    assert abs(nf - (200 - nf)) <= 50
