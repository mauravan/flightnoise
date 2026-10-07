"""Track-Aufbau aus OpenSky-States: nach icao24 gruppieren, nach Zeit sortieren."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from fluglaerm.common.geo import wgs84_to_lv95


@dataclass
class Position:
    ts: int
    east: float
    north: float
    alt_m: float
    speed_kn: float
    track_deg: float


@dataclass
class Track:
    icao24: str
    callsign: str
    aircraft_type: str  # ANP-ID; "UNKNOWN" wenn nicht bestimmbar
    positions: list[Position] = field(default_factory=list)


def build_tracks(
    states: list[dict],
    rec_east: float,
    rec_north: float,
    max_dist_m: float = 30_000.0,
    type_by_icao24: dict[str, str] | None = None,
) -> list[Track]:
    """Gruppiert States nach icao24; verwirft Spuren ohne Receiver-Nähe."""
    grouped: dict[str, list[dict]] = {}
    for s in states:
        if s.get("latitude") is None or s.get("longitude") is None:
            continue
        grouped.setdefault(str(s["icao24"]), []).append(s)
    out: list[Track] = []
    for icao24, rows in grouped.items():
        rows.sort(key=lambda r: (r.get("time_position") or r.get("last_contact") or 0))
        positions: list[Position] = []
        near = False
        for r in rows:
            e, n = wgs84_to_lv95(r["longitude"], r["latitude"])
            alt = r.get("geo_altitude") or r.get("baro_altitude") or 0.0
            if math.hypot(e - rec_east, n - rec_north) <= max_dist_m:
                near = True
            v_ms = r.get("velocity") or 0.0
            positions.append(
                Position(
                    ts=int(r.get("time_position") or r.get("last_contact") or 0),
                    east=e,
                    north=n,
                    alt_m=float(alt),
                    speed_kn=float(v_ms) * 1.94384,
                    track_deg=float(r.get("true_track") or 0.0),
                )
            )
        if not near:
            continue
        callsign = (rows[-1].get("callsign") or "").strip()
        atyp = (type_by_icao24 or {}).get(icao24, "UNKNOWN")
        out.append(Track(icao24=icao24, callsign=callsign, aircraft_type=atyp,
                         positions=positions))
    return out
