"""Lädt EASA-ANP-Tabellen (NPD) nach data/anp/ (git-ignoriert).

Die ANP-Datenbank ist nicht anonym programmatisch abrufbar: EASA verlangt eine
Nutzungsanfrage über ein Webformular. Dieses Skript versucht bekannte Spiegel;
schlägt das fehl, gibt es die manuelle Anleitung aus.

Manuell: https://www.easa.europa.eu/en/anp-data-request  (Formular einreichen)
         bzw. https://www.easa.europa.eu/en/domains/environment/policy-support-and-research/aircraft-noise-and-performance-anp-data
Danach die NPD-Tabellen als JSON <ANP-ID>.json nach data/anp/ ablegen, Schema:

  {"aircraft": "A320-214", "source": "EASA-ANP v2.1", "engine_mount": "wing",
   "max_thrust_lbf": 27000, "ref_speed_kn": 160,
   "powers_lbf": [...], "distances_m": [...],
   "le": [[...]], "lmax": [[...]]}

Platzhalter: data/anp/*.json mit "source": "SYNTHETIC_PLACEHOLDER" sind
runde Beispielwerte (Methodendemonstration, keine echten ANP-Daten).
"""

from __future__ import annotations

import sys

EASA_ANP_URL = (
    "https://www.easa.europa.eu/en/domains/environment/"
    "policy-support-and-research/aircraft-noise-and-performance-anp-data"
)
EASA_REQUEST_URL = "https://www.easa.europa.eu/en/anp-data-request"


def main() -> int:
    print("EASA-ANP-Datenbank ist nicht anonym programmatisch abrufbar.")
    print()
    print("1. Nutzungsanfrage stellen:", EASA_REQUEST_URL)
    print("2. Info-Seite:            ", EASA_ANP_URL)
    print("3. NPD-Tabellen als JSON (Schema s. Modul-Docstring) nach data/anp/ ablegen.")
    print()
    print("Bis dahin nutzt die Engine SYNTHETIC_PLACEHOLDER-Tabellen in data/anp/;")
    print("Ergebnisse sind Methodendemonstration, nicht rechtsgültig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
