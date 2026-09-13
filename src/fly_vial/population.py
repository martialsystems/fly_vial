# Copyright (c) 2026 Martial Systems LLC
"""Non-overlapping generation loop, viability filter, density cap."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.eval_connectome import eval_accepted_pairs
from fly_vial.fitness import phenotype
from fly_vial.genome import FEMALE, MALE, Pop, init_population
from fly_vial.inheritance import meiosis_mutate
from fly_vial.mating import pair
from fly_vial.metrics import heterozygosity_qtl, record_generation
from fly_vial.similarity import freeze_sigma0, mating_traits
from fly_vial.templates import assert_template_counts
from vialforge.gate import (
    FLYWIRE_N,
    MALECNS_N,
    require_closed_vial,
    require_engine,
    require_load,
    require_templates,
)


def _subset(pop: Pop, idx: np.ndarray) -> Pop:
    if idx.size == 0:
        return Pop(
            t=pop.t,
            n=0,
            ids=np.empty(0, dtype=np.uint64),
            sex=np.empty(0, dtype=np.uint8),
            qtl_auto=np.empty((0, pop.qtl_auto.shape[1], 2)),
            qtl_x=np.empty((0, pop.qtl_x.shape[1], 2)),
            load=np.empty((0, pop.load.shape[1], 2), dtype=np.uint8),
            founder_qtl_auto=np.empty((0, pop.founder_qtl_auto.shape[1], 2), dtype=np.uint32),
            founder_qtl_x=np.empty((0, pop.founder_qtl_x.shape[1], 2), dtype=np.uint32),
            founder_load=np.empty((0, pop.founder_load.shape[1], 2), dtype=np.uint32),
            mother_id=np.empty(0, dtype=np.int64),
            father_id=np.empty(0, dtype=np.int64),
            matriline=np.empty(0, dtype=np.uint64),
            next_id=pop.next_id,
            next_founder=pop.next_founder,
        )
    return Pop(
        t=pop.t,
        n=int(idx.size),
        ids=pop.ids[idx],
        sex=pop.sex[idx],
        qtl_auto=pop.qtl_auto[idx],
        qtl_x=pop.qtl_x[idx],
        load=pop.load[idx],
        founder_qtl_auto=pop.founder_qtl_auto[idx],
        founder_qtl_x=pop.founder_qtl_x[idx],
        founder_load=pop.founder_load[idx],
        mother_id=pop.mother_id[idx],
        father_id=pop.father_id[idx],
        matriline=pop.matriline[idx],
        next_id=pop.next_id,
        next_founder=pop.next_founder,
    )


def cap_uniform(eggs: Pop, n_cap: int, rng: np.random.Generator) -> Pop:
    if eggs.n <= n_cap:
        return eggs
    idx = rng.choice(eggs.n, size=n_cap, replace=False)
    idx.sort()
    return _subset(eggs, idx)


def run_generations(cfg: RunConfig, rng: np.random.Generator | None = None) -> dict:
    require_closed_vial()
    require_engine(
        eval_n=0 if not cfg.eval_connectome else min(cfg.eval_pairs * 2, cfg.eval_n_max),
        eval_n_max=cfg.eval_n_max,
        eval_whole_population=False,
        eval_as_default_engine=False,
    )
    require_load(n_load=cfg.n_load, s_let=cfg.s_let, beta=cfg.beta, kappa=cfg.kappa)
    assert_template_counts()
    require_templates(female_n=FLYWIRE_N, male_n=MALECNS_N)

    rng = rng or np.random.default_rng(cfg.seed)
    pop = init_population(cfg, rng)
    ph = phenotype(pop, cfg)
    sigma0 = freeze_sigma0(mating_traits(ph), cfg)
    h0 = heterozygosity_qtl(pop)
    ph = phenotype(pop, cfg, h0_qtl=h0)

    records: list[dict] = []
    prev_mats: list[frozenset[int]] = []
    rec0, prev_mats = record_generation(
        pop,
        ph,
        pairing=None,
        cfg=cfg,
        sigma0=sigma0,
        h0_qtl=h0,
        prev_matrilines=[],
        egg_viability_mean=float(ph.viability.mean()),
        egg_survival_rate=1.0,
        n_eggs=pop.n,
        n_viable=pop.n,
        family_k=None,
        n_eval_hook=0,
    )
    records.append(rec0)

    last_hook: list[dict] = []

    for _step in range(cfg.generations):
        n_f = int(np.sum(pop.sex == FEMALE))
        n_m = int(np.sum(pop.sex == MALE))
        if pop.n == 0 or n_f == 0 or n_m == 0:
            records[-1]["extinct"] = True
            break
        pairing = pair(pop, ph, cfg, rng, sigma0)
        eggs, _pair_of, clutch = meiosis_mutate(pop, ph, pairing, cfg, rng)
        n_eggs = eggs.n
        if n_eggs == 0:
            pop = _subset(eggs, np.empty(0, dtype=np.int64))
            ph = phenotype(pop, cfg, h0_qtl=h0)
            rec, prev_mats = record_generation(
                pop,
                ph,
                pairing,
                cfg,
                sigma0,
                h0,
                prev_mats,
                egg_viability_mean=0.0,
                egg_survival_rate=0.0,
                n_eggs=0,
                n_viable=0,
                family_k=None,
                n_eval_hook=0,
            )
            records.append(rec)
            break
        egg_ph = phenotype(eggs, cfg, h0_qtl=h0)
        survive = rng.random(eggs.n) < egg_ph.viability
        n_viable = int(survive.sum())
        live = _subset(eggs, np.flatnonzero(survive))
        nxt = cap_uniform(live, cfg.n, rng)

        parent_f_ids = pop.ids[pairing.female_idx] if pairing.n_accepted else np.empty(0, dtype=np.uint64)
        parent_m_ids = pop.ids[pairing.male_idx] if pairing.n_accepted else np.empty(0, dtype=np.uint64)
        k = np.zeros(pairing.n_accepted, dtype=np.float64)
        if pairing.n_accepted and nxt.n:
            for i, (pf, pm) in enumerate(zip(parent_f_ids, parent_m_ids, strict=True)):
                k[i] = float(np.sum((nxt.mother_id == int(pf)) & (nxt.father_id == int(pm))))

        n_eval = 0
        hook_rows: list[dict] = []
        if cfg.eval_connectome and pairing.n_accepted:
            hook_rows = eval_accepted_pairs(pop, ph, pairing, cfg, rng)
            n_eval = 2 * len(hook_rows)
            last_hook = hook_rows

        pop = nxt
        ph = phenotype(pop, cfg, h0_qtl=h0)
        rec, prev_mats = record_generation(
            pop,
            ph,
            pairing,
            cfg,
            sigma0,
            h0,
            prev_mats,
            egg_viability_mean=float(egg_ph.viability.mean()),
            egg_survival_rate=(n_viable / n_eggs) if n_eggs else 0.0,
            n_eggs=n_eggs,
            n_viable=n_viable,
            family_k=k,
            n_eval_hook=n_eval,
        )
        records.append(rec)
        if rec["extinct"]:
            break

    return {
        "config": cfg.payload(),
        "h0_qtl": h0,
        "sigma0": sigma0.tolist(),
        "generations": records,
        "eval_hook": last_hook,
        "n_eval_hook_total": int(sum(r["n_eval_hook"] for r in records)),
        "final_t": records[-1]["t"] if records else 0,
        "extinct": bool(records[-1]["extinct"]) if records else True,
    }


def write_run(result: dict, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    csv_path = out.with_suffix(".csv")
    gens = result["generations"]
    keys = [
        "t",
        "n",
        "n_female",
        "n_male",
        "n_accepted",
        "n_failed_match",
        "n_sterile",
        "n_eggs",
        "n_viable",
        "mean_pairwise_phi",
        "heterozygosity_qtl",
        "F",
        "cluster_count",
        "matriline_count",
        "n_extinct_clusters",
        "Ne_hat",
        "n_eval_hook",
    ]
    lines = [",".join(keys + ["viability", "fertility", "courtship", "locomotion"])]
    for g in gens:
        fc = g["fitness_components"]
        row = [g[k] for k in keys] + [
            fc["viability"],
            fc["fertility"],
            fc["courtship"],
            fc["locomotion"],
        ]
        lines.append(",".join(str(x) for x in row))
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
