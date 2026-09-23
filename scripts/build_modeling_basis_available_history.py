"""Build the modeling snapshot with a leakage-safe available-history feature.

Patrick's interface file remains read-only.  The derived snapshot only changes
the three history columns and documents the rule in a deterministic provenance
file.  In particular, no future observation is used to fill a cold start.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "processed" / "modellierung_basis.csv"
DESTINATION = (
    ROOT / "data" / "processed" / "modellierung_basis_bis_3_monate.csv"
)
PROVENANCE = DESTINATION.with_suffix(".provenance.json")

EXPECTED_COLUMNS = [
    "zaehler_id",
    "monat",
    "jahr",
    "split",
    "vollaststunden",
    "verbrauch_kwh",
    "vertragsleistung_kw",
    "kundentyp",
    "monat_idx",
    "arbeitstage",
    "feiertage_im_monat",
    "heizgradtage",
    "produktionsplan_index",
    "wartung_aktiv",
    "vormonat_vls",
    "letzte_3_monate_vls",
    "vorjahr_vls",
    "anomalie",
    "unmoeglich",
    "ziel_rekonstruiert",
]
HISTORY_COLUMNS = ["vormonat_vls", "letzte_3_monate_vls", "vorjahr_vls"]


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _same_with_nan(left: pd.Series, right: pd.Series) -> bool:
    return bool(
        np.allclose(
            left.to_numpy(float),
            right.to_numpy(float),
            rtol=1e-10,
            atol=1e-10,
            equal_nan=True,
        )
    )


def _validate_source(frame: pd.DataFrame) -> None:
    if frame.columns.tolist() != EXPECTED_COLUMNS:
        raise ValueError("Das Schema der Modellierungsbasis hat sich geändert.")
    if len(frame) != 16_800 or frame["zaehler_id"].nunique() != 700:
        raise ValueError("Erwartet werden 16.800 Monatswerte für 700 Zähler.")
    if frame.duplicated(["zaehler_id", "monat"]).any():
        raise ValueError("Zähler und Monat müssen eindeutig sein.")
    if set(frame["split"].unique()) != {"train", "test", "ausschluss"}:
        raise ValueError("Unerwartete Werte in der Split-Spalte.")
    if not frame["vertragsleistung_kw"].gt(0).all():
        raise ValueError("Die Vertragsleistung muss positiv sein.")
    if not np.allclose(
        frame["vollaststunden"],
        frame["verbrauch_kwh"] / frame["vertragsleistung_kw"],
        rtol=1e-10,
        atol=1e-10,
    ):
        raise ValueError("Vollaststunden und kWh/Vertragsleistung widersprechen sich.")

    counts = frame.groupby("zaehler_id", observed=True).size()
    if not counts.eq(24).all():
        raise ValueError("Jeder Zähler muss genau 24 Monatswerte besitzen.")
    expected_months = pd.date_range("2024-01-01", "2025-12-01", freq="MS")
    for meter_id, group in frame.groupby("zaehler_id", sort=False, observed=True):
        actual = pd.DatetimeIndex(group.sort_values("monat")["monat"])
        if not actual.equals(expected_months):
            raise ValueError(f"Die Zeitachse von {meter_id} ist nicht lückenlos.")


def build_frame(source: Path = SOURCE) -> tuple[pd.DataFrame, dict]:
    source = source.resolve()
    source_bytes = source.read_bytes()
    frame = pd.read_csv(source, parse_dates=["monat"])
    _validate_source(frame)

    original = frame.copy(deep=True)
    frame = frame.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
    valid_vls = frame["vollaststunden"].mask(frame["unmoeglich"].astype(bool))
    grouped = valid_vls.groupby(frame["zaehler_id"], sort=False)

    frame["vormonat_vls"] = grouped.shift(1)
    frame["letzte_3_monate_vls"] = grouped.transform(
        lambda values: values.shift(1).rolling(3, min_periods=1).mean()
    )
    frame["vorjahr_vls"] = grouped.shift(12)

    # Existing strict three-month values must remain numerically unchanged.
    strict_values = original.sort_values(["zaehler_id", "monat"])[
        "letzte_3_monate_vls"
    ].reset_index(drop=True)
    strict_mask = strict_values.notna()
    if not np.allclose(
        frame.loc[strict_mask, "letzte_3_monate_vls"],
        strict_values[strict_mask],
        rtol=1e-10,
        atol=1e-10,
    ):
        raise AssertionError("Bereits vorhandene Drei-Monats-Werte wurden verändert.")

    sorted_original = original.sort_values(["zaehler_id", "monat"]).reset_index(drop=True)
    for column in [name for name in EXPECTED_COLUMNS if name not in HISTORY_COLUMNS]:
        if not frame[column].equals(sorted_original[column]):
            raise AssertionError(f"Die fachfremde Spalte {column} wurde verändert.")
    if not _same_with_nan(frame["vormonat_vls"], sorted_original["vormonat_vls"]):
        raise AssertionError("Vormonat weicht von Patricks geprüfter Berechnung ab.")
    if not _same_with_nan(frame["vorjahr_vls"], sorted_original["vorjahr_vls"]):
        raise AssertionError("Vorjahr weicht von Patricks geprüfter Berechnung ab.")

    newly_available = int((
        sorted_original["letzte_3_monate_vls"].isna()
        & frame["letzte_3_monate_vls"].notna()
    ).sum())
    remaining_missing = int(frame["letzte_3_monate_vls"].isna().sum())
    if newly_available != 1_453 or remaining_missing != 700:
        raise AssertionError(
            "Die erwartete Cold-Start-Struktur hat sich geändert: "
            f"ergänzt={newly_available}, verbleibend={remaining_missing}."
        )

    january = frame[frame["monat"].eq(pd.Timestamp("2024-01-01"))]
    if len(january) != 700 or january["letzte_3_monate_vls"].notna().any():
        raise AssertionError("Januar 2024 muss je Zähler ein echter Cold Start bleiben.")

    stats = {
        "rows": int(len(frame)),
        "meters": int(frame["zaehler_id"].nunique()),
        "newly_available_lag3_values": newly_available,
        "remaining_lag3_missing": remaining_missing,
        "source_sha256": _sha256_bytes(source_bytes),
    }
    if _sha256_bytes(source.read_bytes()) != stats["source_sha256"]:
        raise AssertionError("Die Quelldatei wurde während der Verarbeitung verändert.")
    return frame[EXPECTED_COLUMNS], stats


def render_csv(frame: pd.DataFrame) -> str:
    buffer = io.StringIO(newline="")
    frame.to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def render_provenance(csv_text: str, stats: dict) -> str:
    script_hash = _sha256_bytes(Path(__file__).read_bytes())
    payload = {
        "schema_version": 1,
        "policy": {
            "name": "bis_zu_drei_gueltige_vormonate",
            "window_months": 3,
            "min_periods": 1,
            "current_month_excluded": True,
            "unmoegliche_ziele_excluded_from_history": True,
            "future_values_used": False,
            "cold_start": "Januar 2024 bleibt NaN",
        },
        "source": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
        "destination": str(DESTINATION.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": stats["source_sha256"],
        "output_sha256": _sha256_bytes(csv_text.encode("utf-8")),
        "script_sha256": script_hash,
        "rows": stats["rows"],
        "meters": stats["meters"],
        "newly_available_lag3_values": stats["newly_available_lag3_values"],
        "remaining_lag3_missing": stats["remaining_lag3_missing"],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def build_artifacts(source: Path = SOURCE) -> tuple[str, str]:
    frame, stats = build_frame(source)
    csv_text = render_csv(frame)
    return csv_text, render_provenance(csv_text, stats)


def _write_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="nur prüfen, ob CSV und Provenienz aktuell sind",
    )
    args = parser.parse_args()
    if SOURCE.resolve() == DESTINATION.resolve():
        raise SystemExit("Quelle und Ziel dürfen nicht identisch sein.")

    csv_text, provenance_text = build_artifacts()
    if args.check:
        expected = ((DESTINATION, csv_text), (PROVENANCE, provenance_text))
        stale = [path for path, content in expected if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit("Veraltete Artefakte: " + ", ".join(str(path) for path in stale))
        print(f"Modellierungsbasis ist aktuell: {DESTINATION}")
        return

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    _write_atomic(DESTINATION, csv_text)
    _write_atomic(PROVENANCE, provenance_text)
    print(DESTINATION)
    print(PROVENANCE)


if __name__ == "__main__":
    main()
