"""Auflagenlogik nach Kreisschreiben Baudirektion ZH 1.6.2026; nur Wohnen.

Regeln (nutzung == "wohnen", sonst leere Liste):
- lrt > IGW(es) oder irgendein lrn > IGW(es, nacht) ->
  kontrollierte Wohnraumlüftung + Kühlsystem (Art. 22 Abs. 2 lit. a Ziff. 1 USG);
  keine Ausnahmebewilligung nötig.
- lrt > 65 oder lrn["nacht1"] > 55 -> Komfortlüftung Pflicht.
- lrt > 60 oder lrn["nacht1"] > 55 -> erhöhte Anforderungen Gebäudehülle SIA 181.
- lrt > AW(es) -> Zusatzvermerk über AW (Bauzone, keine überwiegenden Interessen nötig).
"""

from __future__ import annotations

from fluglaerm.engine.anhang5 import GRENZWERTE
from fluglaerm.engine.engine import EngineResult

LUEFTUNG = "kontrollierte Wohnraumlüftung + Kühlsystem (Art. 22 Abs. 2 lit. a Ziff. 1 USG)"
KOMFORT = "Komfortlüftung Pflicht"
HUELLEN = "erhöhte Anforderungen Gebäudehülle nach SIA 181 (ZH-Verschärfung)"
UEBER_AW = (
    "über AW: in bestehender Bauzone mit denselben Auflagen erteilbar "
    "(kein überwiegendes Interesse nötig)"
)


def auflagen(res: EngineResult, es: int, nutzung: str) -> list[str]:
    if nutzung != "wohnen":
        return []
    out: list[str] = []
    igw_tag = GRENZWERTE["lrt"][es]["igw"]
    igw_naechte = {k: GRENZWERTE["lrn"][es][k]["igw"] for k in res.lrn}
    if res.lrt > igw_tag or any(res.lrn[k] > igw_naechte[k] for k in res.lrn):
        out.append(LUEFTUNG)
    if res.lrt > 65 or res.lrn.get("nacht1", float("-inf")) > 55:
        out.append(KOMFORT)
    if res.lrt > 60 or res.lrn.get("nacht1", float("-inf")) > 55:
        out.append(HUELLEN)
    if res.lrt > GRENZWERTE["lrt"][es]["aw"]:
        out.append(UEBER_AW)
    return out
