# Copyright (c) 2026 Martial Systems LLC
"""Run hyperparameters."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RunConfig:
    n: int = 1000
    generations: int = 80
    seed: int = 1
    p_female: float = 0.5
    sex_imbalance_max: int = 50
    k_a: int = 16
    k_x: int = 4
    n_load: int = 64
    n_lethal: int = 16
    s_let: float = 1.0
    s_sub: float = 0.25
    h_load: float = 0.0
    lambda_init: float = 4.0
    sigma_init: float = 0.05
    z_max: float = 2.0
    sigma_mu: float = 0.02
    p_pleio: float = 1e-3
    pleio_sigma: float = 0.3
    pleio_n: int = 3
    u: float = 0.002
    beta: float = 0.15
    alpha: float = 2.0
    kappa: float = 0.5
    gamma: float = 1.0
    eps_circuit: float = 0.05
    c0: float = 8.0
    mating_mode: str = "assortative_knn"
    k: int = 3
    d_star: float = 2.5
    d_cluster: float = 2.0
    m_max: int = 1
    receptivity_filter: bool = False
    theta_rec: float = 0.05
    eval_connectome: bool = False
    eval_n_max: int = 8
    eval_pairs: int = 4
    arm: str = "assortative"
    cap: str = "on"
    blocks: bool = False
    n_ceiling: int = 1000
    fail_n_min: int = 50
    fail_viability: float = 0.20
    fail_t_max: int = 200

    def payload(self) -> dict:
        return asdict(self)
