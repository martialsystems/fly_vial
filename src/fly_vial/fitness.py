# Copyright (c) 2026 Martial Systems LLC
"""Load, template, circuit competence, viability, fertility, deformation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.genome import (
    I_BODY,
    I_FA,
    I_FERT,
    I_LOCO,
    I_RECEPT_PC1,
    I_RECEPT_VPODN,
    I_SONG_CPG,
    I_SONG_P1,
    I_SONG_PIP10,
    I_STAB,
    I_TRACK,
    I_WING,
    S_AUTO,
    X_LOCO,
    X_RECEPT,
    X_SONG,
    X_TRACK,
    Pop,
    additive_z,
)


def g_circuit(x: np.ndarray, alpha: float) -> np.ndarray:
    return np.exp(-alpha * np.square(x))


def load_weights(load: np.ndarray, cfg: RunConfig) -> np.ndarray:
    """Per-locus fitness contribution. Shape (n, L). h = 0: heterozygotes are 1."""
    hom = (load[:, :, 0] == 1) & (load[:, :, 1] == 1)
    w = np.ones(load.shape[:2], dtype=np.float64)
    n_let = cfg.n_lethal
    w[:, :n_let] = np.where(hom[:, :n_let], 1.0 - cfg.s_let, 1.0)
    w[:, n_let:] = np.where(hom[:, n_let:], 1.0 - cfg.s_sub, 1.0)
    return w


@dataclass
class Phenotype:
    z: np.ndarray
    song: np.ndarray
    tracking: np.ndarray
    receptivity: np.ndarray
    locomotion: np.ndarray
    body_size: np.ndarray
    wing_morph: np.ndarray
    fa: np.ndarray
    fertility: np.ndarray
    viability: np.ndarray
    v_load: np.ndarray
    d_template: np.ndarray
    n_load_hom: np.ndarray
    n_load_het: np.ndarray
    het_qtl: np.ndarray
    deformed: np.ndarray


def phenotype(pop: Pop, cfg: RunConfig, h0_qtl: float | None = None) -> Phenotype:
    z = additive_z(pop)
    k_a = cfg.k_a
    z_x = z[:, k_a:]
    w = load_weights(pop.load, cfg)
    v_load = w.prod(axis=1)
    d_template = np.sqrt(np.square(z).sum(axis=1))
    v_template = np.exp(-cfg.beta * np.square(d_template))

    het_ibd = pop.founder_qtl_auto[:, :, 0] != pop.founder_qtl_auto[:, :, 1]
    het_qtl = het_ibd.mean(axis=1)
    href = 1.0 if h0_qtl is None or h0_qtl <= 0 else h0_qtl
    f_ind = 1.0 - (het_qtl / href)
    stab = np.maximum(z[:, I_STAB], -0.9)
    fa = np.abs(z[:, I_FA]) * (1.0 + cfg.gamma * f_ind) * (1.0 / (1.0 + stab))
    v_dev = 1.0 / (1.0 + cfg.kappa * fa)

    song = (
        g_circuit(z[:, I_SONG_P1], cfg.alpha)
        * g_circuit(z[:, I_SONG_PIP10], cfg.alpha)
        * g_circuit(z[:, I_SONG_CPG], cfg.alpha)
        * g_circuit(z_x[:, X_SONG], cfg.alpha)
        * v_load
        * v_dev
    )
    tracking = (
        g_circuit(z[:, I_TRACK], cfg.alpha)
        * g_circuit(z_x[:, X_TRACK], cfg.alpha)
        * v_load
        * v_dev
    )
    receptivity = (
        g_circuit(z[:, I_RECEPT_PC1], cfg.alpha)
        * g_circuit(z[:, I_RECEPT_VPODN], cfg.alpha)
        * g_circuit(z_x[:, X_RECEPT], cfg.alpha)
        * v_load
        * v_dev
    )
    locomotion = (
        g_circuit(z[:, I_LOCO], cfg.alpha)
        * g_circuit(z_x[:, X_LOCO], cfg.alpha)
        * v_load
        * v_dev
    )
    fertility = g_circuit(z[:, I_FERT], cfg.alpha) * v_load
    viability = v_load * v_template * locomotion * v_dev
    viability = np.clip(viability, 0.0, 1.0)
    fertility = np.clip(fertility, 0.0, 1.0)

    hom = (pop.load[:, :, 0] == 1) & (pop.load[:, :, 1] == 1)
    het = pop.load[:, :, 0] != pop.load[:, :, 1]
    n_hom = hom.sum(axis=1).astype(np.int32)
    n_het = het.sum(axis=1).astype(np.int32)

    sigma0_placeholder = cfg.sigma_init
    extreme = np.zeros(pop.n, dtype=bool)
    for idx in S_AUTO:
        extreme |= np.abs(z[:, idx]) > (3.0 * sigma0_placeholder)

    collapsed = (
        (song < cfg.eps_circuit)
        | (tracking < cfg.eps_circuit)
        | (receptivity < cfg.eps_circuit)
        | (locomotion < cfg.eps_circuit)
    )
    deformed = (viability <= 0.0) | (fertility <= 0.0) | extreme | collapsed

    return Phenotype(
        z=z,
        song=song,
        tracking=tracking,
        receptivity=receptivity,
        locomotion=locomotion,
        body_size=z[:, I_BODY],
        wing_morph=z[:, I_WING],
        fa=fa,
        fertility=fertility,
        viability=viability,
        v_load=v_load,
        d_template=d_template,
        n_load_hom=n_hom,
        n_load_het=n_het,
        het_qtl=het_qtl,
        deformed=deformed,
    )


def clutch_sizes(fert_f: np.ndarray, fert_m: np.ndarray, cfg: RunConfig) -> np.ndarray:
    return np.maximum(0, np.rint(cfg.c0 * fert_f * fert_m)).astype(np.int32)


def wing_match(wing_m: np.ndarray, wing_f: np.ndarray, alpha: float) -> np.ndarray:
    return g_circuit(wing_m - wing_f, alpha)
