# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import phenotype
from fly_vial.genome import FEMALE, MALE, init_population
from fly_vial.inheritance import meiosis_mutate
from fly_vial.mating import pair
from fly_vial.similarity import freeze_sigma0, mating_traits


def test_offspring_alleles_come_from_parents() -> None:
    cfg = RunConfig(n=8, seed=11, lambda_init=0.0, sigma_mu=0.0, p_pleio=0.0, u=0.0, c0=4.0)
    rng = np.random.default_rng(11)
    pop = init_population(cfg, rng)
    ph = phenotype(pop, cfg)
    sigma0 = freeze_sigma0(mating_traits(ph), cfg)
    pairing = pair(pop, ph, cfg, rng, sigma0)
    eggs, pair_of, clutch = meiosis_mutate(pop, ph, pairing, cfg, rng)
    assert eggs.n == int(clutch.sum())
    assert eggs.n > 0
    for i in range(eggs.n):
        p = int(pair_of[i])
        mom = int(pairing.female_idx[p])
        dad = int(pairing.male_idx[p])
        for loc in range(cfg.k_a):
            a0 = eggs.qtl_auto[i, loc, 0]
            a1 = eggs.qtl_auto[i, loc, 1]
            assert a0 in set(pop.qtl_auto[mom, loc].tolist())
            assert a1 in set(pop.qtl_auto[dad, loc].tolist())
        if eggs.sex[i] == MALE:
            assert eggs.qtl_x[i, :, 1].sum() == 0.0
            assert eggs.matriline[i] == pop.matriline[mom]


def test_load_mutation_mints_founder_id() -> None:
    cfg = RunConfig(n=6, seed=12, lambda_init=0.0, u=1.0, sigma_mu=0.0, p_pleio=0.0, c0=2.0)
    rng = np.random.default_rng(12)
    pop = init_population(cfg, rng)
    ph = phenotype(pop, cfg)
    sigma0 = freeze_sigma0(mating_traits(ph), cfg)
    pairing = pair(pop, ph, cfg, rng, sigma0)
    eggs, _, _ = meiosis_mutate(pop, ph, pairing, cfg, rng)
    assert eggs.next_founder > pop.next_founder
    assert int((eggs.load == 1).sum()) > 0
