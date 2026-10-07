"""CLI: parcel (voller Nachweis), engine, ist."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import click

from fluglaerm.common.geo import lv95_to_wgs84, resolve_egrid, resolve_height
from fluglaerm.common.types import MovementDataset, Receiver
from fluglaerm.engine.engine import evaluate
from fluglaerm.ist_laerm.ist import evaluate_ist
from fluglaerm.ist_laerm.opensky import OpenSkyClient
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
    """Fluglärm-Rechner: Engine (genehmigt) + Ist-Modul (informativ)."""


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


def main() -> None:
    cli()
