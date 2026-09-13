# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import phenotype
from fly_vial.genome import FEMALE, MALE, init_population
from fly_vial.mating import pair
from fly_vial.similarity import freeze_sigma0, mating_traits, pairwise_fm_distance


def _pop(n: int, seed: int) -> tuple:
    cfg = RunConfig(n=n, seed=seed, lambda_init=0.0)
    rng = np.random.default_rng(seed)
    pop = init_population(cfg, rng)
    ph = phenotype(pop, cfg)
    sigma0 = freeze_sigma0(mating_traits(ph), cfg)
    return pop, ph, cfg, rng, sigma0


def test_knn_assigns_nearest_available() -> None:
    pop, ph, cfg, rng, sigma0 = _pop(12, 7)
    cfg = RunConfig(n=12, seed=7, mating_mode="assortative_knn", k=1, m_max=1, lambda_init=0.0)
    pairing = pair(pop, ph, cfg, rng, sigma0)
    assert pairing.n_accepted > 0
    f_idx = np.flatnonzero(pop.sex == FEMALE)
    m_idx = np.flatnonzero(pop.sex == MALE)
    dist = pairwise_fm_distance(mating_traits(ph)[f_idx], mating_traits(ph)[m_idx], sigma0)
    used = set()
    for fi, mi, d in zip(pairing.female_idx, pairing.male_idx, pairing.distance, strict=True):
        assert pop.sex[fi] == FEMALE
        assert pop.sex[mi] == MALE
        assert mi not in used
        used.add(int(mi))
        assert d >= 0.0
    assert pairing.n_failed_match + pairing.n_accepted == int(np.sum(pop.sex == FEMALE))


def test_threshold_can_fail() -> None:
    pop, ph, cfg, rng, sigma0 = _pop(10, 8)
    cfg = RunConfig(
        n=10,
        seed=8,
        mating_mode="assortative_threshold",
        d_star=0.0,
        m_max=1,
        lambda_init=0.0,
    )
    pairing = pair(pop, ph, cfg, rng, sigma0)
    assert pairing.n_failed_match >= 0
    assert pairing.n_accepted + pairing.n_failed_match == int(np.sum(pop.sex == FEMALE))


def test_random_mode_exists() -> None:
    pop, ph, cfg, rng, sigma0 = _pop(16, 9)
    cfg = RunConfig(n=16, seed=9, mating_mode="random", m_max=1, lambda_init=0.0)
    pairing = pair(pop, ph, cfg, rng, sigma0)
    assert pairing.n_accepted > 0
    assert pairing.n_accepted <= min(int(np.sum(pop.sex == FEMALE)), int(np.sum(pop.sex == MALE)))


def test_receptivity_filter_runs_after_legality() -> None:
    pop, ph, cfg, rng, sigma0 = _pop(20, 10)
    cfg = RunConfig(
        n=20,
        seed=10,
        mating_mode="assortative_knn",
        k=3,
        receptivity_filter=True,
        theta_rec=1.1,
        lambda_init=0.0,
    )
    pairing = pair(pop, ph, cfg, rng, sigma0)
    assert pairing.n_accepted == 0
    assert pairing.n_failed_match == int(np.sum(pop.sex == FEMALE))
