# Copyright (c) 2026 Martial Systems LLC
"""Diploid genome layout, initialization, and additive mapping."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fly_vial.config import RunConfig

FEMALE = 0
MALE = 1

QTL_AUTO = (
    "syn_gain_global",
    "syn_jitter",
    "song_P1",
    "song_pIP10",
    "song_CPG",
    "track_LC10",
    "aggr_P1",
    "loco_DN",
    "recept_pC1",
    "recept_vpoDN",
    "body_size",
    "wing_morph",
    "fa_tendency",
    "fertility",
    "stability",
    "celltype_gain_fru",
)

QTL_X = ("x_song_mod", "x_track_mod", "x_recept_mod", "x_loco_mod")

I_SYN_GAIN = 0
I_SYN_JITTER = 1
I_SONG_P1 = 2
I_SONG_PIP10 = 3
I_SONG_CPG = 4
I_TRACK = 5
I_AGGR = 6
I_LOCO = 7
I_RECEPT_PC1 = 8
I_RECEPT_VPODN = 9
I_BODY = 10
I_WING = 11
I_FA = 12
I_FERT = 13
I_STAB = 14
I_FRU = 15

X_SONG = 0
X_TRACK = 1
X_RECEPT = 2
X_LOCO = 3

# Mating similarity subset S: morphology + courtship-circuit QTLs. Not load, fertility, FA.
S_AUTO = (
    I_BODY,
    I_WING,
    I_SONG_P1,
    I_SONG_PIP10,
    I_SONG_CPG,
    I_TRACK,
    I_RECEPT_PC1,
    I_RECEPT_VPODN,
)


@dataclass
class Pop:
    t: int
    n: int
    ids: np.ndarray
    sex: np.ndarray
    qtl_auto: np.ndarray
    qtl_x: np.ndarray
    load: np.ndarray
    founder_qtl_auto: np.ndarray
    founder_qtl_x: np.ndarray
    founder_load: np.ndarray
    mother_id: np.ndarray
    father_id: np.ndarray
    matriline: np.ndarray
    next_id: int
    next_founder: int


def clip_qtl(arr: np.ndarray, z_max: float) -> np.ndarray:
    return np.clip(arr, -z_max, z_max)


def additive_z(pop: Pop) -> np.ndarray:
    """Autosomal mean of two alleles; X: female mean, male slot 0."""
    z_auto = pop.qtl_auto.mean(axis=2)
    z_x = np.empty((pop.n, pop.qtl_x.shape[1]), dtype=np.float64)
    female = pop.sex == FEMALE
    z_x[female] = pop.qtl_x[female].mean(axis=2)
    z_x[~female] = pop.qtl_x[~female, :, 0]
    return np.concatenate([z_auto, z_x], axis=1)


def draw_sex(n: int, cfg: RunConfig, rng: np.random.Generator) -> np.ndarray:
    sex = np.zeros(n, dtype=np.uint8)
    for _ in range(200):
        sex = (rng.random(n) >= cfg.p_female).astype(np.uint8)
        nf = int(np.sum(sex == FEMALE))
        if abs(nf - (n - nf)) <= cfg.sex_imbalance_max:
            return sex
    return sex


def init_population(cfg: RunConfig, rng: np.random.Generator) -> Pop:
    n = cfg.n
    k_a, k_x, l = cfg.k_a, cfg.k_x, cfg.n_load
    sex = draw_sex(n, cfg, rng)
    qtl_auto = clip_qtl(rng.normal(0.0, cfg.sigma_init, size=(n, k_a, 2)), cfg.z_max)
    qtl_x = clip_qtl(rng.normal(0.0, cfg.sigma_init, size=(n, k_x, 2)), cfg.z_max)
    qtl_x[sex == MALE, :, 1] = 0.0
    load = np.zeros((n, l, 2), dtype=np.uint8)
    for i in range(n):
        n_het = int(rng.poisson(cfg.lambda_init))
        n_het = min(max(n_het, 0), l)
        if n_het == 0:
            continue
        loci = rng.choice(l, size=n_het, replace=False)
        hap = rng.integers(0, 2, size=n_het)
        load[i, loci, hap] = 1

    n_f_auto = n * k_a * 2
    n_f_x = n * k_x * 2
    n_f_load = n * l * 2
    founder_qtl_auto = np.arange(1, 1 + n_f_auto, dtype=np.uint32).reshape(n, k_a, 2)
    founder_qtl_x = np.arange(
        1 + n_f_auto, 1 + n_f_auto + n_f_x, dtype=np.uint32
    ).reshape(n, k_x, 2)
    founder_qtl_x[sex == MALE, :, 1] = 0
    founder_load = np.arange(
        1 + n_f_auto + n_f_x,
        1 + n_f_auto + n_f_x + n_f_load,
        dtype=np.uint32,
    ).reshape(n, l, 2)
    ids = np.arange(n, dtype=np.uint64)
    mother = np.full(n, -1, dtype=np.int64)
    father = np.full(n, -1, dtype=np.int64)
    matriline = ids.copy()
    next_founder = int(1 + n_f_auto + n_f_x + n_f_load)
    return Pop(
        t=0,
        n=n,
        ids=ids,
        sex=sex,
        qtl_auto=qtl_auto,
        qtl_x=qtl_x,
        load=load,
        founder_qtl_auto=founder_qtl_auto,
        founder_qtl_x=founder_qtl_x,
        founder_load=founder_load,
        mother_id=mother,
        father_id=father,
        matriline=matriline,
        next_id=n,
        next_founder=next_founder,
    )
