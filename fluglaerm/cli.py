"""CLI: parcel (voller Nachweis), engine, ist."""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime
from pathlib import Path

import click

from fluglaerm.common.geo import lv95_to_wgs84, resolve_egrid, resolve_height
from fluglaerm.common.types import MovementDataset, Receiver
from fluglaerm.data_setup import apply, plan
from fluglaerm.engine.engine import evaluate
from fluglaerm.ist_laerm.ist import evaluate_ist
from fluglaerm.anp_db import AnpDatabase
from fluglaerm.ist_laerm.opensky import OpenSkyClient, load_credentials
from fluglaerm.ist_laerm.own import evaluate_own, format_own_header, format_own_row
from fluglaerm.ist_laerm.report import render_own_report
from fluglaerm.ist_laerm.registry import load_db
from fluglaerm.ist_laerm.collect import StateStore, collect_once, import_history
from fluglaerm.ist_laerm.track import build_tracks
from fluglaerm.report.report import render_json, render_markdown

_LSZH_ARP_EAST = 2684000.0
_LSZH_ARP_NORTH = 1256000.0


def _receiver_position(egrid, east, north, height, airport_east, airport_north):
    if egrid:
        try:
            e, n = resolve_egrid(egrid)
            dh = resolve_height(e, n) - resolve_height(airport_east, airport_north)
        except ValueError as exc:
            raise click.ClickException(str(exc))
        return e, n, height + dh
    if east is None or north is None:
        raise click.UsageError("Entweder --egrid oder --east UND --north angeben.")
    return east, north, height


def load_dataset(path: str) -> tuple[MovementDataset, bool]:
    from fluglaerm.common.types import Movement, Period, Route, Segment

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    ds = MovementDataset(
        airport_icao=raw["airport_icao"],
        airport_east=raw["airport_east"],
        airport_north=raw["airport_north"],
        periods=[Period(**p) for p in raw.get("periods", [])],
        routes=[
            Route(
                id=r["id"], kind=r["kind"], runway=r["runway"], share=r["share"],
                segments=[Segment(**s) for s in r["segments"]],
            )
            for r in raw.get("routes", [])
        ],
        movements=[Movement(**m) for m in raw.get("movements", [])],
    )
    nominal = raw.get("source") == "nominal_placeholder"
    return ds, nominal


@click.group()
def cli() -> None:
    """Fluglärm-Rechner: Engine (genehmigt) + Ist-Modul (informativ) + Daten-Setup."""


@cli.command()
@click.option("--east", type=float, default=None)
@click.option("--north", type=float, default=None)
@click.option("--es", type=click.IntRange(1, 4), required=True)
@click.option("--nutzung", type=click.Choice(["wohnen", "betrieb"]), required=True)
@click.option("--dataset", default="data/seed/zrh_vbr2012.json")
@click.option("--ist/--no-ist", default=False)
@click.option("--egrid", default=None)
@click.option("--height", type=float, default=0.0, help="Empfängerhöhe über Flughafen-Grund (m)")
def engine(east, north, es, nutzung, dataset, ist, egrid, height):
    """Nur Engine: Lrt/Lrn, Status, AGL."""
    ds, _ = load_dataset(dataset)
    east, north, height_m = _receiver_position(egrid, east, north, height, ds.airport_east, ds.airport_north)
    res = evaluate(ds, Receiver(east=east, north=north, es=es, nutzung=nutzung, height_m=height_m))
    click.echo(f"Lrt={res.lrt:.1f} dB [{res.status['tag']}]")
    for pid, v in res.lrn.items():
        click.echo(f"Lrn[{pid}]={v:.1f} dB [{res.status.get(pid)}]")
    click.echo(f"Lrk={res.lrk:.1f} Lrg={res.lrg:.1f} AGL={res.agl}")


@cli.command()
@click.option("--east", type=float, default=None)
@click.option("--north", type=float, default=None)
@click.option("--from", "from_iso", required=True, help="ISO-Start, z.B. 2026-10-01T00:00")
@click.option("--to", "to_iso", required=True)
@click.option("--username", default=None)
@click.option("--password", default=None)
@click.option("--height", type=float, default=0.0, help="Empfängerhöhe über Flughafen-Grund (m)")
@click.option("--egrid", default=None)
def ist(east, north, from_iso, to_iso, username, password, height, egrid):
    """Nur Ist-Modul: Live-Fenster (15 min) oder History mit Konto."""
    east, north, height_m = _receiver_position(egrid, east, north, height, _LSZH_ARP_EAST, _LSZH_ARP_NORTH)
    try:
        t0 = datetime.fromisoformat(from_iso).timestamp()
        t1 = datetime.fromisoformat(to_iso).timestamp()
    except ValueError:
        raise click.BadParameter("ISO-Format erwartet, z.B. 2026-10-01T00:00.", param_hint="--from/--to")
    client = OpenSkyClient(username, password)
    receiver = Receiver(east=east, north=north, es=2, nutzung="wohnen", height_m=height_m)
    lon, lat = lv95_to_wgs84(east, north)
    # 30-km-Box (Grad-Näherung)
    states = client.bbox_states(lat - 0.27, lon - 0.42, lat + 0.27, lon + 0.42)
    tracks = build_tracks(states, east, north)
    res = evaluate_ist(receiver, tracks, max(t1 - t0, 900.0))
    click.echo(f"Leq_ist={res.leq:.1f} dB aus {res.n_flights} Flügen")
    click.echo(res.label)


@cli.command()
@click.option("--east", type=float, default=None)
@click.option("--north", type=float, default=None)
@click.option("--es", type=click.IntRange(1, 4), required=True)
@click.option("--nutzung", type=click.Choice(["wohnen", "betrieb"]), required=True)
@click.option("--ist/--no-ist", default=False)
@click.option("--dataset", default="data/seed/zrh_vbr2012.json")
@click.option("--egrid", default=None)
@click.option("--height", type=float, default=0.0, help="Empfängerhöhe über Flughafen-Grund (m)")
def parcel(east, north, es, nutzung, ist, dataset, egrid, height):
    """Voller Nachweis: Engine + optionaler Ist-Abgleich; schreibt nachweis.md + result.json."""
    ds, nominal = load_dataset(dataset)
    east, north, height_m = _receiver_position(egrid, east, north, height, ds.airport_east, ds.airport_north)
    receiver = Receiver(east=east, north=north, es=es, nutzung=nutzung, height_m=height_m)
    eng = evaluate(ds, receiver)
    ist_res = None
    if ist:
        lon, lat = lv95_to_wgs84(east, north)
        client = OpenSkyClient()
        states = client.bbox_states(lat - 0.27, lon - 0.42, lat + 0.27, lon + 0.42)
        tracks = build_tracks(states, east, north)
        ist_res = evaluate_ist(receiver, tracks, 900.0)
    md = render_markdown(eng, ist_res, receiver, nominal=nominal, egrid=egrid)
    js = render_json(eng, ist_res, receiver, nominal=nominal)
    Path("nachweis.md").write_text(md, encoding="utf-8")
    Path("result.json").write_text(js, encoding="utf-8")
    click.echo(md)


@cli.command()
@click.option("--egrid", default=None)
@click.option("--east", type=float, default=None)
@click.option("--north", type=float, default=None)
@click.option("--height", type=float, default=0.0, help="Empfängerhöhe über Flughafen-Grund (m)")
@click.option("--radius", type=float, default=15000.0, help="Suchradius um den Empfänger (m)")
@click.option("--serials", type=int, multiple=True, help="Empfänger-Seriennummer(n); ohne Angabe alle eigenen")
@click.option("--time", "time_", type=int, default=None, help="Unix-Zeit (Default: jetzt)")
@click.option("--window", type=int, default=0, help="Fenster in Sekunden (0 = nur aktueller Stand)")
@click.option("--interval", type=int, default=60, help="Abtast-Intervall des Backfills in Sekunden")
@click.option("--db", default="data/anp.sqlite")
@click.option("--registry", default="data/aircraft_registry.json")
@click.option("--es", type=click.IntRange(1, 4), default=2,
              help="Empfindlichkeitsstufe 1–4 (Default 2)")
@click.option("--nutzung", type=click.Choice(["wohnen", "betrieb"]), default="wohnen",
              help="Nutzung (Default wohnen)")
@click.option("--client-id", default=None, envvar="OPENSKY_CLIENT_ID")
@click.option("--client-secret", default=None, envvar="OPENSKY_CLIENT_SECRET")
@click.option("--source", type=click.Choice(["opensky", "local"]), default="opensky",
              help="States-Quelle: opensky (live) oder local (SQLite-Historie; window=0 lädt die letzten interval Sekunden, --serials wird ignoriert)")
@click.option("--states-db", default="data/own_states.sqlite", help="Lokale States-DB (nur mit --source local)")
@click.option("--credentials", default=None, help="JSON-Datei mit clientId/clientSecret (statt --client-id/--client-secret bzw. Env)")
@click.option("--debug", is_flag=True, help="Debug-Logging auf stderr")
@click.option("--list-aircraft", is_flag=True, help="ANP-Flugzeuge (acft_id, Typ, Triebwerke) ausgeben und beenden")
@click.option("--output", "output_path", default=None,
              type=click.Path(dir_okay=False, writable=True),
              help="Report-Datei (Markdown) mit Tabelle + Herleitung je Flugzeug")
def own(egrid, east, north, height, radius, serials, time_, window, interval, db, registry, es, nutzung, client_id, client_secret, credentials, debug, list_aircraft, output_path, source, states_db):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
        logging.getLogger("urllib3").setLevel(logging.WARNING)
    log = logging.getLogger("fluglaerm.cli")
    if window < 0:
        raise click.UsageError("--window muss >= 0 sein")
    if window > 0 and interval < 5:
        raise click.UsageError("--interval muss mindestens 5 s sein (API-Zeitauflösung)")
    log.debug(
        "own: egrid=%s east=%s north=%s height=%s radius=%.0f serials=%s time=%s "
        "window=%s interval=%s db=%s registry=%s es=%s nutzung=%s credentials=%s",
        egrid, east, north, height, radius, list(serials) or None, time_,
        window, interval, db, registry, es, nutzung, credentials,
    )
    if list_aircraft:
        try:
            dbh = AnpDatabase(db)
        except FileNotFoundError as exc:
            raise click.ClickException(str(exc))
        import sqlite3

        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        for r in con.execute("SELECT acft_id, description, number_of_engines, max_sea_level_static_thrust_lb FROM aircraft ORDER BY acft_id"):
            click.echo(f"{r[0]} {r[1]} {r[2]} Triebwerke {r[3]} lb")
        return
    east, north, height_m = _receiver_position(egrid, east, north, height, _LSZH_ARP_EAST, _LSZH_ARP_NORTH)
    log.debug("Empfänger: E=%.1f N=%.1f h=%.1f m (LSZH-ARP E=%.0f N=%.0f)",
              east, north, height_m, _LSZH_ARP_EAST, _LSZH_ARP_NORTH)
    p = Path(registry)
    if not p.exists():
        raise click.ClickException(f"Registry nicht gefunden: {registry}")
    reg = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(reg, dict):
        raise click.ClickException(f"Registry {registry} muss ein JSON-Objekt sein")
    log.debug("Registry %s: %d Einträge", registry, len(reg))
    end = time_ or int(time.time())
    if source == "local":
        store = StateStore(states_db)
        if not Path(states_db).exists():
            raise click.ClickException(f"States-DB nicht gefunden: {states_db} "
                                       f"(erst mit 'fluglaerm collect --host HOST' füllen)")
        eff_window = window if window > 0 else interval
        states = store.states_between(end - eff_window, end)
        log.debug("lokale States-DB %s: %d States (Fenster %d s)", states_db, len(states), eff_window)
    else:
        if credentials:
            if not client_id or not client_secret:
                try:
                    file_id, file_secret = load_credentials(credentials)
                except ValueError as exc:
                    raise click.ClickException(str(exc))
                client_id = client_id or file_id
                client_secret = client_secret or file_secret
        log.debug(
            "Credentials: client_id=%s Quelle=%s",
            client_id or "-",
            "Option/Env" if client_id else "keine (own_states wird abbrechen)",
        )
        client = OpenSkyClient(client_id, client_secret)
        start = end - window
        try:
            if window > 0:
                states = client.own_history(start, end, interval, list(serials) or None)
            else:
                states = client.own_states(list(serials) or None, time_)
        except ValueError as exc:
            raise click.ClickException(str(exc))
    if not states:
        log.debug("keine States → Abbruch")
        return
    try:
        dbh = AnpDatabase.with_archive(db)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))
    log.debug("ANP-DB %s geöffnet", db)
    tracks = build_tracks(states, east, north, max_dist_m=radius, type_by_icao24=reg)
    log.debug("build_tracks: %d States → %d Tracks (radius %.0f m)",
              len(states), len(tracks), radius)
    unknown_hexes = {t.icao24 for t in tracks if t.icao24 not in reg}
    aircraft_db = None
    if unknown_hexes:
        adb = p.with_name("aircraft.csv.gz")
        if adb.exists():
            aircraft_db = load_db(adb)
            log.debug("Flugzeug-DB %s: %d Zeilen (%d unbekannte Hex-IDs)",
                      adb, len(aircraft_db), len(unknown_hexes))
    receiver = Receiver(east=east, north=north, es=es, nutzung=nutzung, height_m=height_m)
    res = evaluate_own(receiver, tracks, dbh, reg, peak=window > 0,
                       aircraft_db=aircraft_db)
    click.echo(format_own_header())
    for r in res.rows:
        click.echo(format_own_row(r))
    for s in res.substituted:
        click.echo(f"ersetzt: {s}")
    for u in res.unknown:
        click.echo(f"unbekannt: {u}")
    for s in res.skipped:
        click.echo(f"übersprungen: {s}")
    click.echo(f"L_jetzt={res.level_db:.1f} dB aus {len(res.rows)} Flugzeugen")
    click.echo(res.label)

    def _fmt_db(v: float) -> str:
        return "−∞" if v == float("-inf") else f"{v:.1f}"
    click.echo("")
    click.echo("Beurteilungspegel (Ist-Beobachtung, kein Jahresmittel)")
    click.echo(f"ES {receiver.es} ({receiver.nutzung})")
    click.echo(f"Lrt (Tag):   {_fmt_db(res.lrt)} — {res.status.get('tag', '—')}")
    click.echo(f"Lrn (nacht1): {_fmt_db(res.lrn.get('nacht1', float('-inf')))} — {res.status.get('nacht1', '—')}")
    click.echo(f"Lrn (nacht2): {_fmt_db(res.lrn.get('nacht2', float('-inf')))} — {res.status.get('nacht2', '—')}")
    click.echo(f"Lrk: {_fmt_db(res.lrk)}   Lrg: {_fmt_db(res.lrg)}")
    click.echo(f"Klein: {res.n_klein}   Gross: {res.n_gross}")
    if output_path:
        report = render_own_report(res, receiver, db_path=db, registry_path=registry,
                                   radius=radius, window=window)
        Path(output_path).write_text(report, encoding="utf-8")
        click.echo(f"Report geschrieben: {output_path}")


@cli.command()
@click.option("--host", required=True, help="Feeder-Host (IP oder mDNS-Name)")
@click.option("--port", type=int, default=8080)
@click.option("--db", default="data/own_states.sqlite")
@click.option("--interval", type=click.IntRange(1, None), default=5, help="Abtast-Intervall in Sekunden")
@click.option("--duration", type=float, default=None, help="Gesamtlaufzeit in Sekunden (Default: endlos bis Ctrl-C)")
@click.option("--once", is_flag=True, help="Einmal abfragen, speichern, beenden (für cron/launchd)")
@click.option("--debug", is_flag=True, help="Debug-Logging auf stderr")
def collect(host, port, db, interval, duration, once, debug):
    """tar1090-Feeder abtasten und States in die lokale SQLite-Historie schreiben."""
    import requests

    if debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    log = logging.getLogger("fluglaerm.cli")
    store = StateStore(db)
    store.init_schema()
    log.info("sammle von http://%s:%d/data/aircraft.json -> %s (Intervall %d s%s)",
             host, port, db, interval,
             ", einmalig" if once else (f", Dauer {duration:g} s" if duration is not None else ", endlos bis Ctrl-C"))
    snapshots, n_hist = import_history(store, host, port)
    log.info("History-Backfill: %d Snapshots, %d States gespeichert", snapshots, n_hist)
    if once:
        try:
            n = collect_once(store, host, port)
        except requests.RequestException as exc:
            raise click.ClickException(f"Feeder nicht erreichbar: {exc}")
        log.info("%d States gespeichert", n)
        click.echo(f"{n} States gespeichert")
        return
    t0 = time.monotonic()
    total = 0
    rounds = 0
    try:
        while duration is None or time.monotonic() - t0 < duration:
            try:
                n = collect_once(store, host, port)
                total += n
                rounds += 1
                log.info("%d States gespeichert (Abfrage %d, gesamt %d)", n, rounds, total)
            except requests.RequestException as exc:
                log.warning("Feeder nicht erreichbar: %s", exc)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    log.info("fertig: %d Abfragen, %d States gespeichert", rounds, total)


@cli.command()
@click.option("--check", is_flag=True,
              help="Nur prüfen und berichten, nichts anlegen oder laden")
@click.option("--gwr", is_flag=True,
              help="data/ch.sqlite (1.7 GB, nur für --egrid) mitladen")
def setup(check, gwr):
    """Daten-Setup: alles automatisch bereitstellen, was geht; sonst sagen woher."""
    root = Path(".")
    if check:
        items, report = plan(root, gwr), []
    else:
        items, report = apply(root, gwr)
    for it in items:
        click.echo(f"[{it.status:>6}]  {it.path:<32} {it.name}"
                   + (f" — {it.detail}" if it.detail else ""))
    manual = [it for it in items if it.status == "manual"]
    for line in report:
        click.echo(line)
    n_ok = sum(1 for it in items if it.status in ("ok", "fixed"))
    click.echo(f"Setup: {n_ok}/{len(items)} bereit, {len(manual)} manuell"
               + (" (--check: nichts verändert)" if check else ""))
    if manual:
        click.get_current_context().exit(1)


def main() -> None:
    cli()
