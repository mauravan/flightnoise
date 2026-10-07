"""Akustik-Kern nach ECAC Doc 29, 5. Aufl., Vol. 2 (Technical Guide).

Einziger Schallausbreitungs-Kern; gemeinsam von Engine und Ist-Modul genutzt.

Segment-Gleichung (vereinfacht, ohne finite-segment/ground-roll-Sonderfälle):
    SEL_seg = L_E(P, d) + ΔV + ΔI(φ) − Λ(β, ℓ)

  - L_E(P, d): NPD-Baseline, bilinear in (P, log d)      [Doc 29 §4.4–4.5]
  - ΔV = 10·log10(Vref / Vseg), Vref = 160 kt           [Doc 29 (4-14)]
  - ΔI(φ) Installation/Directivity                       [Doc 29 (4-15)]
  - Λ(β, ℓ) = Γ(ℓ)·Λ(β) Lateral-Dämpfung (AIR-5662)      [Doc 29 (4-17)–(4-19)]

Quellen: ECAC Doc 29 5th ed. Vol. 2, §§ 4.3–4.5.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

VREF_KN = 160.0  # NPD-Referenzgeschwindigkeit (Doc 29: 270.05 ft/s)

# Installations-Koeffizienten (4-15): a, b, c je Triebwerksanordnung
MOUNT_COEFFS = {
    "wing": (0.0039, 0.062, 0.8786),
    "fuselage": (0.1225, 0.329, 1.0),
    "prop": None,  # ΔI = 0 (4-16)
}

DEFAULT_ANP_DIR = Path("data/anp")


@dataclass
class NpdTable:
    aircraft: str
    source: str  # z.B. "EASA-ANP v2.1" oder "SYNTHETIC_PLACEHOLDER"
    engine_mount: str  # "wing" | "fuselage" | "prop"
    max_thrust_lbf: float
    ref_speed_kn: float
    powers_lbf: list[float]  # aufsteigend
    distances_m: list[float]  # aufsteigend
    le: list[list[float]]  # le[i][j] = SEL bei powers[i], distances[j]
    lmax: list[list[float]]


@lru_cache(maxsize=32)
def load_npd(aircraft_anp: str, data_dir: str | Path = DEFAULT_ANP_DIR) -> NpdTable:
    """Lädt <data_dir>/<aircraft_anp>.json (via fetch_anp.py bereitgestellt; gecacht)."""
    path = Path(data_dir) / f"{aircraft_anp}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Keine NPD-Tabelle für '{aircraft_anp}' in {Path(data_dir).resolve()}/. "
            "Echte EASA-ANP-Daten via data/fetch_anp.py anfordern."
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    return NpdTable(
        aircraft=raw["aircraft"],
        source=raw.get("source", "unknown"),
        engine_mount=raw["engine_mount"],
        max_thrust_lbf=float(raw["max_thrust_lbf"]),
        ref_speed_kn=float(raw.get("ref_speed_kn", VREF_KN)),
        powers_lbf=[float(p) for p in raw["powers_lbf"]],
        distances_m=[float(d) for d in raw["distances_m"]],
        le=[[float(v) for v in row] for row in raw["le"]],
        lmax=[[float(v) for v in row] for row in raw["lmax"]],
    )


def _interp1(x: float, xs: list[float]) -> tuple[int, int, float]:
    """Gibt (i0, i1, t) mit x = xs[i0] + t*(xs[i1]-xs[i0]), geclampte Ränder."""
    if x <= xs[0]:
        return 0, 0, 0.0
    if x >= xs[-1]:
        return len(xs) - 1, len(xs) - 1, 0.0
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return i, i + 1, t
    raise AssertionError("unreachable")  # pragma: no cover


def interp_npd(table: NpdTable, power_lbf: float, dist_m: float) -> tuple[float, float]:
    """Bilinear in (P, log10 d) -> (LE, Lmax). Ränder geclampt."""
    i0, i1, tp = _interp1(power_lbf, table.powers_lbf)
    logd = [math.log10(d) for d in table.distances_m]
    j0, j1, td = _interp1(math.log10(max(dist_m, 1.0)), logd)
    out = []
    for grid in (table.le, table.lmax):
        v00, v01 = grid[i0][j0], grid[i0][j1]
        v10, v11 = grid[i1][j0], grid[i1][j1]
        v0 = v00 + td * (v01 - v00)
        v1 = v10 + td * (v11 - v10)
        out.append(v0 + tp * (v1 - v0))
    return out[0], out[1]


def installation_correction(phi_deg: float, engine_mount: str) -> float:
    """ΔI(φ) nach (4-15); für φ < 0 gilt ΔI(0). Props: 0."""
    coeffs = MOUNT_COEFFS[engine_mount]
    if coeffs is None:
        return 0.0
    a, b, c = coeffs
    phi = math.radians(max(phi_deg, 0.0))
    term1 = (a * math.cos(phi) ** 2 + math.sin(phi) ** 2) ** b
    term2 = c * math.sin(2 * phi) ** 2 + math.cos(2 * phi) ** 2
    return 10.0 * math.log10(term1 * term2)


def lateral_attenuation(beta_deg: float, ell_m: float) -> float:
    """Λ(β, ℓ) = Γ(ℓ)·Λ(β) nach (4-18)–(4-19). β in Grad, ℓ in m."""
    ell = max(ell_m, 0.0)
    gamma = 1.089 * (1.0 - math.exp(-0.00274 * ell)) if ell <= 914.0 else 1.0
    if beta_deg < 0.0:
        lam_beta = 10.857
    elif beta_deg <= 50.0:
        lam_beta = 1.137 - 0.0229 * beta_deg + 9.72 * math.exp(-0.142 * beta_deg)
    else:
        lam_beta = 0.0
    return gamma * lam_beta


def duration_correction(speed_kn: float, vref_kn: float = VREF_KN) -> float:
    """ΔV = 10·log10(Vref / Vseg) nach (4-14)."""
    return 10.0 * math.log10(vref_kn / speed_kn)


def finite_segment_correction(
    q_m: float, seg_len_m: float, le_inf: float, lmax_at_dp: float
) -> float:
    """ΔF = 10·log10(F) nach (4-20): Energieanteil des finiten Segments.

    q: Distanz S1->Sp (negativ = Empfänger hinter Segment, >L = davor).
    d_lambda: skalierte Distanz = d0 · 10^((LE∞(P,dp) − Lmax(P,dp))/10),
      d0 = (2/π)·Vref·t0, Vref = 160 kt, t0 = 1 s.
    Untergrenze −150 dB (Doc 29-Empfehlung).
    """
    from scipy.constants import foot, knot

    vref_ms = 160.0 * knot / (foot / foot)  # 160 kt in m/s
    d0 = (2.0 / math.pi) * vref_ms * 1.0
    d_lambda = d0 * 10.0 ** ((le_inf - lmax_at_dp) / 10.0)
    d_lambda = max(d_lambda, 1e-6)
    lam = max(seg_len_m, 1e-6)
    a1 = -q_m / d_lambda
    a2 = -(q_m - lam) / d_lambda

    def _term(a: float) -> float:
        return a / (1.0 + a * a) + math.atan(a)

    f = (_term(a2) - _term(a1)) / math.pi
    f = max(f, 1e-15)
    return max(10.0 * math.log10(f), -150.0)


def segment_sel(
    aircraft_anp: str,
    phase: str,
    thrust_frac: float,
    slant_m: float,
    seg_ground_speed_kn: float,
    elev_deg: float,
    lat_disp_m: float,
    data_dir: str | Path = DEFAULT_ANP_DIR,
    delta_f: float = 0.0,
) -> float:
    """SEL eines Fluggpfad-Segments am Empfänger.

    phase: "departure" | "arrival" (API; derzeit nur Dokumentation der Flugphase).
    thrust_frac: 0..1 Anteil des Maximalschubs (None-Behandlung ausserhalb).
    elev_deg: Elevationswinkel β, lat_disp_m: Lateralversatz ℓ.
    Depression φ = β (kein Bankwinkel modelliert, ε = 0).
    delta_f: finite-segment-Korrektur ΔF ≤ 0 nach (4-20); Default 0 (infinite path).
    """
    table = load_npd(aircraft_anp, data_dir)
    power = max(thrust_frac, 0.0) * table.max_thrust_lbf
    base_le, _ = interp_npd(table, power, slant_m)
    dv = duration_correction(seg_ground_speed_kn, table.ref_speed_kn)
    di = installation_correction(elev_deg, table.engine_mount)
    lam = lateral_attenuation(elev_deg, lat_disp_m)
    return base_le + dv + di - lam + delta_f
