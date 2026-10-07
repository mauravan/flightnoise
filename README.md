# Fluglärm-Rechner

Zwei klar getrennte Module:

1. **Rechtskonforme Engine** (`fluglaerm/engine/`): bildet die Methodik von LSV Anhang 5 /
   ECAC Doc 29 nach, gespeist mit dem **genehmigten** Flugbetrieb. Ergebnis: Beurteilungspegel
   Lr Tag/Nacht (Lrt/Lrn), Grenzwert-Vergleich, AGL-Lage, Auflagen, Nachweis-Dokument.
2. **Ist-Lärm-Modul** (`fluglaerm/ist_laerm/`, informativ): liest echte ADS-B-Spuren von
   OpenSky Network ein und schätzt SEL/Leq des tatsächlichen Verkehrs. **Keine Rechtswirkung.**

Rechtliche Grenze: LSV Art. 38 Abs. 2 verlangt die *Berechnung* des Lärms des **genehmigten**
Flugbetriebs, nicht des tatsächlichen Verkehrs. Das behördenverbindliche Endergebnis bleibt
FLULA2 (Empa) über ein Akustikbüro.
