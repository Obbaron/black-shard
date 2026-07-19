"""Conversion tests. Two hermetically-built calendars:

* Gregorian (proleptic) as a real-world reference, checked against Python's own
  ``datetime`` for year lengths and weekdays across leap boundaries; and
* the Calendar of Yavanna,

anchored on one shared day and round-tripped in both directions. Also re-derives
the source's coprimality claim: gcd(361, 378) = 1, so the conjunction returns only
after 378 years.

Runnable directly (``python tests/test_convert.py``) or under pytest.
"""
import datetime as dt
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fcal.engine import *  # noqa: F401,F403,E402


def _gregorian():
    return Calendar(
        name="Gregorian",
        months=[
            Month("January", 31, "jan"), Month("February", 28, "feb"), Month("March", 31, "mar"),
            Month("April", 30, "apr"), Month("May", 31, "may"), Month("June", 30, "jun"),
            Month("July", 31, "jul"), Month("August", 31, "aug"), Month("September", 30, "sep"),
            Month("October", 31, "oct"), Month("November", 30, "nov"), Month("December", 31, "dec"),
        ],
        week=Week(7, ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]),
        moons=[Moon("Luna", 29.530588853, shift=0)],
        leap_rules=[LeapRule("Gregorian leap", interval=4, except_interval=100,
                             unless_interval=400, adjustments=[Adjustment("feb", 1)])],
        epoch_year=1, start_weekday=0,       # 0001-01-01 (proleptic) is a Monday
        current_year=2026, has_year_zero=False, hard_year=False,
    )


def _yavanna():
    named = {1: "Monarchē", 2: "Theurion", 3: "Desmia"}
    months = []
    for i in range(1, 20):
        m = Month(name=named.get(i, f"Month {i}"), days=19, id=f"m{i:02d}")
        if i == 19:
            m.out_of_week_tail = 4
            m.tail_name = "Plerosis"
            m.tail_id = "plerosis"
        months.append(m)
    return Calendar(
        name="Calendar of Yavanna",
        months=months,
        week=Week(7, ["Monda", "Tuesda", "Wirsda", "Horda", "Frida", "Sorda", "Sunda"],
                  hard=False),
        moons=[Moon("Monē", 27), Moon("Mania", 14)],
        epoch_year=1, start_weekday=0, current_year=812,
        has_year_zero=True, hard_year=True,
    )


MKEYS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


def test_gregorian_matches_datetime():
    greg = _gregorian()
    assert greg.validate() == []

    for y in [1, 4, 100, 400, 1900, 2000, 2024, 2025, 2026, 2100]:
        py_len = (dt.date(y + 1, 1, 1) - dt.date(y, 1, 1)).days
        assert greg.year_length(y) == py_len, (y, greg.year_length(y), py_len)

    for pd in [dt.date(1, 1, 1), dt.date(1600, 2, 29), dt.date(1900, 3, 1),
               dt.date(2000, 2, 29), dt.date(2026, 7, 19), dt.date(2024, 2, 29)]:
        o = greg.date_to_ordinal(Date(pd.year, MKEYS[pd.month - 1], pd.day))
        assert greg.weekday_name_of_ordinal(o) == pd.strftime("%A"), pd

    a = greg.date_to_ordinal(Date(2000, "jan", 1))
    b = greg.date_to_ordinal(Date(2026, "jul", 19))
    assert b - a == (dt.date(2026, 7, 19) - dt.date(2000, 1, 1)).days


def test_yavanna_gregorian_conversion():
    greg = _gregorian()
    yav = _yavanna()
    # Anchor: declare Yavanna 1 Monarchē 812 == 19 July 2026 (illustrative choice).
    conv = Converter(yav, greg, anchor_a=Date(812, "m01", 1), anchor_b=Date(2026, "jul", 19))

    for (blk, day, yr) in [("m01", 1, 812), ("m10", 7, 812), ("plerosis", 4, 812),
                           ("m19", 15, 850), ("m05", 19, 700), ("m01", 1, 813)]:
        d = Date(yr, blk, day)
        back = conv.b_to_a(conv.a_to_b(d))
        assert (back.year, back.block, back.day) == (d.year, d.block, d.day), (d, back)


def test_coprimality_return_period():
    assert math.gcd(361, 378) == 1
    assert 378 // math.gcd(361, 378) == 378


if __name__ == "__main__":
    test_gregorian_matches_datetime()
    test_yavanna_gregorian_conversion()
    test_coprimality_return_period()
    print("CONVERSION TESTS PASSED")
