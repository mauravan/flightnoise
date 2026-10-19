"""Importiert das EASA-ANP-Archiv v2.3 (CSV im ZIP) nach data/anp_archive.sqlite.

Die Proxies der EASA-Ersatztabelle (ANP Aircraft Substitutions – Jets & heavy
props) sind v2-Flugzeuge: von 109 ``ANP_PROXY``-Werten führt ANP v9
(``data/anp.sqlite``) nur ``7773ER``; die übrigen 108 existieren allein im von
EASA publizierten Archiv v2.3. Deshalb wird das Archiv als zweite, gleich
schemaisierte SQLite-DB eingelesen und über ``AnpDatabase.with_archive`` neben
v9 gespannt — v9 bleibt immer bevorzugt.

Verwendung (vom Projekt-Root aus)::

    .venv/bin/python data/import_anp_archive.py

Das ZIP (``data/easa_anp/anp_archive_2_3.zip``) wird bei Bedarf automatisch
entpackt. Schema identisch zu import_anp (gleiche Tabellen-/Spaltennamen und
Primärschlüssel), Rohformat CSV (Semikolon, UTF-8-BOM) statt xlsx. Idempotent
(DROP/CREATE pro Tabelle). ZIP, CSVs und DB sind gitignoriert
(EASA-Nutzungsbedingungen verbieten Weiterverbreitung).
"""

from __future__ import annotations

import csv
import sqlite3
import zipfile
from pathlib import Path

from import_anp import clean, sanitize

SRC_DIR = Path("data/easa_anp")
ZIP_PATH = SRC_DIR / "anp_archive_2_3.zip"
DB_PATH = Path("data/anp_archive.sqlite")

# (csv filename, table, primary key) — Spaltennamen identisch zu import_anp.
SOURCES: list[tuple[str, str, list[str]]] = [
    ("ANP2.3_Aircraft.csv", "aircraft", ["acft_id"]),
    ("ANP2.3_NPD_data.csv", "npd_data",
     ["npd_id", "noise_metric", "op_mode", "power_setting"]),
    ("ANP2.3_Aerodynamic_coefficients.csv", "aerodynamic_coefficients",
     ["acft_id", "op_type", "flap_id"]),
    ("ANP2.3_Default_approach_procedural_steps.csv",
     "default_approach_procedural_steps",
     ["acft_id", "profile_id", "step_number", "flap_id"]),
    ("ANP2.3_Default_departure_procedural_steps.csv",
     "default_departure_procedural_steps",
     ["acft_id", "profile_id", "stage_length", "step_number"]),
    ("ANP2.3_Default_fixed_point_profiles.csv", "default_fixed_point_profiles",
     ["acft_id", "op_type", "profile_id", "stage_length", "point_number"]),
    ("ANP2.3_Default_weights.csv", "default_weights",
     ["acft_id", "stage_length"]),
    ("ANP2.3_Jet_engine_coefficients.csv", "jet_engine_coefficients",
     ["acft_id", "thrust_rating"]),
    ("ANP2.3_Propeller_engine_coefficients.csv", "propeller_engine_coefficients",
     ["acft_id", "thrust_rating"]),
    ("ANP2.3_Spectral_classes.csv", "spectral_classes", ["spectral_class_id"]),
]


def _typed(value: object) -> object:
    """CSV-Strings → int/float wo möglich (die v9-xlsx liefert Typen fertig)."""
    if not isinstance(value, str):
        return value
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


# Die v2.3-CSV benennt die Spalte "Wing" der v9-xlsx als
# "Lateral Directivity Identifier"; AnpDatabase/evaluate_own sprechen 'wing'.
_COLUMN_ALIAS = {"lateral_directivity_identifier": "wing"}


def read_csv(path: Path) -> tuple[list[str], list[tuple]]:
    """Liest eine Archiv-CSV (Semikolon, UTF-8-BOM): (Spalten, Datenzeilen)."""
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter=";")
        header = next(reader)
        columns = [
            _COLUMN_ALIAS.get(name, name) for name in map(lambda h: sanitize(str(h)), header)
        ]
        rows = [tuple(_typed(clean(c)) for c in row) for row in reader]
    return columns, rows


def ensure_csvs() -> None:
    """Entpackt alle ``ANP2.3_*``-Mitglieder des ZIPs, wenn keine CSV existiert."""
    if any(SRC_DIR.glob("ANP2.3_*.csv")):
        return
    if not ZIP_PATH.exists():
        raise FileNotFoundError(
            f"{ZIP_PATH} nicht gefunden; erst "
            "curl -L -o data/easa_anp/anp_archive_2_3.zip "
            "https://www.easa.europa.eu/en/downloads/138164/en"
        )
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as zf:
        members = [
            name for name in zf.namelist()
            if name.startswith("ANP2.3_") and not name.endswith("/")
        ]
        zf.extractall(SRC_DIR, members)


def import_archive(src_dir: Path = SRC_DIR, db_path: Path = DB_PATH) -> dict[str, int]:
    """Liest alle zehn Archiv-CSVs und baut die SQLite-DB neu auf."""
    counts: dict[str, int] = {}
    conn = sqlite3.connect(db_path)
    try:
        for filename, table, pk in SOURCES:
            columns, rows = read_csv(src_dir / filename)
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            pk_clause = f", PRIMARY KEY ({', '.join(pk)})"
            conn.execute(f"CREATE TABLE {table} ({', '.join(columns)}{pk_clause})")
            conn.executemany(
                f"INSERT INTO {table} VALUES ({', '.join('?' * len(columns))})",
                rows,
            )
            conn.commit()
            counts[table] = len(rows)
        conn.execute(
            "CREATE INDEX idx_npd_mode ON npd_data (npd_id, op_mode, noise_metric)"
        )
        conn.commit()
    finally:
        conn.close()
    return counts


def main() -> None:
    ensure_csvs()
    counts = import_archive()
    total = 0
    for _filename, table, _pk in SOURCES:
        n = counts[table]
        total += n
        print(f"{table}: {n} rows")
    print(f"total: {total} rows")


if __name__ == "__main__":
    main()
