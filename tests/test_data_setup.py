"""Setup-Scan/-Apply: Statuslogik und Registry-Bau (hermetisch, kein Netz)."""

from __future__ import annotations

import gzip
import json
import os
import sqlite3

from click.testing import CliRunner

from fluglaerm.cli import setup
from fluglaerm.data_setup import apply, plan

PATHS = [
    "data/anp/*.json",
    "data/anp.sqlite",
    "data/anp_archive.sqlite",
    "data/anp.sqlite:substitutions",
    "data/seed/zrh_vbr2012.json",
    "data/ch.sqlite",
    "data/aircraft.csv.gz",
    "data/aircraft_registry.json",
    "credentials.json",
]

# eine Zeile, wie load_db sie frisst (icao24;registration;typecode;flags;desc)
DB_ROW = "010204;SU-GFJ;A20N;00;AIRBUS A-320neo;;;\n"


def _by_path(items, path):
    return next(it for it in items if it.path == path)


def _touch(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")


def _write_gz(dest, rows=DB_ROW):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, "wt", encoding="utf-8") as fh:
        fh.write(rows)


def _sqlite(path, ddl, insert=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    try:
        con.execute(ddl)
        if insert:
            con.execute(*insert)
        con.commit()
    finally:
        con.close()


def test_plan_statuses_empty_root(tmp_path):
    items = plan(tmp_path)
    assert [it.path for it in items] == PATHS
    assert [it.status for it in items] == [
        "auto", "manual", "auto", "auto", "manual", "manual", "auto", "auto",
        "manual",
    ]
    assert "easa.europa.eu" in _by_path(items, "data/anp.sqlite").detail
    assert "curl -C -" in _by_path(items, "data/ch.sqlite").detail
    assert "1.7 GB" in _by_path(items, "data/ch.sqlite").detail
    assert [it.status for it in plan(tmp_path, gwr=True)] == [
        "auto", "manual", "auto", "auto", "manual", "auto", "auto", "auto",
        "manual",
    ]


def test_plan_sqlite_auto_when_workbooks_present(tmp_path):
    (tmp_path / "data/easa_anp").mkdir(parents=True)
    (tmp_path / "data/easa_anp" / "Aircraft.xlsx").write_text("x")
    item = _by_path(plan(tmp_path), "data/anp.sqlite")
    assert item.status == "auto"
    assert "import_anp.py" in item.detail


def test_plan_all_present(tmp_path):
    for p in ("data/anp/A320-214.json",
              "data/seed/zrh_vbr2012.json", "data/ch.sqlite",
              "data/aircraft.csv.gz"):
        _touch(tmp_path / p)
    _sqlite(tmp_path / "data/anp.sqlite",
            "CREATE TABLE substitutions (icao_code TEXT, acft_id TEXT,"
            " delta_dep_db REAL, delta_app_db REAL, PRIMARY KEY (icao_code, acft_id))",
            ("INSERT INTO substitutions VALUES ('A320','A320-211',0.2,0.0)",))
    _sqlite(tmp_path / "data/anp_archive.sqlite",
            "CREATE TABLE aircraft (acft_id TEXT)",
            ("INSERT INTO aircraft VALUES ('A320-211')",))
    _touch(tmp_path / "data/aircraft_registry.json")
    (tmp_path / "data/aircraft_registry.json").write_text(
        json.dumps({"010204": "A320-250N"}), encoding="utf-8"
    )
    os.utime(tmp_path / "data/aircraft.csv.gz", (1_000_000, 1_000_000))
    _touch(tmp_path / "credentials.json")
    items = plan(tmp_path)
    assert [it.status for it in items] == ["ok"] * 9
    assert all(it.detail == "" for it in items)


def test_plan_registry_rebuild_when_db_newer(tmp_path):
    _touch(tmp_path / "data/aircraft.csv.gz")
    _touch(tmp_path / "data/aircraft_registry.json")
    os.utime(tmp_path / "data/aircraft.csv.gz", (2_000_000_000, 2_000_000_000))
    item = _by_path(plan(tmp_path), "data/aircraft_registry.json")
    assert item.status == "auto"
    assert item.detail == "Registry bauen aus data/aircraft.csv.gz"


def test_apply_runs_only_provisionable_steps(tmp_path):
    seen: list[str] = []

    def run_script(rel):
        seen.append(rel)
        if rel == "data/anp/make_placeholders.py":
            _touch(tmp_path / "data/anp/B777-300ER.json")
        return True, ""

    def download(url, dest):
        _write_gz(dest)

    def download_gwr(url, dest):
        _touch(dest)

    items, report = apply(
        tmp_path, gwr=True,
        run_script=run_script, download=download, download_gwr=download_gwr,
    )
    assert seen == ["data/anp/make_placeholders.py", "data/import_anp_archive.py"]
    assert report == []
    assert _by_path(items, "data/anp/*.json").status == "fixed"
    assert _by_path(items, "data/aircraft.csv.gz").status == "fixed"
    assert _by_path(items, "data/ch.sqlite").status == "fixed"
    assert _by_path(items, "data/anp.sqlite").status == "manual"
    assert _by_path(items, "data/anp_archive.sqlite").status == "manual"
    sub = _by_path(items, "data/anp.sqlite:substitutions")
    assert sub.status == "manual"
    assert "ANP-Datenbank fehlt" in sub.detail
    assert _by_path(items, "data/aircraft_registry.json").status == "fixed"


def test_apply_registry_builds_full_map(tmp_path):
    _write_gz(tmp_path / "data/aircraft.csv.gz",
              DB_ROW + "aabbcc;HB-AFE;B738;00;BOEING 737-800;;;\n")

    items, report = apply(
        tmp_path, download=lambda url, dest: _touch(dest)
    )
    reg = _by_path(items, "data/aircraft_registry.json")
    assert reg.status == "fixed"
    assert report == ["1 x B738 — keine ANP-Entsprechung"]
    assert json.loads(
        (tmp_path / "data/aircraft_registry.json").read_text(encoding="utf-8")
    ) == {"010204": "A320-250N"}

    # zweiter Lauf ohne DB-Änderung → idempotent, Datei unberührt
    mtime = (tmp_path / "data/aircraft_registry.json").stat().st_mtime
    items2, report2 = apply(
        tmp_path, download=lambda url, dest: _touch(dest)
    )
    reg2 = _by_path(items2, "data/aircraft_registry.json")
    assert reg2.status == "ok"
    # frische Registry: plan meldet ok, der Schritt läuft gar nicht
    assert reg2.detail == ""
    assert report2 == []
    assert (tmp_path / "data/aircraft_registry.json").stat().st_mtime == mtime


def test_apply_registry_all_unmapped_writes_nothing(tmp_path):
    _write_gz(tmp_path / "data/aircraft.csv.gz",
              "aabbcc;HB-AFE;B738;00;BOEING 737-800;;;\n")

    items, report = apply(
        tmp_path, download=lambda url, dest: _touch(dest)
    )
    reg = _by_path(items, "data/aircraft_registry.json")
    assert reg.status == "manual"
    assert report == ["1 x B738 — keine ANP-Entsprechung"]
    assert not (tmp_path / "data/aircraft_registry.json").exists()


def test_apply_manual_when_curl_missing(tmp_path, monkeypatch):
    import fluglaerm.data_setup as ds

    monkeypatch.setattr(ds.shutil, "which", lambda _name: None)
    items, _ = apply(
        tmp_path, gwr=True,
        run_script=lambda rel: (True, ""),
        download=lambda url, dest: _touch(dest),
    )
    ch = _by_path(items, "data/ch.sqlite")
    assert ch.status == "manual"
    assert "curl -C -" in ch.detail
    assert not (tmp_path / "data/ch.sqlite").exists()


def test_cli_check_mode_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENSKY_CLIENT_ID", raising=False)
    monkeypatch.delenv("OPENSKY_CLIENT_SECRET", raising=False)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(setup, ["--check"])
    assert result.exit_code == 1
    assert "easa.europa.eu" in result.output
    assert "curl -C -" in result.output
    assert "Registry bauen aus data/aircraft.csv.gz" in result.output
    assert "data/anp_archive.sqlite" in result.output
    assert "data/anp.sqlite:substitutions" in result.output
    assert "nichts verändert" in result.output
    assert not (tmp_path / "data/anp").exists()
    assert not (tmp_path / "data/aircraft.csv.gz").exists()
