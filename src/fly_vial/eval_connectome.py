# Copyright (c) 2026 Martial Systems LLC
"""Optional reduced-circuit audit hook. Not the population engine."""

from __future__ import annotations

import json

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import Phenotype
from fly_vial.genome import (
    I_RECEPT_PC1,
    I_SONG_P1,
    I_SYN_GAIN,
    I_SYN_JITTER,
    I_TRACK,
    Pop,
)
from fly_vial.mating import Pairing
from fly_vial.paths import TEMPLATES
from vialforge.gate import require_engine


def _softplus(x: np.ndarray) -> np.ndarray:
    return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0.0)


def load_fixture() -> dict:
    return json.loads((TEMPLATES / "fixture_subgraph.json").read_text(encoding="utf-8"))


def rate_model(z_row: np.ndarray, rng: np.random.Generator, steps: int = 50) -> dict:
    spec = load_fixture()
    w = np.asarray(spec["W"], dtype=np.float64)
    cells = spec["cells"]
    gain = float(np.exp(z_row[I_SYN_GAIN]))
    jitter = float(_softplus(np.asarray([z_row[I_SYN_JITTER]]))[0])
    noise = rng.normal(0.0, jitter, size=w.shape)
    w_mod = w * gain + noise
    excit = np.ones(w.shape[0])
    name_gain = {
        "P1": z_row[I_SONG_P1],
        "pC1": z_row[I_RECEPT_PC1],
        "LC10a": z_row[I_TRACK],
        "LC10": z_row[I_TRACK],
    }
    for i, name in enumerate(cells):
        if name in name_gain:
            excit[i] *= float(np.exp(name_gain[name]))
    i_ext = 0.5 * excit
    r = np.zeros(w.shape[0])
    for _ in range(steps):
        r = np.tanh(w_mod @ r + i_ext)
    out = {}
    for key, names in spec["readouts"].items():
        idx = [cells.index(nm) for nm in names]
        out[key] = float(np.mean(np.abs(r[idx])))
    return out


def eval_accepted_pairs(
    pop: Pop,
    ph: Phenotype,
    pairing: Pairing,
    cfg: RunConfig,
    rng: np.random.Generator,
) -> list[dict]:
    n_pairs = min(int(cfg.eval_pairs), int(pairing.n_accepted), cfg.eval_n_max // 2)
    n_eval = n_pairs * 2
    require_engine(
        eval_n=n_eval,
        eval_n_max=cfg.eval_n_max,
        eval_whole_population=False,
        eval_as_default_engine=False,
    )
    if n_pairs <= 0:
        return []
    pick = rng.choice(pairing.n_accepted, size=n_pairs, replace=False)
    rows = []
    for p in pick:
        fi = int(pairing.female_idx[p])
        mi = int(pairing.male_idx[p])
        male_scores = rate_model(ph.z[mi], rng)
        female_scores = rate_model(ph.z[fi], rng)
        rows.append(
            {
                "female_id": int(pop.ids[fi]),
                "male_id": int(pop.ids[mi]),
                "closed_form_courtship": float(pairing.courtship[p]),
                "hook_song": male_scores["song"],
                "hook_tracking": male_scores["tracking"],
                "hook_receptivity": female_scores["receptivity"],
            }
        )
    return rows
