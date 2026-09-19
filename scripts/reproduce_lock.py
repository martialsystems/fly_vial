#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Hash-check or rebuild locked fly_vial logs. Never overwrite the lock files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
TIMES = (0, 1, 8, 20, 40, 80)

EXPECTED_SHA256 = {
    "assort_80.json": "92a328278e62c4c607749c9358cdc733e1f06424a4b7f13c97c352ce4f4f759b",
    "random_80.json": "3c4606204cdf5516ddf7bbf371a59111473c944510fff4f87f8599b1171e8e61",
    "assort_80_s2.json": "f4b699dd1197ecc2ff98510073b568092dd3963ecabd19277770065e45a4d752",
    "random_80_s2.json": "ffcb77d6efb24c6cfbd4b2c94c9782c4dd751f24195720ad16a79327f629648f",
    "assort_80_s3.json": "fd8df4bb9fcf906ae349175728658e7f6f9019efe7354bda2cc32038f4b1e7a0",
    "random_80_s3.json": "5ca067a39917b150bb3056f632f10f89753bb2094c171323f35c9fbf4e5e05fd",
}

LOCKED = ("assort_80.json", "random_80.json")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_hashes() -> int:
    failed = 0
    for name, expected in EXPECTED_SHA256.items():
        path = LOGS / name
        if not path.is_file():
            print(f"MISSING {name}", file=sys.stderr)
            failed += 1
            continue
        got = sha256_file(path)
        if got != expected:
            print(f"HASH {name} {got} != {expected}", file=sys.stderr)
            failed += 1
        else:
            print(f"ok {name}")
    return 1 if failed else 0


def snapshot(path: Path) -> dict[int, tuple[int, float, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    by_t = {int(row["t"]): row for row in data["generations"]}
    out = {}
    for t in TIMES:
        row = by_t[t]
        out[t] = (
            int(row["n"]),
            float(row["F"]),
            float(row["fitness_components"]["courtship"]),
        )
    return out


def diff_snapshots(label: str, locked: dict, rebuilt: dict) -> list[str]:
    errs: list[str] = []
    for t in TIMES:
        ln, lf, lc = locked[t]
        rn, rf, rc = rebuilt[t]
        if ln != rn:
            errs.append(f"{label} t={t} n {rn} != {ln}")
        if abs(lf - rf) > 1e-12:
            errs.append(f"{label} t={t} F {rf} != {lf}")
        if abs(lc - rc) > 1e-12:
            errs.append(f"{label} t={t} courtship {rc} != {lc}")
    return errs


def rerun() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(ROOT))
    from fly_vial.config import RunConfig
    from fly_vial.population import run_generations, write_run

    locked_assort = snapshot(LOGS / "assort_80.json")
    locked_rand = snapshot(LOGS / "random_80.json")
    errs: list[str] = []
    with tempfile.TemporaryDirectory(prefix="fly_vial_repro_") as tmp:
        tmp_path = Path(tmp)
        assort_out = tmp_path / "assort.json"
        rand_out = tmp_path / "random.json"
        assort_cfg = RunConfig(
            n=1000,
            generations=80,
            seed=1,
            mating_mode="assortative_knn",
            k=3,
            eval_connectome=False,
            arm="assortative",
            cap="on",
            n_ceiling=1000,
        )
        rand_cfg = RunConfig(
            n=1000,
            generations=80,
            seed=1,
            mating_mode="random",
            eval_connectome=False,
            arm="random",
            cap="on",
            n_ceiling=1000,
        )
        write_run(run_generations(assort_cfg), assort_out)
        write_run(run_generations(rand_cfg), rand_out)
        if assort_out.resolve() == (LOGS / "assort_80.json").resolve():
            raise SystemExit("refuse: rerun would touch the lock")
        errs.extend(diff_snapshots("assortative", locked_assort, snapshot(assort_out)))
        errs.extend(diff_snapshots("random", locked_rand, snapshot(rand_out)))
        print(f"wrote temp {assort_out} {rand_out}")
    if errs:
        print("\n".join(errs), file=sys.stderr)
        return 1
    print("rerun matches seed-1 lock at t=0,1,8,20,40,80")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Hash-check or rebuild locked fly_vial logs")
    p.add_argument("--rerun", action="store_true", help="rebuild seed-1 80-gen arms in temp")
    args = p.parse_args(argv)
    for name in LOCKED:
        if not (LOGS / name).is_file():
            print(f"missing lock {name}", file=sys.stderr)
            return 1
    rc = check_hashes()
    if args.rerun:
        rc = rc or rerun()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
