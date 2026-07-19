"""
build_calendars.py
==================
Constructs the calendars bundled with this subdirectory and writes them to disk:

* ``yavanna_calendar()``  -> data/canon/yavanna.json
     The Calendar of Yavanna, encoded faithfully from *The Hierophancy of Sophras*
     (eutaxia.md). Black Shard canon.
* ``gregorian_calendar()`` -> data/reference/gregorian.json
     Earth's proleptic Gregorian calendar, included purely as a neutral, real-world
     reference for exercising leap rules and conversion. **NOT Black Shard canon.**

Running the file also renders the Yavanna year to rendered/yavanna_812.html and
prints a short conversion demonstration.

These two functions are the one place where setting-specific calendars are spelled
out as code; the ``fcal`` package itself stays setting-agnostic.

Modelling notes for Yavanna (flagged so you can override them):
  * Year = 361 = 19x19, nineteen months of nineteen days. "The square is intact."
  * The four Plerosis days are the LAST FOUR DAYS of month 19, marked out-of-week
    (out_of_week_tail=4). This is the only encoding that satisfies every number the
    doc states at once: 361 total, 19x19, "fifty-one weeks and four days more"
    (357 in-week = 51x7), and Monda perpetually heading the year.
  * Month names: only the first three are given in the source (Monarche, Theurion,
    Desmia); the rest are placeholders.
  * Moon cycles (Mone 27, Mania 14) are INFERRED from "seven out and seven back"
    (=14) and "twenty-seven such runs to the year, one for each day of her sister's
    course" (=27). Their least common multiple is 378, which matches the canon
    conjunction period. Treat the cycle numbers as provisional.
"""
import sys
from pathlib import Path

# Allow `python examples/build_calendars.py` from anywhere: put the subdir root
# (which contains the `fcal` package) on the path.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fcal import (  # noqa: E402
    Calendar, Month, Week, Moon, LeapRule, Adjustment, Date, Converter,
    render_year_html, paths,
)

MONTH_NAMES = {1: "Monarchē", 2: "Theurion", 3: "Desmia"}


def yavanna_calendar() -> Calendar:
    months = []
    for i in range(1, 20):
        m = Month(name=MONTH_NAMES.get(i, f"Month {i}"), days=19, id=f"m{i:02d}")
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
        moons=[
            Moon("Monē", cycle=27, shift=0, color="#e8e0c8"),
            Moon("Mania", cycle=14, shift=0, color="#b9c7e0"),
        ],
        epoch_year=1, start_weekday=0, current_year=812,
        has_year_zero=True, hard_year=True,
        epoch_offset=0,   # day 1 of the Eutaxian calendar == world-day 0 (the anchor)
    )


def gregorian_calendar() -> Calendar:
    ms = [
        Month("January", 31, "jan"), Month("February", 28, "feb"),
        Month("March", 31, "mar"), Month("April", 30, "apr"),
        Month("May", 31, "may"), Month("June", 30, "jun"),
        Month("July", 31, "jul"), Month("August", 31, "aug"),
        Month("September", 30, "sep"), Month("October", 31, "oct"),
        Month("November", 30, "nov"), Month("December", 31, "dec"),
    ]
    return Calendar(
        name="Gregorian",
        months=ms,
        week=Week(7, ["Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"]),
        moons=[Moon("Luna", cycle=29.530588853, shift=0, color="#e6e6ea")],
        leap_rules=[LeapRule("Gregorian leap", interval=4, except_interval=100,
                             unless_interval=400,
                             adjustments=[Adjustment("feb", 1)])],
        epoch_year=1, start_weekday=0, current_year=2026,
        has_year_zero=False, hard_year=False,
    )


def build() -> None:
    paths.CANON_DIR.mkdir(parents=True, exist_ok=True)
    paths.REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    paths.RENDERED_DIR.mkdir(parents=True, exist_ok=True)

    yav = yavanna_calendar()
    greg = gregorian_calendar()
    yav.save(str(paths.canon("yavanna")))
    greg.save(str(paths.reference("gregorian")))

    html_path = paths.RENDERED_DIR / "yavanna_812.html"
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(render_year_html(yav, 812, title="Calendar of Yavanna"))

    print("Wrote:")
    print(f"  {paths.canon('yavanna')}")
    print(f"  {paths.reference('gregorian')}")
    print(f"  {html_path}")

    # Anchor one shared day (illustrative): 1 Monarchē 812 == 19 July 2026.
    conv = Converter(yav, greg, Date(812, "m01", 1), Date(2026, "jul", 19))
    print()
    print("=" * 60)
    print("CONVERSION DEMO  (anchor: 1 Monarchē 812 = 19 July 2026)")
    print("=" * 60)
    for label, d in [
        ("New Year 812", Date(812, "m01", 1)),
        ("First Plerosis day 812", Date(812, "plerosis", 1)),
        ("Last Plerosis day 812", Date(812, "plerosis", 4)),
        ("New Year 813", Date(813, "m01", 1)),
    ]:
        g = conv.a_to_b(d)
        wd = greg.weekday_name_of_ordinal(greg.date_to_ordinal(g))
        print(f"  {label:24s}  {str(d):20s} -> {g.day} {g.block} {g.year} ({wd})")

    print("\nA Gregorian date back into Yavanna:")
    g = Date(2027, "jan", 1)
    print(f"  1 January 2027 -> {conv.b_to_a(g)}")


if __name__ == "__main__":
    build()
