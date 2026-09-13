# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import json
from pathlib import Path

from fly_vial.claims import scan_text

REPO = Path(__file__).resolve().parents[1]


def test_readme_question_first_and_templates() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# fly_vial\n")
    body = text.split("\n", 1)[1].lstrip()
    assert body.startswith("Does a closed vial")
    assert "1,000" in text
    assert "139,255" in text
    assert "166,691" in text
    assert "What it is not" not in text
    assert "—" not in text
    assert scan_text(text) == []
    assert ".venv/bin/python -m pytest" in text
    assert "vialforge/" in text
    assert "AGENTS.md" in text
    assert "https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178" in text
    assort = json.loads((REPO / "logs" / "assort_80.json").read_text(encoding="utf-8"))
    rand = json.loads((REPO / "logs" / "random_80.json").read_text(encoding="utf-8"))
    a_last = assort["generations"][-1]
    r_last = rand["generations"][-1]
    frozen = (
        "k=3, seed 1, N=1,000, 80 generations: within-individual IBD "
        f"F = {a_last['F']:.3f} vs random F = {r_last['F']:.3f}. Census held. "
        "Courtship fell on both arms. Engine is closed-form. "
        "FlyWire/MaleCNS are templates, not the stepper."
    )
    assert frozen in text
    assert frozen in (REPO / "description.txt").read_text(encoding="utf-8")
    assert "logs/random_80.json" in text
    assert "t = 1" in text
    assert "0.934" in text
    assert "0.595" in text
    assert "H = 1 - F" in text
    assert "mean_pairwise_phi" in text
    assert "not F" in text.lower() or "It is not F" in text
    assert "free" in text.lower() and "recombination" in text.lower()
    assert "brain-only" in text or "no VNC" in text
    assert "closed-form overlays" in text
    assert "n_eval_hook" in text
    desc = (REPO / "description.txt").read_text(encoding="utf-8").strip()
    assert "F = 0.524" in desc
    assert "F = 0.034" in desc
    assert "not the stepper" in desc
    assert "templates" in desc
    assert "logs/assort_80_s2.json" in text
    assert "0.474" in text
    assert "0.463" in text
    assert "Failure contrast (ceiling still binding)" in text
    assert "Removing the cap did not make similarity pairing the faster route to failure." in text
    assert "Census never floated. Realized births stayed above 1,000 to t=200." in text
    assert "1,959" in text
    frozen_count = text.count(
        "k=3, seed 1, N=1,000, 80 generations: within-individual IBD F = 0.524 vs random F = 0.034."
    )
    assert frozen_count >= 1
