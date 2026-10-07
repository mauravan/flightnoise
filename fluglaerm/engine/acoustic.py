"""Anhang-5-Korrekturen und Pegelaggregation (wörtlich LBK ZRH).

- Lrk (Kleinluftfahrzeuge, nur Tag 06–20): Lrk = Leq_k + 10·log10(N/15000)
- Lrt = 10·log10(10^(Lrk/10) + 10^(Lrg/10))
- Lrn(1./2. Nachtstunde) = Leq der Grossflugzeuge in der jeweiligen Stunde.
  Letzte Nachtstunde (05–06) wird für ZRH nicht berechnet (Flughafen geschlossen).
"""

from __future__ import annotations

import math

KLEIN_REF_N = 15000
LST_NIGHT_CLOSED = True  # ZRH geschlossen 05–06


def klein_lrk(leq_klein: float, n_klein: int) -> float:
    """Lrk = Leq_k + 10·log10(N/15000)."""
    return leq_klein + 10.0 * math.log10(n_klein / KLEIN_REF_N)


def gesamt_lrt(lrk: float, lrg: float) -> float:
    """Lrt = 10·log10(10^0.1·lrk + 10^0.1·lrg)."""
    return 10.0 * math.log10(10 ** (lrk / 10.0) + 10 ** (lrg / 10.0))


def accumulate_leq(sels: list[float], period_s: float) -> float:
    """Leq = 10·log10((1/T)·Σ 10^(SEL_i/10)). Leere Liste -> -inf."""
    if not sels:
        return float("-inf")
    energy = sum(10.0 ** (s / 10.0) for s in sels)
    return 10.0 * math.log10(energy / period_s)
