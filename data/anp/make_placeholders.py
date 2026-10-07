"""Erzeugt SYNTHETIC_PLACEHOLDER-NPD-Tabellen für Smoke-Tests/Unit-Tests.

Runde Beispielwerte (monoton fallend in d, steigend in P), KEINE echten ANP-Daten.
Ergebnisse damit sind Methodendemonstration, nicht rechtsgültig.
Echte Tabellen: via data/fetch_anp.py anfordern, Schema s. dort.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

OUT_DIR = "data/anp"  # relativ zu Projektwurzel beim Aufruf von dort

# Standard-NPD-Distanzen (ft) wie in ANP-Tabellen
DIST_FT = [200, 400, 630, 1000, 2000, 4000, 6300, 10000, 16000, 25000]
FT_TO_M = 0.3048

TYPES = {
    # anp-id: (max_thrust_lbf, C_offset, engine_mount)
    # C so kalibriert, dass der Seed am ARP Lrt ≈ 60–65 dB erreicht
    # (Grössenordnung publizierter vBR-2012-Kurven). KEINE echten ANP-Daten —
    # echte Tabellen via data/fetch_anp.py ersetzen diesen Platzhalter.
    "B777-300ER": (115000.0, 115.6, "wing"),  # schwer (repräsentativ)
    "A320-214": (27000.0, 113.0, "wing"),  # mittel (repräsentativ)
    "E190": (20300.0, 108.6, "wing"),  # leicht (repräsentativ)
    "C172": (1600.0, 95.0, "prop"),  # Kleinluftfahrzeug (repräsentativ)
}

THRUST_FRACS = [0.15, 0.35, 0.55, 0.75, 1.0]


def le_value(c: float, power_lbf: float, dist_m: float) -> float:
    return c + 8.0 * math.log10(power_lbf) - 20.0 * math.log10(dist_m) - 0.0008 * dist_m


def main() -> None:
    out = Path("data/anp")
    out.mkdir(parents=True, exist_ok=True)
    distances_m = [round(f * FT_TO_M, 2) for f in DIST_FT]
    for name, (pmax, c, mount) in TYPES.items():
        powers = [round(pmax * f, 1) for f in THRUST_FRACS]
        le = [[round(le_value(c, p, d), 2) for d in distances_m] for p in powers]
        lmax = [[round(v - 8.0, 2) for v in row] for row in le]
        doc = {
            "aircraft": name,
            "source": "SYNTHETIC_PLACEHOLDER",
            "engine_mount": mount,
            "max_thrust_lbf": pmax,
            "ref_speed_kn": 160,
            "powers_lbf": powers,
            "distances_m": distances_m,
            "le": le,
            "lmax": lmax,
        }
        (out / f"{name}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
        print(f"wrote data/anp/{name}.json")


if __name__ == "__main__":
    main()
