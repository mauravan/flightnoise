"""Baut data/seed/zrh_vbr2012.json aus LBK-ZRH-Aggregaten (verifiziert).

Grossflugzeuge: Tag 320'112, 1. NS 9'125, 2. NS 930; Kleinflugzeuge 20'000 (nur Tag).
Flottenanteile: schwer 12 % (B777-300ER), mittel 50 % (A320-214),
leicht 38 % (E190); Kleinflugzeuge -> C172.
Routen: nominale Platzhalter (eine Departure-/eine Arrival-Gerade je aktiver
Piste 14/16/28/34), "source": "nominal_placeholder". Volle Rechtstreue erfordert
die aus SIL/Betriebsreglement digitalisierten genehmigten Flugrouten —
der Seed dient nur Smoke-Test/Unit-Tests, nicht als Rechtsnachweis.
"""

from __future__ import annotations

import json
from pathlib import Path

AIRPORT = {"airport_icao": "LSZH", "airport_east": 2684000.0, "airport_north": 1256000.0}

# Pistenköpfe grob (LV95, Platzhalter-Geometrie um ARP)
RUNWAYS = {
    "14": (2683500.0, 1255500.0),
    "16": (2684500.0, 1255000.0),
    "28": (2682000.0, 1256500.0),
    "34": (2685000.0, 1257000.0),
}

PERIODS = [
    {"id": "tag", "start_hour": 6, "end_hour": 22},
    {"id": "nacht1", "start_hour": 22, "end_hour": 23},
    {"id": "nacht2", "start_hour": 23, "end_hour": 24},
    {"id": "letzte_nacht", "start_hour": 5, "end_hour": 6},
]

# (ANP-ID, Anteil)
FLEET = [("B777-300ER", 0.12), ("A320-214", 0.50), ("E190", 0.38)]

# Bewegungen Grossflugzeuge je Periode (Jahr)
GROSS = {"tag": 320112, "nacht1": 9125, "nacht2": 930}
KLEIN_TAG = 20000


def _route(rid: str, kind: str, runway: str, share: float) -> dict:
    # Nominale Platzhalter: Gerade nahe ARP, seitlich versetzt (kein Direktüberflug),
    # dicht abgetastet (1 km), damit Empfänger neben der Route realistische Pegel sehen.
    import math
    ex, ny = AIRPORT["airport_east"], AIRPORT["airport_north"]
    headings = {"14": 140.0, "16": 160.0, "28": 280.0, "34": 340.0}
    az = math.radians(headings[runway] + (0.0 if kind == "departure" else 180.0))
    dx, dy = math.sin(az), math.cos(az)
    # Seitlich versetzt: normal zur Richtung, gestaffelt je Piste;
    # DEP-16 in 300 m Seitenlinie am ARP (kein exakter Direktüberflug —
    # Häuser stehen neben, nicht auf dem Lift-off-Punkt).
    off = {"14": 1500.0, "16": 300.0 if kind == "departure" else -1500.0,
           "28": 2000.0, "34": -2000.0}[runway]
    nx, nyy = math.cos(az), -math.sin(az)
    pts = []
    for k in range(17):
        d = -2000.0 + k * 1000.0  # -2 km .. +14 km
        # Bodenrolle bis d=0, danach Steigflug; Überflug ARP (d≈0) in ~400 m
        alt = 0.0 if d <= 0 else 400.0 + max(d, 0.0) * 0.08
        pts.append({
            "east": ex + dx * d + nx * off,
            "north": ny + dy * d + nyy * off,
            "alt_m": alt,
            "thrust": None,
        })
    return {"id": rid, "kind": kind, "runway": runway, "segments": pts, "share": share}


def main() -> None:
    routes = []
    rwy = list(RUNWAYS)
    for i, rw in enumerate(rwy):
        routes.append(_route(f"DEP-{rw}", "departure", rw, 1.0 / len(rwy)))
        routes.append(_route(f"ARR-{rw}", "arrival", rw, 1.0 / len(rwy)))
    movements = []
    for pid, total in GROSS.items():
        for j, (anp, frac) in enumerate(FLEET):
            # Jahresbewegungen dieser Klasse gleichmässig auf alle 8 Routen
            per_route = int(round(total * frac / len(routes)))
            for r in routes:
                movements.append({
                    "route_id": r["id"], "aircraft_anp": anp, "period": pid,
                    "count": per_route, "weight_class": "gross",
                })
    movements.append({
        "route_id": routes[0]["id"], "aircraft_anp": "C172", "period": "tag",
        "count": KLEIN_TAG, "weight_class": "klein",
    })
    doc = {**AIRPORT, "periods": PERIODS, "routes": routes,
           "movements": movements, "source": "nominal_placeholder"}
    out = Path("data/seed/zrh_vbr2012.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=1), encoding="utf-8")
    print(f"wrote {out} ({len(movements)} movements, {len(routes)} routes)")


if __name__ == "__main__":
    main()
