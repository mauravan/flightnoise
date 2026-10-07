import math

from fluglaerm.engine.anhang5 import GRENZWERTE, grenzwert_status


def test_gesamt_formel_beispiel():
    # LoD: Lrk=55, Lrg=63 -> 10*log10(10^5.5 + 10^6.3)
    from fluglaerm.engine.acoustic import gesamt_lrt

    assert gesamt_lrt(lrk=55.0, lrg=63.0) == 10 * math.log10(10**5.5 + 10**6.3)


def test_grenzwert_status_es2_tag():
    assert grenzwert_status(63, es=2, periode="tag", art="lrt") == "IGW überschritten"
    assert grenzwert_status(66, es=2, periode="tag", art="lrt") == "AW überschritten"
    assert grenzwert_status(57, es=2, periode="tag", art="lrt") == "eingehalten"
    assert grenzwert_status(58, es=2, periode="tag", art="lrt") == "PW überschritten"


def test_grenzwerte_werte_wörtlich():
    assert GRENZWERTE["lrt"][2] == {"pw": 57, "igw": 60, "aw": 65}
    assert GRENZWERTE["lrn"][2]["nacht1"] == {"pw": 50, "igw": 55, "aw": 65}
    assert GRENZWERTE["lrk"][1] == {"pw": 50, "igw": 55, "aw": 65}
