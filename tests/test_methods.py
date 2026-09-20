# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from pathlib import Path

from fly_vial.claims import scan_text

REPO = Path(__file__).resolve().parents[1]
QUESTION = (
    "Does a closed vial of 1,000 diploid flies, paired by genome similarity, "
    "raise IBD F faster than random mating at the same N, seed, and load?"
)


def test_methods_card_matches_readme_question() -> None:
    text = (REPO / "METHODS.yaml").read_text(encoding="utf-8")
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("question: " + QUESTION)
    assert QUESTION in readme
    assert "pre_specified: false" in text
    assert "science_lock: e2e22b7" in text
    assert "object: unconstrained evolutionary toy" in text
    assert "status: Screen" in text
    assert "n_seeds: 3" in text
    assert "166691" in text
    assert "139255" in text
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert "METHODS.yaml" in readme
    assert "CITATION.cff" in readme
    assert "REPRODUCE.md" in readme
    assert "scripts/reproduce_lock.py" in readme
    cite = (REPO / "CITATION.cff").read_text(encoding="utf-8")
    assert "cff-version: 1.2.0" in cite
    assert "Martial Systems LLC" in cite
    assert "10.5281" not in cite
    assert "Grok" not in cite
    assert "type: swh" in cite
    assert "swh:1:snp:1ca342b7bacb5c9f996cf97a39933df3eb6c056e" in cite
    assert "—" not in cite
    assert (REPO / "requirements.lock.txt").is_file()
    lock = (REPO / "requirements.lock.txt").read_text(encoding="utf-8")
    assert "numpy==2.5.3" in lock
    assert "pytest==9.1.1" in lock
    third = (REPO / "THIRD_PARTY.md").read_text(encoding="utf-8")
    assert "10.1016/j.cell.2026.08.015" in third
    assert "166,691" in third
    assert "166,700" not in third
    assert scan_text(third) == []
    repro = (REPO / "REPRODUCE.md").read_text(encoding="utf-8")
    assert "92a328278e62c4c607749c9358cdc733e1f06424a4b7f13c97c352ce4f4f759b" in repro
    assert "Never overwrite" in repro or "never overwrite" in repro.lower()
    assert "—" not in repro
    assert scan_text(repro) == []


def test_reproduce_lock_hashes() -> None:
    import subprocess

    script = REPO / "scripts" / "reproduce_lock.py"
    proc = subprocess.run(
        [str(REPO / ".venv" / "bin" / "python"), str(script)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    assert "ok assort_80.json" in proc.stdout
    assert "ok random_80.json" in proc.stdout
