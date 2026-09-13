# Copyright (c) 2026 Martial Systems LLC
"""Meiosis, mutation, and clutch expansion. Founder IDs follow allelic lineage."""

from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import Phenotype, clutch_sizes
from fly_vial.genome import FEMALE, MALE, Pop, clip_qtl
from fly_vial.mating import Pairing


def _take_hap(arr: np.ndarray, idx: np.ndarray, pick: np.ndarray) -> np.ndarray:
    """arr (n_parent, L, 2), idx (n_eggs,), pick (n_eggs, L) -> (n_eggs, L)."""
    rows = arr[idx]
    pick3 = pick[:, :, None]
    return np.take_along_axis(rows, pick3, axis=2)[:, :, 0]


def meiosis_mutate(
    pop: Pop,
    ph: Phenotype,
    pairing: Pairing,
    cfg: RunConfig,
    rng: np.random.Generator,
) -> tuple[Pop, np.ndarray, np.ndarray]:
    """Return candidate eggs (before viability filter) and parent pair index per egg.

    The second array maps egg -> pair index. Third is clutch size per pair.
    """
    if pairing.n_accepted == 0:
        empty = Pop(
            t=pop.t + 1,
            n=0,
            ids=np.empty(0, dtype=np.uint64),
            sex=np.empty(0, dtype=np.uint8),
            qtl_auto=np.empty((0, cfg.k_a, 2)),
            qtl_x=np.empty((0, cfg.k_x, 2)),
            load=np.empty((0, cfg.n_load, 2), dtype=np.uint8),
            founder_qtl_auto=np.empty((0, cfg.k_a, 2), dtype=np.uint32),
            founder_qtl_x=np.empty((0, cfg.k_x, 2), dtype=np.uint32),
            founder_load=np.empty((0, cfg.n_load, 2), dtype=np.uint32),
            mother_id=np.empty(0, dtype=np.int64),
            father_id=np.empty(0, dtype=np.int64),
            matriline=np.empty(0, dtype=np.uint64),
            next_id=pop.next_id,
            next_founder=pop.next_founder,
        )
        return empty, np.empty(0, dtype=np.int64), np.empty(0, dtype=np.int32)

    fi, mi = pairing.female_idx, pairing.male_idx
    clutch = clutch_sizes(ph.fertility[fi], ph.fertility[mi], cfg)
    n_eggs = int(clutch.sum())
    if n_eggs == 0:
        empty = Pop(
            t=pop.t + 1,
            n=0,
            ids=np.empty(0, dtype=np.uint64),
            sex=np.empty(0, dtype=np.uint8),
            qtl_auto=np.empty((0, cfg.k_a, 2)),
            qtl_x=np.empty((0, cfg.k_x, 2)),
            load=np.empty((0, cfg.n_load, 2), dtype=np.uint8),
            founder_qtl_auto=np.empty((0, cfg.k_a, 2), dtype=np.uint32),
            founder_qtl_x=np.empty((0, cfg.k_x, 2), dtype=np.uint32),
            founder_load=np.empty((0, cfg.n_load, 2), dtype=np.uint32),
            mother_id=np.empty(0, dtype=np.int64),
            father_id=np.empty(0, dtype=np.int64),
            matriline=np.empty(0, dtype=np.uint64),
            next_id=pop.next_id,
            next_founder=pop.next_founder,
        )
        return empty, np.empty(0, dtype=np.int64), clutch

    pair_of = np.repeat(np.arange(fi.size), clutch)
    mom = np.repeat(fi, clutch)
    dad = np.repeat(mi, clutch)

    sex = rng.integers(0, 2, size=n_eggs, dtype=np.uint8)
    pick_m_a = rng.integers(0, 2, size=(n_eggs, cfg.k_a), dtype=np.int64)
    pick_d_a = rng.integers(0, 2, size=(n_eggs, cfg.k_a), dtype=np.int64)
    qtl_m = _take_hap(pop.qtl_auto, mom, pick_m_a)
    qtl_d = _take_hap(pop.qtl_auto, dad, pick_d_a)
    fnd_m = _take_hap(pop.founder_qtl_auto, mom, pick_m_a)
    fnd_d = _take_hap(pop.founder_qtl_auto, dad, pick_d_a)

    qtl_m = clip_qtl(qtl_m + rng.normal(0.0, cfg.sigma_mu, size=qtl_m.shape), cfg.z_max)
    qtl_d = clip_qtl(qtl_d + rng.normal(0.0, cfg.sigma_mu, size=qtl_d.shape), cfg.z_max)
    qtl_auto = np.stack([qtl_m, qtl_d], axis=2)
    founder_qtl_auto = np.stack([fnd_m, fnd_d], axis=2)

    pick_m_x = rng.integers(0, 2, size=(n_eggs, cfg.k_x), dtype=np.int64)
    # Father is hemizygous: always slot 0.
    pick_d_x = np.zeros((n_eggs, cfg.k_x), dtype=np.int64)
    x_from_mom = _take_hap(pop.qtl_x, mom, pick_m_x)
    x_from_dad = _take_hap(pop.qtl_x, dad, pick_d_x)
    fx_mom = _take_hap(pop.founder_qtl_x, mom, pick_m_x)
    fx_dad = _take_hap(pop.founder_qtl_x, dad, pick_d_x)
    x_from_mom = clip_qtl(x_from_mom + rng.normal(0.0, cfg.sigma_mu, size=x_from_mom.shape), cfg.z_max)
    x_from_dad = clip_qtl(x_from_dad + rng.normal(0.0, cfg.sigma_mu, size=x_from_dad.shape), cfg.z_max)

    qtl_x = np.zeros((n_eggs, cfg.k_x, 2), dtype=np.float64)
    founder_qtl_x = np.zeros((n_eggs, cfg.k_x, 2), dtype=np.uint32)
    daughters = sex == FEMALE
    sons = ~daughters
    qtl_x[daughters, :, 0] = x_from_mom[daughters]
    qtl_x[daughters, :, 1] = x_from_dad[daughters]
    founder_qtl_x[daughters, :, 0] = fx_mom[daughters]
    founder_qtl_x[daughters, :, 1] = fx_dad[daughters]
    qtl_x[sons, :, 0] = x_from_mom[sons]
    founder_qtl_x[sons, :, 0] = fx_mom[sons]

    pick_m_l = rng.integers(0, 2, size=(n_eggs, cfg.n_load), dtype=np.int64)
    pick_d_l = rng.integers(0, 2, size=(n_eggs, cfg.n_load), dtype=np.int64)
    load_m = _take_hap(pop.load, mom, pick_m_l).astype(np.uint8)
    load_d = _take_hap(pop.load, dad, pick_d_l).astype(np.uint8)
    fl_m = _take_hap(pop.founder_load, mom, pick_m_l)
    fl_d = _take_hap(pop.founder_load, dad, pick_d_l)

    mut_m = (load_m == 0) & (rng.random(load_m.shape) < cfg.u)
    mut_d = (load_d == 0) & (rng.random(load_d.shape) < cfg.u)
    load_m = np.where(mut_m, 1, load_m).astype(np.uint8)
    load_d = np.where(mut_d, 1, load_d).astype(np.uint8)
    n_mut = int(mut_m.sum() + mut_d.sum())
    new_ids = np.arange(pop.next_founder, pop.next_founder + n_mut, dtype=np.uint32)
    fl_m = fl_m.copy()
    fl_d = fl_d.copy()
    cursor = 0
    if mut_m.any():
        k = int(mut_m.sum())
        fl_m[mut_m] = new_ids[cursor : cursor + k]
        cursor += k
    if mut_d.any():
        k = int(mut_d.sum())
        fl_d[mut_d] = new_ids[cursor : cursor + k]
        cursor += k
    next_founder = pop.next_founder + n_mut
    load = np.stack([load_m, load_d], axis=2)
    founder_load = np.stack([fl_m, fl_d], axis=2)

    hits = np.flatnonzero(rng.random(n_eggs) < cfg.p_pleio)
    for i in hits:
        loci = rng.choice(cfg.k_a, size=min(cfg.pleio_n, cfg.k_a), replace=False)
        delta = rng.normal(0.0, cfg.pleio_sigma, size=loci.size)
        qtl_auto[i, loci, 0] = clip_qtl(qtl_auto[i, loci, 0] + delta, cfg.z_max)
        qtl_auto[i, loci, 1] = clip_qtl(qtl_auto[i, loci, 1] + delta, cfg.z_max)

    ids = np.arange(pop.next_id, pop.next_id + n_eggs, dtype=np.uint64)
    eggs = Pop(
        t=pop.t + 1,
        n=n_eggs,
        ids=ids,
        sex=sex,
        qtl_auto=qtl_auto,
        qtl_x=qtl_x,
        load=load,
        founder_qtl_auto=founder_qtl_auto.astype(np.uint32),
        founder_qtl_x=founder_qtl_x.astype(np.uint32),
        founder_load=founder_load.astype(np.uint32),
        mother_id=pop.ids[mom].astype(np.int64),
        father_id=pop.ids[dad].astype(np.int64),
        matriline=pop.matriline[mom],
        next_id=pop.next_id + n_eggs,
        next_founder=next_founder,
    )
    return eggs, pair_of, clutch
