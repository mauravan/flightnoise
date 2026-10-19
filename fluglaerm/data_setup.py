"""Daten-Setup: prüft die von ``fluglaerm`` gebrauchten Dateien und stellt
bereit, was ohne menschliche Lizenzschritte geht (NPD-Platzhalter, ANP-Sqlite,
GWR-Sqlite, Flugzeug-DB, Aircraft-Registry); alles Übrige wird mit Quelle und
Zielpfad gemeldet.

``plan`` scannt rein lesend und vergibt ``ok`` | ``auto`` | ``manual``;
``apply`` führt die ``auto``-Schritte aus und macht daraus ``fixed``
(Erfolg) oder ``manual`` (Fehlschlag, ``detail`` = Anleitung).
Kein Fehlschlag bricht den Lauf ab — jedes Item bekommt sein eigenes Urteil.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

from fluglaerm.ist_laerm import registry

_NPD_PATH = "data/anp/*.json"
_SQLITE_PATH = "data/anp.sqlite"
_SEED_PATH = "data/seed/zrh_vbr2012.json"
_GWR_PATH = "data/ch.sqlite"
_AIRCRAFT_PATH = "data/aircraft.csv.gz"
_REGISTRY_PATH = "data/aircraft_registry.json"
_CREDENTIALS_PATH = "credentials.json"

GWR_URL = "https://public.madd.bfs.admin.ch/data_ch.sqlite"

NPD_ACTION = "data/anp/make_placeholders.py"
NPD_FAIL = (
    "data/anp/make_placeholders.py ausführen "
    "(.venv/bin/python data/anp/make_placeholders.py); echte NPD-Tabellen über "
    "data/fetch_anp.py"
)
SQLITE_ACTION = "data/import_anp.py"
SQLITE_FAIL = (
    "EASA-ANP-v9-Workbooks (9 xlsx) von "
    "https://www.easa.europa.eu/en/anp-data-request nach data/easa_anp/ legen "
    "(Dateinamen s. SOURCES in data/import_anp.py), dann setup erneut "
    "ausführen. Alt (nur NPD-Tabellen als JSON): data/fetch_anp.py."
)
SEED_FAIL = (
    "data/seed/build_seed.py ausführen (Datei ist git-committet; fehlt sie, "
    "ist der Checkout unvollständig)."
)
GWR_FAIL = (
    "curl -C - -o data/ch.sqlite " + GWR_URL + " (1.7 GB)"
)
AIRCRAFT_FAIL = f"curl -L -o data/aircraft.csv.gz {registry.DB_URL}"
REGISTRY_NO_DB = (
    "Flugzeug-DB fehlt (data/aircraft.csv.gz) — Registry kann nicht "
    "gebaut werden."
)
REGISTRY_EMPTY = (
    "Kein Flugzeug in der Flugzeug-DB hat eine ANP-Entsprechung — "
    "data/aircraft_registry.json von Hand pflegen."
)
CREDENTIALS_FAIL = (
    "Nur für 'own' nötig: --client-id/--client-secret bzw. "
    "OPENSKY_CLIENT_ID/OPENSKY_CLIENT_SECRET, oder credentials.json mit "
    '{"clientId": …, "clientSecret": …}. Nie committen.'
)
ARCHIVE_URL = "https://www.easa.europa.eu/en/downloads/138164/en"
SUBSTITUTIONS_URL = "https://www.easa.europa.eu/en/downloads/138165/en"
_ARCHIVE_PATH = "data/anp_archive.sqlite"
_ARCHIVE_ZIP = "data/easa_anp/anp_archive_2_3.zip"
_SUBSTITUTIONS_PATH = "data/anp.sqlite:substitutions"
_SUBSTITUTIONS_XLSX = ("data/easa_anp/"
    "anp_aircraft_substitutions_-_jets_heavy_props_22022018_.xlsx")
ARCHIVE_FAIL = (
    "curl -L -o data/easa_anp/anp_archive_2_3.zip " + ARCHIVE_URL
    + ", dann .venv/bin/python data/import_anp_archive.py."
)
SUBSTITUTIONS_FAIL = (
    "curl -L -o " + _SUBSTITUTIONS_XLSX + " " + SUBSTITUTIONS_URL
    + ", dann .venv/bin/python data/import_substitutions.py."
)
SUBSTITUTIONS_NO_DB = (
    "ANP-Datenbank fehlt (data/anp.sqlite) — Ersatztabelle kann nicht "
    "geschrieben werden; setup erneut ausführen, sobald data/anp.sqlite steht."
)
ARCHIVE_ACTION = "data/import_anp_archive.py"
SUBSTITUTIONS_ACTION = "data/import_substitutions.py"


@dataclass(frozen=True)
class Item:
    name: str
    path: str
    status: str
    detail: str


def _has_npd(root: Path) -> bool:
    return any((root / "data/anp").glob("*.json"))


def _has_workbooks(root: Path) -> bool:
    return any((root / "data/easa_anp").glob("*.xlsx"))


def _registry_fresh(root: Path) -> bool:
    """Registry vorhanden, nicht leer und nicht älter als die Flugzeug-DB."""
    reg = root / _REGISTRY_PATH
    db = root / _AIRCRAFT_PATH
    if not reg.exists():
        return False
    try:
        data = json.loads(reg.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(data) and db.exists() and reg.stat().st_mtime >= db.stat().st_mtime


def _env_credentials() -> bool:
    return bool(
        os.environ.get("OPENSKY_CLIENT_ID")
        and os.environ.get("OPENSKY_CLIENT_SECRET")
    )


def _table_rows(root: Path, db_rel: str, table: str) -> int:
    """Zeilen in ``table`` (0 wenn DB/Tabelle fehlen oder leer)."""
    path = root / db_rel
    if not path.exists():
        return 0
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as con:
            return int(con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    except sqlite3.Error:
        return 0


def _archive_ok(root: Path) -> bool:
    return _table_rows(root, _ARCHIVE_PATH, "aircraft") > 0


def _substitutions_ok(root: Path) -> bool:
    return _table_rows(root, "data/anp.sqlite", "substitutions") > 0


def plan(root: Path, gwr: bool = False) -> list[Item]:
    """Reiner Scan (keine Schreibzugriffe): ein Item pro Datengut, fixe Reihenfolge."""
    npd = _has_npd(root)
    sqlite = (root / _SQLITE_PATH).exists()
    workbooks = _has_workbooks(root)
    seed = (root / _SEED_PATH).exists()
    ch = (root / _GWR_PATH).exists()
    aircraft = (root / _AIRCRAFT_PATH).exists()
    reg = _registry_fresh(root)
    cred = (root / _CREDENTIALS_PATH).exists() or _env_credentials()
    return [
        Item(
            "NPD-Tabellen", _NPD_PATH,
            "ok" if npd else "auto",
            "" if npd else NPD_ACTION,
        ),
        Item(
            "ANP-Datenbank", _SQLITE_PATH,
            "ok" if sqlite else ("auto" if workbooks else "manual"),
            "" if sqlite else (SQLITE_ACTION if workbooks else SQLITE_FAIL),
        ),
        Item(
            "ANP-Archiv v2.3", _ARCHIVE_PATH,
            "ok" if _archive_ok(root) else "auto",
            "" if _archive_ok(root) else
            f"download {ARCHIVE_URL} → data/easa_anp/, dann {ARCHIVE_ACTION}",
        ),
        Item(
            "ANP-Substitutionen", _SUBSTITUTIONS_PATH,
            "ok" if _substitutions_ok(root) else "auto",
            "" if _substitutions_ok(root) else
            f"download {SUBSTITUTIONS_URL} → data/easa_anp/, dann "
            f"{SUBSTITUTIONS_ACTION}",
        ),
        Item(
            "Seed-Datensatz", _SEED_PATH,
            "ok" if seed else "manual",
            "" if seed else SEED_FAIL,
        ),
        Item(
            "GWR-Datenbank", _GWR_PATH,
            "ok" if ch else ("auto" if gwr else "manual"),
            "" if ch else GWR_FAIL,
        ),
        Item(
            "Flugzeug-DB", _AIRCRAFT_PATH,
            "ok" if aircraft else "auto",
            "" if aircraft else
            f"download {registry.DB_URL} → data/aircraft.csv.gz",
        ),
        Item(
            "Aircraft-Registry", _REGISTRY_PATH,
            "ok" if reg else "auto",
            "" if reg else f"Registry bauen aus {_AIRCRAFT_PATH}",
        ),
        Item(
            "OpenSky-Credentials", _CREDENTIALS_PATH,
            "ok" if cred else "manual",
            "" if cred else CREDENTIALS_FAIL,
        ),
    ]


def _run_script(rel: str, root: Path | None = None) -> tuple[bool, str]:
    """Führt ein ``data/``-Skript im Projekt-Root aus — die Skripte schreiben
    relativ zum CWD, ``cwd=root`` ist also tragend."""
    proc = subprocess.run(
        [sys.executable, rel],
        cwd=root if root is not None else Path("."),
        capture_output=True,
        text=True,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-500:]


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)


def _download_gwr(url: str, dest: Path) -> None:
    """1.7 GB nur über curl (Fortsetzen mit -C -); fehlt curl, meldet apply manuell."""
    if shutil.which("curl") is None:
        raise RuntimeError("curl nicht gefunden")
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-L", "-C", "-", "-o", str(dest), url], check=False)


def _set(items: list[Item], path: str, status: str, detail: str) -> None:
    for i, it in enumerate(items):
        if it.path == path:
            items[i] = replace(it, status=status, detail=detail)
            return


def _registry_step(root: Path, report: list[str]) -> tuple[str, str]:
    """Mappt die ganze Flugzeug-DB in die Registry (bestehende Einträge
    gewinnen). Nie geraten: was kein ANP-Flugzeug hat, bleibt draussen und
    wird als Report-Zeile gemeldet."""
    db = registry.load_db(root / _AIRCRAFT_PATH)
    new, lines = registry.build_full_registry(db)
    report.extend(lines)
    reg_path = root / _REGISTRY_PATH
    existing: dict[str, str] = {}
    if reg_path.exists():
        existing = json.loads(reg_path.read_text(encoding="utf-8"))
    merged = registry.merge(existing, new)
    if not merged:
        return "manual", REGISTRY_EMPTY
    if merged == existing:
        return "ok", f"{len(merged)} Einträge in {_REGISTRY_PATH} (unverändert)"
    reg_path.parent.mkdir(parents=True, exist_ok=True)
    reg_path.write_text(
        json.dumps(merged, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    return "fixed", f"{len(new)} gemappt, {len(merged)} Einträge in {_REGISTRY_PATH}"


def apply(
    root: Path,
    gwr: bool = False,
    run_script: Callable[[str], tuple[bool, str]] | None = None,
    download: Callable[[str, Path], None] | None = None,
    download_gwr: Callable[[str, Path], None] | None = None,
) -> tuple[list[Item], list[str]]:
    """Führt jeden ``auto``-Schritt aus; gibt (Items, Report-Zeilen) zurück."""
    items = plan(root, gwr)
    report: list[str] = []
    script = run_script or (lambda rel: _run_script(rel, root))
    fetch = download or _download
    fetch_gwr = download_gwr or _download_gwr

    for it in list(items):
        if it.status != "auto":
            continue
        path = it.path
        fallback = it.detail
        try:
            if path == _NPD_PATH:
                ok, _out = script(NPD_ACTION)
                done = ok and _has_npd(root)
                _set(items, path, "fixed" if done else "manual",
                     NPD_ACTION if done else NPD_FAIL)
            elif path == _SQLITE_PATH:
                ok, _out = script(SQLITE_ACTION)
                done = ok and (root / _SQLITE_PATH).exists()
                _set(items, path, "fixed" if done else "manual",
                     SQLITE_ACTION if done else SQLITE_FAIL)
            elif path == _ARCHIVE_PATH:
                fetch(ARCHIVE_URL, root / _ARCHIVE_ZIP)
                ok, _out = script(ARCHIVE_ACTION)
                done = ok and _archive_ok(root)
                _set(items, path, "fixed" if done else "manual",
                     f"{_table_rows(root, _ARCHIVE_PATH, 'aircraft')} Flugzeuge "
                     f"in {_ARCHIVE_PATH}" if done else ARCHIVE_FAIL)
            elif path == _SUBSTITUTIONS_PATH:
                if not (root / _SQLITE_PATH).exists():
                    _set(items, path, "manual", SUBSTITUTIONS_NO_DB)
                else:
                    fetch(SUBSTITUTIONS_URL, root / _SUBSTITUTIONS_XLSX)
                    ok, _out = script(SUBSTITUTIONS_ACTION)
                    done = ok and _substitutions_ok(root)
                    _set(items, path, "fixed" if done else "manual",
                         f"{_table_rows(root, 'data/anp.sqlite', 'substitutions')} "
                         f"Ersatztypen in data/anp.sqlite" if done
                         else SUBSTITUTIONS_FAIL)
            elif path == _GWR_PATH:
                fetch_gwr(GWR_URL, root / _GWR_PATH)
                done = (root / _GWR_PATH).exists()
                _set(items, path, "fixed" if done else "manual", GWR_FAIL)
            elif path == _AIRCRAFT_PATH:
                fetch(registry.DB_URL, root / _AIRCRAFT_PATH)
                done = (root / _AIRCRAFT_PATH).exists()
                _set(items, path, "fixed" if done else "manual", AIRCRAFT_FAIL)
            elif path == _REGISTRY_PATH:
                if not (root / _AIRCRAFT_PATH).exists():
                    _set(items, path, "manual", REGISTRY_NO_DB)
                else:
                    status, detail = _registry_step(root, report)
                    _set(items, path, status, detail)
            else:
                _set(items, path, "manual", fallback)
        except Exception as exc:  # ein Item darf setup nicht abbrechen
            _set(items, path, "manual", fallback)
            print(f"setup: {path} fehlgeschlagen ({exc!r})", file=sys.stderr)
    return items, report
