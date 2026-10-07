import math

import pytest

from fluglaerm.engine import npd
from fluglaerm.engine.npd import (
    duration_correction,
    installation_correction,
    interp_npd,
    lateral_attenuation,
    load_npd,
    segment_sel,
)


def test_grid_reproduction_exact():
    """segment_sel-Vorgabe: Tabellenwert bei fester (P, d) auf <= 0.1 dB."""
    t = load_npd("A320-214")
    p, d = t.powers_lbf[2], t.distances_m[3]
    le, _ = interp_npd(t, p, d)
    assert abs(le - t.le[2][3]) <= 0.1


def test_offgrid_bilinear_logd():
    t = load_npd("A320-214")
    le, _ = interp_npd(t, t.powers_lbf[0], 500.0)
    # manuell: P exakt auf Gitterlinie 0, log-d zwischen dist[3]=304.8m, dist[4]=609.6m
    l0, l1 = math.log10(t.distances_m[3]), math.log10(t.distances_m[4])
    td = (math.log10(500.0) - l0) / (l1 - l0)
    expected = t.le[0][3] + td * (t.le[0][4] - t.le[0][3])
    assert abs(le - expected) < 1e-9


def test_lateral_attenuation_doc29():
    # (4-19): Gamma(0)=0, Lambda(90°)=0, Lambda(0°,>914m)=~10.857
    assert lateral_attenuation(5.0, 0.0) == pytest.approx(0.0)
    assert lateral_attenuation(90.0, 5000.0) == pytest.approx(0.0)
    assert lateral_attenuation(0.0, 5000.0) == pytest.approx(10.857, abs=0.01)
    # negativer Winkel (Terrain): 10.857
    assert lateral_attenuation(-2.0, 5000.0) == pytest.approx(10.857, abs=0.01)


def test_duration_and_installation():
    assert duration_correction(160.0) == pytest.approx(0.0)
    assert duration_correction(320.0) == pytest.approx(-3.0103, abs=1e-3)
    assert installation_correction(30.0, "prop") == 0.0
    # (4-15) wing-Koeffizienten: ΔI(0°) = 10·log10(0.0039^0.062) ≈ -1.49 dB
    assert installation_correction(0.0, "wing") == pytest.approx(-1.4935, abs=1e-3)
    # Prop: ΔI = 0 für alle Winkel (4-16)
    assert installation_correction(0.0, "prop") == 0.0


def test_missing_table_raises():
    with pytest.raises(FileNotFoundError):
        load_npd("NOPE-999")
