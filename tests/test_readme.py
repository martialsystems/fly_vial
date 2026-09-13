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
    log = REPO / "logs" / "assort_80.json"
    assert log.is_file()
    data = json.loads(log.read_text(encoding="utf-8"))
    last = data["generations"][-1]
    assert f"F = {last['F']:.3f}" in text or f"F={last['F']:.3f}" in text
