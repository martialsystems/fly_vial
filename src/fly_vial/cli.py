# Copyright (c) 2026 Martial Systems LLC
"""CLI for the closed-vial population."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from fly_vial.claims import require_clean
from fly_vial.config import RunConfig
from fly_vial.paths import LOGS, REPO
from fly_vial.population import run_generations, write_run
from vialforge.gate import require_readme_clean

BANNER = (
    "Closed vial. Assortative pairing. Recessive load. Connectome templates."
)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="fly-vial", description=BANNER)
    sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="run a closed-vial experiment")
    run.add_argument("--arm", default="assortative", choices=["assortative", "random"])
    run.add_argument("--mode", default="knn", choices=["knn", "threshold", "random"])
    run.add_argument("--k", type=int, default=3)
    run.add_argument("--d-star", type=float, default=2.5)
    run.add_argument("--generations", type=int, default=80)
    run.add_argument("--n", type=int, default=1000)
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--out", type=Path, default=LOGS / "run.json")
    run.add_argument("--eval-connectome", action="store_true")
    run.add_argument("--receptivity-filter", action="store_true")
    run.add_argument("--cap", choices=["on", "off"], default="on")
    run.add_argument("--blocks", action="store_true")
    return p


def _mode_name(arm: str, mode: str) -> str:
    if arm == "random" or mode == "random":
        return "random"
    if mode == "threshold":
        return "assortative_threshold"
    return "assortative_knn"


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    require_clean(BANNER, source="banner")
    readme = REPO / "README.md"
    if readme.is_file():
        require_readme_clean(readme.read_text(encoding="utf-8"))
        require_clean(readme.read_text(encoding="utf-8"), source="README.md")
    cfg = RunConfig(
        n=args.n,
        generations=args.generations,
        seed=args.seed,
        mating_mode=_mode_name(args.arm, args.mode),
        k=args.k,
        d_star=args.d_star,
        eval_connectome=bool(args.eval_connectome),
        receptivity_filter=bool(args.receptivity_filter),
        arm=args.arm,
        cap=args.cap,
        blocks=bool(args.blocks),
        n_ceiling=args.n,
        fail_t_max=max(args.generations, 200) if args.cap == "off" else 200,
    )
    result = run_generations(cfg)
    write_run(result, args.out)
    last = result["generations"][-1]
    print(
        f"t={last['t']} n={last['n']} F={last['F']:.4f} "
        f"phi={last['mean_pairwise_phi']:.4f} "
        f"viability={last['fitness_components']['viability']:.4f} "
        f"T_fail={result['T_fail']} rule={result['fail_rule']} "
        f"cap={cfg.cap} extinct={last['extinct']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
