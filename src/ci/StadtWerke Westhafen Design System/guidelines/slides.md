# Präsentationen und PowerPoint

Die HTML-Layouts in `slides/` sind die Referenz. Für PowerPoint gelten dieselben Regeln, nur in
anderen Einheiten.

## Seitenmaß

| Ziel | Maß |
| --- | --- |
| HTML-Layouts hier | 1280 × 720 px |
| PowerPoint 16:9 | 33,87 × 19,05 cm (Standard-Breitbild) |
| Umrechnung | 1 px (1280er Bühne) ≈ 0,0265 cm |

## Typografie in PowerPoint

| Rolle | HTML | PowerPoint |
| --- | --- | --- |
| Titel Deckblatt | 54 px | 40 pt Semibold, Zeilenabstand 1,08 |
| Folientitel | 40 px | 30 pt Semibold |
| Eyebrow / Kapitel | 16 px, +0,1em, Versalien | 12 pt Semibold, Laufweite erweitert |
| Lead / Kernaussage | 24 px | 18 pt Regular |
| Fließtext, Aufzählung | 19–22 px | 14–16 pt Regular |
| Kennzahl | 40 px Geist Mono | 30 pt Geist Mono Semibold (nur Kacheln, nicht in Charts) |
| Fußzeile | 16 px | 12 pt Regular, `--grey-500` |

Schriften: **IBM Plex Sans** und **Geist Mono** (kostenlos, installierbar). Ohne Installation
ersatzweise Segoe UI / Consolas — dann Laufweiten prüfen.

## Aufbau eines Decks

1. Titelfolie (Navy, Vollsignet)
2. Agenda
3. Kapiteltrenner pro IHK-Kapitel (4 Stück)
4. Inhalt: höchstens ein Gedanke pro Folie, Aussage in der Überschrift
5. Abschlussfolie mit Empfehlungen und dem Modell-Vorbehalt

**Höchstens zwei Hintergründe** im ganzen Deck: weiß und `--navy-800`. Navy ist reserviert für
Titel, Kapiteltrenner, Zitat und Abschluss — nie für Inhaltsfolien mit Tabellen oder Charts.

## Charts in Folien

Aus dem Notebook exportieren, nicht in PowerPoint nachbauen:

```python
fig.write_image("chart.png", width=1120, height=560, scale=2)
```

Achsen- und Legendenschrift vor dem Export auf 15–17 px hochsetzen (Folienabstand ≫ Bildschirm).
Chart-PNG als Bild einfügen, Überschrift und Aussage als echten Text daneben — nie als Teil des Bildes.

## Fußzeile

Wortmarke links (Höhe ≈ 0,7 cm), Projektname mittig, Foliennummer rechts, 1 px Trennlinie
`--border-subtle` darüber. Auf Navy-Folien Trennlinie in Weiß 16 %.

## Was nicht vorkommt

Keine Emoji. Keine Cliparts oder Icon-Dekoration. Keine Verlaufshintergründe. Keine
Folienübergänge außer "Weich" (oder gar keine). Keine Aufzählung tiefer als zwei Ebenen.
Keine Vollzitate aus dem Bericht — Folien tragen Aussagen, der Bericht trägt Belege.
