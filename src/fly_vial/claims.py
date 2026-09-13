# Copyright (c) 2026 Martial Systems LLC
"""Fail closed on banned claim tokens. Scan designated surfaces only."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

BANNED: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("unique_brains", re.compile(r"unique reconstructed|1,?000 unique", re.I)),
    (
        "population_spike",
        re.compile(
            r"(default|population).{0,40}(full[- ]cns|139k|167k|166k).{0,20}spike|"
            r"live (whole-cns|139k|167k|166k) LIF",
            re.I,
        ),
    ),
    (
        "animation_as_science",
        re.compile(r"\b(animation|renderer)\b.{0,40}\b(science|result|finding)\b", re.I),
    ),
    (
        "deformed_visual",
        re.compile(r"deformed.{0,30}visual style|visual style.{0,30}deformed", re.I),
    ),
    (
        "rescue",
        re.compile(r"\b(with immigration|wild-type rescue|restock from template)\b", re.I),
    ),
)


class ClaimBanError(RuntimeError):
    pass


def scan_text(text: str) -> list[str]:
    return [name for name, pat in BANNED if pat.search(text or "")]


def require_clean(text: str, *, source: str) -> None:
    hits = scan_text(text)
    if hits:
        raise ClaimBanError(f"{source}: banned claims {hits}")
    if "—" in (text or ""):
        raise ClaimBanError(f"{source}: em dash")


def require_paths_clean(paths: Iterable[Path]) -> None:
    for path in paths:
        if path.is_file():
            require_clean(path.read_text(encoding="utf-8"), source=str(path))
