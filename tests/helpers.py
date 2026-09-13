# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.genome import Pop


def one_fly(*, sex: int, load_hom_lethal: bool = False, cfg: RunConfig | None = None) -> Pop:
    cfg = cfg or RunConfig(n=1)
    load = np.zeros((1, cfg.n_load, 2), dtype=np.uint8)
    if load_hom_lethal:
        load[0, 0, :] = 1
    qtl_auto = np.zeros((1, cfg.k_a, 2))
    qtl_x = np.zeros((1, cfg.k_x, 2))
    return Pop(
        t=0,
        n=1,
        ids=np.array([0], dtype=np.uint64),
        sex=np.array([sex], dtype=np.uint8),
        qtl_auto=qtl_auto,
        qtl_x=qtl_x,
        load=load,
        founder_qtl_auto=np.array([[[1, 2]] * cfg.k_a], dtype=np.uint32),
        founder_qtl_x=np.array([[[3, 4]] * cfg.k_x], dtype=np.uint32),
        founder_load=np.arange(10, 10 + cfg.n_load * 2, dtype=np.uint32).reshape(1, cfg.n_load, 2),
        mother_id=np.array([-1], dtype=np.int64),
        father_id=np.array([-1], dtype=np.int64),
        matriline=np.array([0], dtype=np.uint64),
        next_id=1,
        next_founder=10 + cfg.n_load * 2,
    )
