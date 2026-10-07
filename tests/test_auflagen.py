from fluglaerm.engine.auflagen import HUELLEN, KOMFORT, LUEFTUNG, auflagen
from fluglaerm.engine.engine import EngineResult


def _res(lrt: float, nacht1: float) -> EngineResult:
    return EngineResult(
        lrt=lrt,
        lrn={"nacht1": nacht1, "nacht2": 40.0},
        lrk=50.0,
        lrg=lrt,
        status={},
        agl="innerhalb",
    )


def test_auflagen_mittel():
    """Plan-Vorgabe: lrt=63, nacht1=52, es=2, wohnen -> Lüftung + Hülle, kein Komfort."""
    got = auflagen(_res(63.0, 52.0), es=2, nutzung="wohnen")
    assert LUEFTUNG in got
    assert HUELLEN in got
    assert KOMFORT not in got
    assert got == [LUEFTUNG, HUELLEN]


def test_auflagen_komfort_schwelle():
    """Plan-Vorgabe: lrt=66 -> zusätzlich Komfortlüftung (plus AW-Vermerk, AW=65)."""
    from fluglaerm.engine.auflagen import UEBER_AW
    got = auflagen(_res(66.0, 52.0), es=2, nutzung="wohnen")
    assert got == [LUEFTUNG, KOMFORT, HUELLEN, UEBER_AW]


def test_auflagen_betrieb_leer():
    assert auflagen(_res(70.0, 60.0), es=2, nutzung="betrieb") == []


def test_auflagen_unter_igw_leer():
    assert auflagen(_res(55.0, 45.0), es=2, nutzung="wohnen") == []
