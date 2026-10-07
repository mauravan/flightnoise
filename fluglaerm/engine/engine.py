"""Engine: genehmigter Flugbetrieb -> Lrt/Lrn, Status, AGL-Lage.

Modell: Jede Movement zählt `count` identische Überflüge AUF IHRER Route
(count ist massgeblich je Route; Route.share nur Doku des Routensplits).
Pro Überflug wird je Routensegment ein SEL via npd.segment_sel berechnet
(Näherung: Empfänger-Geometrie zum Segment-Vertex), die SEL werden je
Periode energetisch zu Leq aggregiert.

Jahresmittel (LSV Anhang 5: Beurteilungspegel = Jahresmittel; Datensatz-
Counts sind Jahresbewegungen): T_tag = 16h*365, T_Nachtstunde = 1h*365.
Letzte Nachtstunde ZRH geschlossen -> kein Wert (minus unendlich).

AGL-Lage (zentral hier): "innerhalb" gdw. lrt > 60 oder lrn["nacht1"] > 55
(IGW ES II).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from fluglaerm.common.geo import lateral_offset_m, slant_m
from fluglaerm.common.types import MovementDataset, Receiver
from fluglaerm.engine import acoustic as ac
from fluglaerm.engine.anhang5 import grenzwert_status
from fluglaerm.engine.npd import finite_segment_correction, interp_npd, load_npd, segment_sel

DAYS_PER_YEAR = 365
PERIOD_SECONDS = {
    "tag": 16 * 3600 * DAYS_PER_YEAR,
    "nacht1": 3600 * DAYS_PER_YEAR,
    "nacht2": 3600 * DAYS_PER_YEAR,
    "letzte_nacht": 3600 * DAYS_PER_YEAR,
}

# Flugphasen-Defaults je Routenart: (thrust_frac, speed_kn)
PHASE_DEFAULTS = {
    "departure": (0.85, 200.0),
    "arrival": (0.35, 160.0),
}


@dataclass
class EngineResult:
    lrt: float
    lrn: dict[str, float]
    lrk: float
    lrg: float
    status: dict[str, str]  # periode -> Statusstring
    agl: str  # "innerhalb" | "ausserhalb"


def _sel_for_movement(
    aircraft_anp: str,
    route_kind: str,
    s1: object,
    s2: object,
    receiver: Receiver,
) -> float:
    # Stück S1->S2 (Höhe linear); Sp = Fusspunkt auf verlängerter Gerade (Fig. 4-2).
    # Reine Bodenrolle (beide Enden alt ≤ 0): kein Beitrag (SOR-Direktivität
    # ausserhalb Scope; Doc 29 §§ 4.5.6–4.5.7).
    if s1.alt_m <= 0.0 and s2.alt_m <= 0.0:
        return float("-inf")
    thrust_frac, speed_kn = PHASE_DEFAULTS[route_kind]
    if s1.thrust is not None:
        thrust_frac = s1.thrust
    vx, vy = s2.east - s1.east, s2.north - s1.north
    seg_len = max(math.hypot(vx, vy), 1e-6)
    rx, ry = receiver.east - s1.east, receiver.north - s1.north
    q = (rx * vx + ry * vy) / seg_len  # S1->Sp entlang Segment (kann ausserhalb liegen)
    t = min(max(q / seg_len, 0.0), 1.0)
    cx, cy = s1.east + vx * t, s1.north + vy * t
    alt_c = max(s1.alt_m, 0.0) + (max(s2.alt_m, 0.0) - max(s1.alt_m, 0.0)) * t
    slant = max(
        slant_m(cx, cy, alt_c, receiver.east, receiver.north, receiver.height_m), 1.0
    )
    elev_deg = math.degrees(
        math.asin(min(max(alt_c - receiver.height_m, 0.0) / slant, 1.0))
    )
    az = math.degrees(math.atan2(vx, vy))
    lat = lateral_offset_m(cx, cy, receiver.east, receiver.north, az)
    # NPD-Baseline am Fusspunkt + ΔF (4-20) mit LE∞/Lmax am dp
    table = load_npd(aircraft_anp)
    power = max(thrust_frac, 0.0) * table.max_thrust_lbf
    base_le, base_lmax = interp_npd(table, power, slant)
    d_f = finite_segment_correction(q, seg_len, base_le, base_lmax)
    return segment_sel(
        aircraft_anp, route_kind, thrust_frac, slant, speed_kn, elev_deg, lat,
        delta_f=d_f,
    )


def evaluate(dataset: MovementDataset, receiver: Receiver) -> EngineResult:
    routes = {r.id: r for r in dataset.routes}
    # SEL-Listen je Periode, getrennt nach Gewichtsklasse
    sel_gross: dict[str, list[float]] = {p: [] for p in PERIOD_SECONDS}
    sel_klein: list[float] = []
    n_klein = 0

    for m in dataset.movements:
        route = routes[m.route_id]
        segs = route.segments
        for i in range(len(segs) - 1):
            sel = _sel_for_movement(m.aircraft_anp, route.kind, segs[i], segs[i + 1], receiver)
            # count = Anzahl Überflüge AUF DIESER Route (massgeblich je Movement)
            n_eff = max(float(m.count), 0.0)
            sel_scaled = sel + 10.0 * math.log10(n_eff) if n_eff > 0 else float("-inf")
            if m.weight_class == "klein":
                if m.period == "tag":
                    sel_klein.append(sel_scaled)
            else:
                if m.period in sel_gross:
                    sel_gross[m.period].append(sel_scaled)
        if m.weight_class == "klein" and m.period == "tag":
            n_klein += int(m.count)

    leq_gross_tag = ac.accumulate_leq(sel_gross["tag"], PERIOD_SECONDS["tag"])
    # Kleinflugzeuge nur Tag 06–20 (14 h): T_klein = 14h*365
    leq_klein_tag = ac.accumulate_leq(sel_klein, 14 * 3600 * DAYS_PER_YEAR)
    lrk = ac.klein_lrk(leq_klein_tag, n_klein) if sel_klein else float("-inf")
    lrg = leq_gross_tag
    lrt = ac.gesamt_lrt(lrk, lrg) if sel_klein else lrg

    lrn: dict[str, float] = {}
    for pid in ("nacht1", "nacht2"):
        lrn[pid] = ac.accumulate_leq(sel_gross.get(pid, []), PERIOD_SECONDS[pid])

    es = receiver.es
    status = {
        "tag": grenzwert_status(lrt, es, "tag", "lrt"),
        "nacht1": grenzwert_status(lrn["nacht1"], es, "nacht1", "lrn"),
        "nacht2": grenzwert_status(lrn["nacht2"], es, "nacht2", "lrn"),
    }
    agl = (
        "innerhalb"
        if (lrt > 60 or lrn.get("nacht1", float("-inf")) > 55)
        else "ausserhalb"
    )
    return EngineResult(lrt=lrt, lrn=lrn, lrk=lrk, lrg=lrg, status=status, agl=agl)
