"""Registry-Bau: DB-Parsing, Typecode-Mapping (hermetisch)."""

from __future__ import annotations

import gzip

from fluglaerm.ist_laerm.registry import (
    build_full_registry,
    load_db,
    map_type,
    merge,
)

DB_ROWS = (
    "4B002C;HB-ABS;AT75;00;ATR-72-500;;;\n"
    "4b0086;HB-AFE;BU31;00;BUCKER Bu-131 Jungmann;;;\n"
    "3c675a;D-AIZZ;A20N;00;AIRBUS A-320neo;;;\n"
    "3c66b0;D-AIUP;A320;00;AIRBUS A-320;;;\n"
    "zzz999;BAD;A20N;00;AIRBUS A-320neo;;;\n"
)


def _db(tmp_path):
    plain = tmp_path / "aircraft.csv"
    plain.write_text(DB_ROWS, encoding="utf-8")
    gz = tmp_path / "aircraft.csv.gz"
    with gzip.open(gz, "wt", encoding="utf-8") as fh:
        fh.write(DB_ROWS)
    return load_db(plain), load_db(gz)


def test_map_type_pinned():
    assert map_type("A20N") == "A320-250N"      # Default LEAP
    assert map_type("a359") == "A350-1041"      # case-insensitive
    assert map_type("B77W") == "7773ER"
    assert map_type("B738") is None             # kein ANP-Flugzeug
    assert map_type("GLF6") is None             # G650ER: keine B-1-Koeffizienten
    assert map_type("E195") == "ERJ190-400"


def test_load_db_parses_gz_and_plain(tmp_path):
    plain, gz = _db(tmp_path)
    assert plain == gz
    assert "4b002c" in plain and "3c675a" in plain  # Hex klein, gemischt ok
    assert plain["4b002c"]["registration"] == "HB-ABS"
    assert plain["4b002c"]["typecode"] == "AT75"
    assert plain["4b002c"]["description"] == "ATR-72-500"
    assert "zzz999" not in plain  # keine gültige Hex-ID


def test_build_full_registry_maps_every_row(tmp_path):
    db, _ = _db(tmp_path)
    reg, report = build_full_registry(db)
    assert reg == {"3c675a": "A320-250N"}
    # AT75 (ATR), BU31 (Bucker) und A320 (ceo, kein NEO) haben keine
    # ANP-Entsprechung; zzz999 ist keine gültige Hex-ID und fällt raus
    assert report == [
        "1 x A320 — keine ANP-Entsprechung",
        "1 x AT75 — keine ANP-Entsprechung",
        "1 x BU31 — keine ANP-Entsprechung",
    ]


def test_build_full_registry_report_limit(tmp_path):
    rows = "".join(
        f"{i:06x};D-{i:06x};T{i};00;Beschreibung;;;\n" for i in range(25)
    )
    (tmp_path / "aircraft.csv").write_text(rows, encoding="utf-8")
    db = load_db(tmp_path / "aircraft.csv")
    reg, report = build_full_registry(db, limit=5)
    assert reg == {}
    assert len(report) == 5


def test_merge_keeps_manual_entries():
    assert merge({"abc": "A320-250N"}, {"abc": "A320-270N"}) == {"abc": "A320-250N"}
    assert merge({}, {"abc": "A320-250N"}) == {"abc": "A320-250N"}
