"""Baut die Aircraft-Registry: ICAO24 → ANP acft_id.

Quelle ist die wiedehopf/tar1090-db (csv-Branch; Mictronics-Datenbank —
dieselbe Datenbasis, die auch readsb/tar1090 nutzen). Semikolon-CSV ohne
Kopfzeile, Felder::

    icao24;registration;typecode;flags;description
    4B002C;HB-ABS;AT75;00;ATR-72-500;;;

Never-guess: nur Typecodes mit genau einem passenden ANP-Flugzeug werden
gemappt (TYPECODE_MAP). Wo die Datenbasis keine Entscheidung erlaubt
(A320neo-Triebwerksvariante), greift ein dokumentierter Default, der pro Hex
überschreibbar bleibt; alles Unklare bleibt unbekannt und wird gemeldet.
"""

from __future__ import annotations

import csv
import gzip
import re
import sys
import urllib.request
from pathlib import Path

DB_URL = (
    "https://github.com/wiedehopf/tar1090-db/raw/refs/heads/csv/aircraft.csv.gz"
)

# Typecode → ANP acft_id. Nur Einträge, für die data/anp.sqlite genau ein
# passendes Flugzeug mit B-1-Koeffizienten hat (12 von 14).
TYPECODE_MAP: dict[str, str] = {
    "A20N": "A320-250N",   # Default LEAP-1A; PW-Variante (A320-270N) nur von Hand
    "A21N": "A321-270N",   # ANP führt nur eine A321neo-Reihe
    "A332": "A330-743L",   # A330-200 ceo
    "A333": "A330-743L",   # A330-300 ceo
    "A338": "A330-941",    # A330-800 neo
    "A339": "A330-941",    # A330-900 neo
    "A359": "A350-1041",   # A350-900
    "B744": "747400RN",
    "B763": "7673ER",
    "B77W": "7773ER",      # 777-300ER
    "B789": "7879",
    "E190": "ERJ190-300",
    "E195": "ERJ190-400",
}

_HEX = re.compile(r"^[0-9a-f]{6}$")


def map_type(typecode: str, description: str = "") -> str | None:
    """ICAO-Typecode → ANP acft_id; None wenn kein eindeutiger Treffer."""
    return TYPECODE_MAP.get(typecode.strip().upper())


def ensure_db(path: str | Path, url: str = DB_URL) -> None:
    """Lädt die tar1090-db-CSV, falls sie noch nicht vorliegt."""
    path = Path(path)
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"lade {url} → {path} …", file=sys.stderr)
    urllib.request.urlretrieve(url, path)
    print(f"{path} ({path.stat().st_size} bytes)", file=sys.stderr)


def load_db(path: str | Path) -> dict[str, dict[str, str]]:
    """Liest die tar1090-db-CSV (auch .gz): {icao24 klein → Felder}."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as fh:
        rows = csv.reader(fh, delimiter=";")
        out: dict[str, dict[str, str]] = {}
        for row in rows:
            if len(row) < 3:
                continue
            icao24 = row[0].strip().lower()
            if not _HEX.match(icao24):
                continue
            out[icao24] = {
                "registration": row[1].strip(),
                "typecode": row[2].strip(),
                "description": row[4].strip() if len(row) > 4 else "",
            }
    return out


def build_full_registry(
    db: dict[str, dict[str, str]], limit: int = 20
) -> tuple[dict[str, str], list[str]]:
    """Mappt jede Zeile der Flugzeug-DB: {icao24 → acft_id} plus Report-Zeilen
    für die häufigsten Typecodes ohne ANP-Entsprechung — nie geraten."""
    reg: dict[str, str] = {}
    unmapped: dict[str, int] = {}
    for icao24, entry in db.items():
        acft_id = map_type(entry["typecode"], entry["description"])
        if acft_id is None:
            code = entry["typecode"] or "(kein Typecode)"
            unmapped[code] = unmapped.get(code, 0) + 1
            continue
        reg[icao24] = acft_id
    report = [
        f"{count} x {code} — keine ANP-Entsprechung"
        for code, count in sorted(
            unmapped.items(), key=lambda kv: (-kv[1], kv[0])
        )[:limit]
    ]
    return reg, report


def merge(existing: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    """Bestehende Einträge gewinnen — Handkorrekturen (z. B. A320-270N)
    werden nie überschrieben."""
    out = dict(new)
    out.update(existing)
    return out
