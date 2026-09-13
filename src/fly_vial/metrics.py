# Copyright (c) 2026 Martial Systems LLC
"""Generation census: kinship, heterozygosity, clusters, Ne."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fly_vial.config import RunConfig
from fly_vial.fitness import Phenotype
from fly_vial.genome import FEMALE, MALE, Pop
from fly_vial.mating import Pairing
from fly_vial.similarity import mating_traits, pairwise_fm_distance


def mean_pairwise_phi(founder: np.ndarray) -> float:
    """Mean kinship over unordered pairs from autosomal QTL founder IDs."""
    n, k, _ = founder.shape
    if n < 2 or k == 0:
        return 0.0
    acc = np.zeros((n, n), dtype=np.float64)
    for loc in range(k):
        mat = founder[:, loc, 0]
        pat = founder[:, loc, 1]
        acc += (mat[:, None] == mat[None, :]).astype(np.float64)
        acc += (mat[:, None] == pat[None, :]).astype(np.float64)
        acc += (pat[:, None] == mat[None, :]).astype(np.float64)
        acc += (pat[:, None] == pat[None, :]).astype(np.float64)
    acc *= 0.25 / k
    iu = np.triu_indices(n, k=1)
    return float(acc[iu].mean())


def heterozygosity_qtl(pop: Pop) -> float:
    if pop.n == 0:
        return 0.0
    return float((pop.founder_qtl_auto[:, :, 0] != pop.founder_qtl_auto[:, :, 1]).mean())


def heterozygosity_load(pop: Pop) -> float:
    if pop.n == 0:
        return 0.0
    return float((pop.load[:, :, 0] != pop.load[:, :, 1]).mean())


class _UF:
    def __init__(self, n: int) -> None:
        self.p = np.arange(n)

    def find(self, x: int) -> int:
        p = self.p
        while p[x] != x:
            p[x] = p[p[x]]
            x = int(p[x])
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def both_sex_clusters(
    pop: Pop, ph: Phenotype, sigma0: np.ndarray, d_cluster: float
) -> list[np.ndarray]:
    if pop.n == 0:
        return []
    f_idx = np.flatnonzero(pop.sex == FEMALE)
    m_idx = np.flatnonzero(pop.sex == MALE)
    if f_idx.size == 0 or m_idx.size == 0:
        return []
    z = mating_traits(ph)
    dist = pairwise_fm_distance(z[f_idx], z[m_idx], sigma0)
    uf = _UF(pop.n)
    ii, jj = np.where(dist < d_cluster)
    for a, b in zip(f_idx[ii], m_idx[jj], strict=False):
        uf.union(int(a), int(b))
    buckets: dict[int, list[int]] = {}
    for i in range(pop.n):
        buckets.setdefault(uf.find(i), []).append(i)
    out: list[np.ndarray] = []
    for members in buckets.values():
        arr = np.asarray(members, dtype=np.int64)
        if np.any(pop.sex[arr] == FEMALE) and np.any(pop.sex[arr] == MALE):
            out.append(arr)
    return out


def n_extinct_clusters(
    prev_matrilines: list[frozenset[int]],
    pop: Pop,
) -> int:
    if not prev_matrilines or pop.n == 0:
        return len(prev_matrilines)
    alive_f = set(int(x) for x in pop.matriline[pop.sex == FEMALE])
    alive_m = set(int(x) for x in pop.matriline[pop.sex == MALE])
    n = 0
    for s in prev_matrilines:
        if s.isdisjoint(alive_f) or s.isdisjoint(alive_m):
            n += 1
    return n


@dataclass
class GenerationRecord:
    payload: dict


def record_generation(
    pop: Pop,
    ph: Phenotype,
    pairing: Pairing | None,
    cfg: RunConfig,
    sigma0: np.ndarray,
    h0_qtl: float,
    prev_matrilines: list[frozenset[int]],
    egg_viability_mean: float,
    egg_survival_rate: float,
    n_eggs: int,
    n_viable: int,
    family_k: np.ndarray | None,
    n_eval_hook: int,
) -> tuple[dict, list[frozenset[int]]]:
    n_f = int(np.sum(pop.sex == FEMALE))
    n_m = int(np.sum(pop.sex == MALE))
    extinct = pop.n == 0 or n_f == 0 or n_m == 0
    h_qtl = heterozygosity_qtl(pop)
    f_t = 0.0 if h0_qtl <= 0 else 1.0 - (h_qtl / h0_qtl)
    clusters = both_sex_clusters(pop, ph, sigma0, cfg.d_cluster)
    mats = [frozenset(int(x) for x in pop.matriline[c]) for c in clusters]
    n_ext = n_extinct_clusters(prev_matrilines, pop)

    court_mean = float(pairing.courtship.mean()) if pairing is not None and pairing.n_accepted else 0.0
    sim_mean = float(pairing.distance.mean()) if pairing is not None and pairing.n_accepted else 0.0
    n_acc = 0 if pairing is None else pairing.n_accepted
    n_fail = 0 if pairing is None else pairing.n_failed_match
    n_ster = 0 if pairing is None else pairing.n_sterile

    ne_simple = 0.0
    ne_hat = 0.0
    if n_acc and pairing is not None:
        n_pf = int(len(set(pairing.female_idx.tolist())))
        n_pm = int(len(set(pairing.male_idx.tolist())))
        if n_pf + n_pm > 0:
            ne_simple = 4.0 * n_pf * n_pm / (n_pf + n_pm)
            ne_hat = ne_simple
            if family_k is not None and family_k.size:
                kbar = float(family_k.mean())
                vk = float(family_k.var())
                if kbar > 0:
                    ne_hat = ne_simple / (1.0 + vk / kbar)

    trait_names = [
        "song",
        "tracking",
        "receptivity",
        "locomotion",
        "body_size",
        "wing_morph",
        "fa",
        "fertility",
        "viability",
        "d_template",
    ]
    trait_mean = {}
    trait_var = {}
    for name in trait_names:
        arr = getattr(ph, name)
        trait_mean[name] = float(arr.mean()) if pop.n else 0.0
        trait_var[name] = float(arr.var()) if pop.n else 0.0

    rec = {
        "t": pop.t,
        "n": pop.n,
        "n_female": n_f,
        "n_male": n_m,
        "n_accepted": n_acc,
        "n_failed_match": n_fail,
        "n_sterile": n_ster,
        "n_eggs": n_eggs,
        "n_viable": n_viable,
        "trait_mean": trait_mean,
        "trait_var": trait_var,
        "mean_pairwise_phi": mean_pairwise_phi(pop.founder_qtl_auto) if pop.n else 0.0,
        "mean_similarity": sim_mean,
        "heterozygosity_qtl": h_qtl,
        "heterozygosity_load": heterozygosity_load(pop),
        "F": f_t,
        "cluster_count": len(clusters),
        "matriline_count": int(len(set(int(x) for x in pop.matriline))) if pop.n else 0,
        "n_extinct_clusters": n_ext,
        "extinct": extinct,
        "fitness_components": {
            "viability": egg_viability_mean,
            "viability_adult": trait_mean["viability"],
            "fertility": trait_mean["fertility"],
            "courtship": court_mean,
            "locomotion": trait_mean["locomotion"],
            "fa": trait_mean["fa"],
            "d_template": trait_mean["d_template"],
            "egg_survival_rate": egg_survival_rate,
        },
        "Ne_simple": ne_simple,
        "Ne_hat": ne_hat,
        "n_eval_hook": n_eval_hook,
        "n_deformed": int(ph.deformed.sum()) if pop.n else 0,
    }
    return rec, mats
