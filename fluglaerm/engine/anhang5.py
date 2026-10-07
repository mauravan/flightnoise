"""Grenzwerte + Beurteilungslogik wörtlich nach LSV Anhang 5 (LBK ZRH Juli 2015).

Einzige Quelle der Grenzwerte im Code. Art: "lrt" | "lrn" | "lrk".
Periode: "tag" für lrt/lrk; "nacht1" | "nacht2" | "letzte_nacht" für lrn.
"""

from __future__ import annotations

GRENZWERTE = {
    "lrt": {
        1: {"pw": 53, "igw": 55, "aw": 60},
        2: {"pw": 57, "igw": 60, "aw": 65},
        3: {"pw": 60, "igw": 65, "aw": 70},
        4: {"pw": 65, "igw": 70, "aw": 75},
    },
    "lrn": {
        1: {
            "nacht1": {"pw": 43, "igw": 45, "aw": 55},
            "nacht2": {"pw": 43, "igw": 45, "aw": 55},
            "letzte_nacht": {"pw": 43, "igw": 45, "aw": 55},
        },
        2: {
            "nacht1": {"pw": 50, "igw": 55, "aw": 65},
            "nacht2": {"pw": 47, "igw": 50, "aw": 60},
            "letzte_nacht": {"pw": 47, "igw": 50, "aw": 60},
        },
        3: {
            "nacht1": {"pw": 50, "igw": 55, "aw": 65},
            "nacht2": {"pw": 50, "igw": 55, "aw": 65},
            "letzte_nacht": {"pw": 50, "igw": 55, "aw": 65},
        },
        4: {
            "nacht1": {"pw": 55, "igw": 60, "aw": 70},
            "nacht2": {"pw": 55, "igw": 60, "aw": 70},
            "letzte_nacht": {"pw": 55, "igw": 60, "aw": 70},
        },
    },
    "lrk": {
        1: {"pw": 50, "igw": 55, "aw": 65},
        2: {"pw": 55, "igw": 60, "aw": 70},
        3: {"pw": 60, "igw": 65, "aw": 70},
        4: {"pw": 65, "igw": 70, "aw": 75},
    },
}


def grenzwert_status(pegel: float, es: int, periode: str, art: str) -> str:
    """-> "eingehalten" | "PW überschritten" | "IGW überschritten" | "AW überschritten"."""
    if art == "lrn":
        stufen = GRENZWERTE["lrn"][es][periode]
    else:
        stufen = GRENZWERTE[art][es]
    if pegel > stufen["aw"]:
        return "AW überschritten"
    if pegel > stufen["igw"]:
        return "IGW überschritten"
    if pegel > stufen["pw"]:
        return "PW überschritten"
    return "eingehalten"
