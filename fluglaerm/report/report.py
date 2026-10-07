"""Nachweis-Dokument: Markdown + JSON.

Pflichtangaben: Parzelle (LV95/EGRID), ES, Nutzung, Lrt/Lrn, überschrittene
Grenzwertstufe je Periode, AGL-Lage, Auflagen, Quellen + Datenstand.
Nur nominale Seed-Routen -> Satz «Methode demonstriert, nicht rechtsgültig —
genehmigter Routendatensatz fehlt».
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict

from fluglaerm.common.types import Receiver
from fluglaerm.engine.auflagen import auflagen
from fluglaerm.engine.engine import EngineResult
from fluglaerm.ist_laerm.ist import IstResult

SOURCES = [
    "vBR-2012-Aggregate (LBK ZRH Juli 2015)",
    "ECAC Doc 29, 5. Aufl., Vol. 2 (Technical Guide)",
    "Kreisschreiben Baudirektion ZH 1.6.2026",
    "LSV Anhang 5",
]

NOMINAL_HINWEIS = (
    "Methode demonstriert, nicht rechtsgültig — genehmigter Routendatensatz fehlt"
)


def _fmt(x: float) -> str:
    return "—" if math.isinf(x) or math.isnan(x) else f"{x:.1f} dB"


def render_markdown(
    engine: EngineResult,
    ist: IstResult | None,
    receiver: Receiver,
    sources: list[str] | None = None,
    nominal: bool = True,
    egrid: str | None = None,
) -> str:
    srcs = sources or SOURCES
    aufl = auflagen(engine, receiver.es, receiver.nutzung)
    lines = [
        "# Fluglärm-Nachweis (Methodendemonstration)",
        "",
        "## Parzelle",
        f"- LV95: E {receiver.east:.0f} / N {receiver.north:.0f}",
        f"- Empfängerhöhe (über Flughafen-Grund): {receiver.height_m:.1f} m",
    ]
    if egrid:
        lines.append(f"- EGRID: {egrid}")
    lines += [
        f"- Empfindlichkeitsstufe: ES {receiver.es}",
        f"- Nutzung: {receiver.nutzung}",
        "",
        "## Beurteilungspegel (genehmigter Flugbetrieb)",
        f"- Lrt (Tag): {_fmt(engine.lrt)} — Status: {engine.status.get('tag')}",
    ]
    for pid, val in engine.lrn.items():
        lines.append(f"- Lrn ({pid}): {_fmt(val)} — Status: {engine.status.get(pid)}")
    lines += [
        f"- Lrk: {_fmt(engine.lrk)}, Lrg: {_fmt(engine.lrg)}",
        f"- AGL-Lage: {engine.agl}",
        "",
        "## Auflagen",
    ]
    lines += [f"- {a}" for a in aufl] or ["- keine"]
    if ist is not None:
        lines += [
            "",
            "## Ist-Lärm (Abgleich, informativ)",
            f"- Leq_ist: {_fmt(ist.leq)} aus {ist.n_flights} Flügen",
            f"- {ist.label}",
        ]
    lines += ["", "## Quellen / Datenstand"]
    lines += [f"- {s}" for s in srcs]
    if nominal:
        lines += ["", f"> {NOMINAL_HINWEIS}."]
    lines.append("")
    return "\n".join(lines)


def render_json(
    engine: EngineResult,
    ist: IstResult | None,
    receiver: Receiver,
    nominal: bool = True,
) -> str:
    doc = {
        "receiver": asdict(receiver),
        "engine": {
            "lrt": engine.lrt,
            "lrn": engine.lrn,
            "lrk": engine.lrk,
            "lrg": engine.lrg,
            "status": engine.status,
            "agl": engine.agl,
            "auflagen": auflagen(engine, receiver.es, receiver.nutzung),
        },
        "ist": ({"leq": ist.leq, "n_flights": ist.n_flights, "label": ist.label}
                if ist else None),
        "sources": SOURCES,
        "nominal": nominal,
    }
    return json.dumps(doc, indent=1, ensure_ascii=False)
