"""Engine tests: build the Calendar of Yavanna from scratch and check that every
number the source insists on holds - 361 = 19x19, 357 in-week days = 51 weeks,
Monda perpetually heading the year, the out-of-week Plerosis tail, ordinal<->date
round-tripping, monotonic weekdays, and a JSON round-trip.

Runnable directly (``python tests/test_engine.py``) or under pytest.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fcal.engine import *  # noqa: F401,F403,E402


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
        week=Week(
            7,
            ["Monda", "Tuesda", "Wirsda", "Horda", "Frida", "Sorda", "Sunda"],
            hard=False,
        ),
        moons=[Moon("Monē", 27), Moon("Mania", 14)],
        epoch_year=1,
        start_weekday=0,
        current_year=812,
        has_year_zero=True,
        hard_year=True,
    )


def test_yavanna_engine():
    yav = _yavanna()

    assert yav.validate() == []
    assert yav.year_length(1) == 361
    assert yav.in_week_days_in_year(1) == 357 == 51 * 7

    for y in (1, 2, 100, 811, 812, 813):
        assert yav.new_year_weekday(y) == 0, (y, yav.new_year_weekday(y))

    # Plerosis addressed as its own block; out-of-week.
    p1 = yav.date_to_ordinal(Date(812, "plerosis", 1))
    assert yav.weekday_of_ordinal(p1) is None
    assert yav.weekday_of_ordinal(p1 + 4) == 0  # week resumes on Monda

    # month 19 day 15 is the last in-week day; day "16" is Plerosis 1.
    d15 = yav.date_to_ordinal(Date(812, "m19", 15))
    assert yav.weekday_of_ordinal(d15) == 6  # Sunda
    assert d15 + 1 == p1

    bad = sum(
        1
        for o in range(-4000, 8000)
        if yav.date_to_ordinal(yav.ordinal_to_date(o)) != o
    )
    assert bad == 0

    prev = None
    for o in range(0, 800):
        wd = yav.weekday_of_ordinal(o)
        if wd is not None:
            if prev is not None:
                assert (prev + 1) % 7 == wd, (o, prev, wd)
            prev = wd

    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "yavanna.json"
        yav.save(str(path))
        assert Calendar.load(str(path)).to_json() == yav.to_json()


if __name__ == "__main__":
    test_yavanna_engine()
    print("YAVANNA ENGINE TESTS PASSED")
