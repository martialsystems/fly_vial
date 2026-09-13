# Copyright (c) 2026 Martial Systems LLC
"""Forced pairing: k-NN assortative, threshold, or random. Monogamy default."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import Phenotype, wing_match
from fly_vial.genome import FEMALE, MALE, Pop
from fly_vial.similarity import mating_traits, pairwise_fm_distance


@dataclass
class Pairing:
    female_idx: np.ndarray
    male_idx: np.ndarray
    distance: np.ndarray
    courtship: np.ndarray
    accepted: np.ndarray
    sterile: np.ndarray
    n_failed_match: int
    n_accepted: int
    n_sterile: int


def _legal_males(
    dist_row: np.ndarray,
    remaining: np.ndarray,
    cfg: RunConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    """Local male indices that are still legal and have capacity."""
    cap = remaining > 0
    if not np.any(cap):
        return np.empty(0, dtype=np.int64)
    if cfg.mating_mode == "random":
        return np.flatnonzero(cap)
    if cfg.mating_mode == "assortative_threshold":
        return np.flatnonzero(cap & (dist_row <= cfg.d_star))
    # assortative_knn
    k = min(int(cfg.k), dist_row.size)
    nearest = np.argpartition(dist_row, kth=k - 1)[:k]
    nearest = nearest[cap[nearest]]
    return nearest


def pair(pop: Pop, ph: Phenotype, cfg: RunConfig, rng: np.random.Generator, sigma0: np.ndarray) -> Pairing:
    f_idx = np.flatnonzero(pop.sex == FEMALE)
    m_idx = np.flatnonzero(pop.sex == MALE)
    empty = Pairing(
        female_idx=np.empty(0, dtype=np.int64),
        male_idx=np.empty(0, dtype=np.int64),
        distance=np.empty(0),
        courtship=np.empty(0),
        accepted=np.empty(0, dtype=bool),
        sterile=np.empty(0, dtype=bool),
        n_failed_match=int(f_idx.size),
        n_accepted=0,
        n_sterile=0,
    )
    if f_idx.size == 0 or m_idx.size == 0:
        return empty

    z = mating_traits(ph)
    dist = pairwise_fm_distance(z[f_idx], z[m_idx], sigma0)
    remaining = np.full(m_idx.size, cfg.m_max, dtype=np.int32)
    order = rng.permutation(f_idx.size)

    chosen_f: list[int] = []
    chosen_m: list[int] = []
    chosen_d: list[float] = []
    n_fail = 0

    for local_f in order:
        legal = _legal_males(dist[local_f], remaining, cfg, rng)
        if legal.size == 0:
            n_fail += 1
            continue
        if cfg.mating_mode == "random":
            pick = int(rng.choice(legal))
        else:
            pick = int(legal[np.argmin(dist[local_f, legal])])
        chosen_f.append(int(f_idx[local_f]))
        chosen_m.append(int(m_idx[pick]))
        chosen_d.append(float(dist[local_f, pick]))
        remaining[pick] -= 1

    if not chosen_f:
        return Pairing(
            female_idx=np.empty(0, dtype=np.int64),
            male_idx=np.empty(0, dtype=np.int64),
            distance=np.empty(0),
            courtship=np.empty(0),
            accepted=np.empty(0, dtype=bool),
            sterile=np.empty(0, dtype=bool),
            n_failed_match=n_fail,
            n_accepted=0,
            n_sterile=0,
        )

    fi = np.asarray(chosen_f, dtype=np.int64)
    mi = np.asarray(chosen_m, dtype=np.int64)
    d = np.asarray(chosen_d, dtype=np.float64)
    wm = wing_match(ph.wing_morph[mi], ph.wing_morph[fi], cfg.alpha)
    court = ph.song[mi] * ph.tracking[mi] * ph.receptivity[fi] * wm
    accepted = np.ones(fi.size, dtype=bool)
    if cfg.receptivity_filter:
        keep = court >= cfg.theta_rec
        n_fail += int((~keep).sum())
        fi, mi, d, court = fi[keep], mi[keep], d[keep], court[keep]
        accepted = np.ones(fi.size, dtype=bool)

    sterile = (ph.fertility[fi] * ph.fertility[mi]) <= 0.0
    return Pairing(
        female_idx=fi,
        male_idx=mi,
        distance=d,
        courtship=court,
        accepted=accepted,
        sterile=sterile,
        n_failed_match=n_fail,
        n_accepted=int(fi.size),
        n_sterile=int(sterile.sum()),
    )
