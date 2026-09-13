# Copyright (c) 2026 Martial Systems LLC
"""Standardized Euclidean distance on the mating subset S."""

from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import Phenotype
from fly_vial.genome import S_AUTO


def mating_traits(ph: Phenotype) -> np.ndarray:
    return ph.z[:, list(S_AUTO)]


def freeze_sigma0(traits: np.ndarray, cfg: RunConfig) -> np.ndarray:
    sd = traits.std(axis=0, ddof=1) if traits.shape[0] > 1 else np.full(traits.shape[1], cfg.sigma_init)
    sd = np.where(sd <= 1e-12, cfg.sigma_init, sd)
    return sd.astype(np.float64)


def pairwise_fm_distance(z_f: np.ndarray, z_m: np.ndarray, sigma0: np.ndarray) -> np.ndarray:
    """(n_f, n_m) standardized Euclidean distances."""
    delta = (z_f[:, None, :] - z_m[None, :, :]) / sigma0[None, None, :]
    return np.sqrt(np.square(delta).sum(axis=2))
