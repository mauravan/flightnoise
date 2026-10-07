"""Ist-Lärm-Auswertung: Leq aus echten ADS-B-Spuren (informativ!).

Jede Track-Position wird als Segment-Überflug mit Standardprofil gewertet;
SEL via engine.npd.segment_sel, Leq über period_s aggregiert.

label: "informativ, nicht rechtsgültig (Ist-Verkehr, keine Anhang-5-Korrektur)"
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from fluglaerm.common.geo import lateral_offset_m, slant_m
from fluglaerm.common.types import Receiver
from fluglaerm.engine import acoustic as ac
from fluglaerm.engine.npd import segment_sel
from fluglaerm.ist_laerm.track import Track

IST_LABEL = "informativ, nicht rechtsgültig (Ist-Verkehr, keine Anhang-5-Korrektur)"

# Fallback-Typ wenn aircraft_type unbekannt (Mittelklasse, klar dokumentiert)
FALLBACK_ANP = "A320-214"


@dataclass
class IstResult:
    leq: float
    n_flights: int
    label: str = IST_LABEL


def evaluate_ist(
    receiver: Receiver,
    tracks: list[Track],
    period_s: float,
    data_dir: str = "data/anp",
) -> IstResult:
    sels: list[float] = []
    for t in tracks:
        anp = t.aircraft_type if t.aircraft_type != "UNKNOWN" else FALLBACK_ANP
        for p in t.positions:
            slant = max(
                slant_m(p.east, p.north, p.alt_m, receiver.east, receiver.north,
                        receiver.height_m), 1.0
            )
            elev = math.degrees(
                math.asin(min(max(p.alt_m - receiver.height_m, 0.0) / slant, 1.0))
            )
            lat = lateral_offset_m(p.east, p.north, receiver.east, receiver.north,
                                   p.track_deg)
            try:
                sel = segment_sel(anp, "departure", 0.55, slant,
                                  max(p.speed_kn, 50.0), elev, lat, data_dir)
            except FileNotFoundError:
                sel = segment_sel(FALLBACK_ANP, "departure", 0.55, slant,
                                  max(p.speed_kn, 50.0), elev, lat, data_dir)
            sels.append(sel)
    leq = ac.accumulate_leq(sels, period_s)
    return IstResult(leq=leq, n_flights=len(tracks))
