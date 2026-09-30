"""Gemeinsame Präsentation von Gruppe 6 als PPTX für Google Slides.

Aufbau laut docs/superpowers/specs/2026-09-30-team-praesentation-design.md: Titel und Agenda,
Iana (Ausgangssituation, Daten), Kikos elf Folien (ML Canvas, Methodik und Modell), Patrick
(Ergebnisse, Empfehlungen, Fazit), Schluss, Backup und Folienmuster zum Weiterbauen.

Kikos Folien kommen aus ``build_kiko_pptx.py`` (Inhalt unverändert, Kapitelleiste statt
Schrittleiste, Diagramme als PNG). Alle Texte bleiben bearbeitbare Textfelder.

    .venv/Scripts/python.exe scripts/build_team_pptx.py
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parent))
import team_kit as kit  # noqa: E402

K, BUILD, ROOT = kit.K, kit.BUILD, kit.ROOT
OUT = kit.TEAM_DIR / "Gruppe6_Praesentation_SWW.pptx"


@dataclass
class Entry:
    kind: str                            # "main", "backup" oder "pattern"
    make: Callable                       # make(prs, num) -> Folie
    label: str


def kiko_specs():
    facts = BUILD["extract_facts"](BUILD["Notebook"].load())
    return BUILD["build_slides"](facts), facts


def check_sync(specs) -> None:
    assert len(specs) == len(K["BUILDERS"]), "HTML- und PPTX-Foliensatz von Kiko laufen auseinander"


def kiko_entries(specs, facts, charts) -> tuple[list[Entry], list[Entry]]:
    """Kikos Folien: Hauptfolien 1–2 gehören zu Kapitel 03, der Rest zu 04; Backups ohne Leiste."""
    main, backup = [], []
    for idx, (builder, spec) in enumerate(zip(K["BUILDERS"], specs)):
        chapter = None if spec.backup else ("03" if idx < 2 else "04")

        def make(prs, num, builder=builder, spec=spec, idx=idx, chapter=chapter):
            before = len(prs.slides)
            builder(prs, spec, num, facts)
            s = prs.slides[before]
            kit.replace_charts(s, idx, spec, charts)
            # Canvas-Folie hat die Feldpunkte, die Split-Folie die große Kapitelnummer
            if chapter and not any(sh.name.startswith("Canvas-Feld") or sh.name == "Split links" for sh in s.shapes):
                dark = s.background.fill.fore_color.rgb == kit.rgb(kit.NAVY)
                kit.chapter_bar(s, chapter, dark)
            return s

        (backup if spec.backup else main).append(Entry("backup" if spec.backup else "main", make, spec.label))
    return main, backup


def deck_entries(specs, facts, charts) -> list[Entry]:
    kiko_main, kiko_backup = kiko_entries(specs, facts, charts)
    return kiko_main + kiko_backup


def numbers(entries: list[Entry]) -> list[str]:
    total = sum(e.kind == "main" for e in entries)
    count = {"main": 0, "backup": 0, "pattern": 0}
    out = []
    for e in entries:
        count[e.kind] += 1
        n = count[e.kind]
        out.append(f"{n} / {total}" if e.kind == "main" else ("B" if e.kind == "backup" else "M") + str(n))
    return out


def _assemble(entries: list[Entry]):
    prs = Presentation()
    prs.slide_width, prs.slide_height = kit.E(kit.W), kit.E(kit.H)
    prs.core_properties.title = "Prognose des monatlichen Energieverbrauchs und Erkennung von Anomalien"
    prs.core_properties.author = "Gruppe 6 · Iana Kraievska · Patrick Olmo Hederer · Kiko Ramon Lukas"
    prs.core_properties.language = "de-DE"
    kit.STATE["scratch"] = prs.slides.add_slide(prs.slide_layouts[6])
    for entry, num in zip(entries, numbers(entries)):
        entry.make(prs, num)
    kit.drop_slide(prs, kit.STATE["scratch"])
    for slide in prs.slides:
        kit.flatten_alpha(slide)
    kit.theme_fonts(prs)
    return prs


def build(path: Path = OUT) -> Path:
    specs, facts = kiko_specs()
    check_sync(specs)
    charts = kit.load_charts()
    entries = deck_entries(specs, facts, charts)
    missing = K["_MISSING"]
    missing.clear()
    prs = _assemble(entries)
    if missing:  # fehlende Icons einmal gesammelt rendern, dann neu zusammenbauen
        K["render_icons"](missing)
        missing.clear()
        prs = _assemble(entries)
        if missing:
            raise RuntimeError(f"Icons fehlen weiterhin: {sorted(missing)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(path)
    return path


if __name__ == "__main__":
    out = build()
    print(f"{out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
