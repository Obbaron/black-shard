# Fantasy Calendar Engine

Small Python toolkit for defining, viewing, and converting between calendars.

## Layout

```
calendar/
├── README.md
├── pyproject.toml            installable; provides the `fcal` console script
├── .gitignore
├── fcal/                     engine
│   ├── __init__.py           public API: Calendar, Date, Converter, convert, World, render_*, …
│   ├── engine.py             data model, validation, JSON I/O, date/weekday/moon math, conversion
│   ├── render.py             a year → standalone HTML "wall calendar", or plain text
│   ├── cli.py                command-line front end (python -m fcal.cli …)
│   ├── world.py              the world registry: loads data/world.json, converts across calendars
│   └── paths.py              locations of the data/ and rendered/ directories
├── data/
│   ├── world.json            the index: which calendars exist, and the shared anchor
│   ├── canon/                in-world calendars - Black Shard canon
│   │   └── yavanna.json      the Calendar of Yavanna (defines the anchor)
│   └── reference/            real-world / test fixtures - NOT canon, NOT on the world axis
│       └── gregorian.json    proleptic Gregorian, for exercising leap rules & conversion
├── examples/
│   └── build_calendars.py    constructs the bundled calendars and writes them out
├── rendered/                 generated, browsable HTML (regenerable; committed on purpose)
│   └── yavanna_812.html
└── tests/
    ├── conftest.py
    ├── test_engine.py
    ├── test_convert.py
    └── test_world.py
```

### Where this subdirectory should sit

Drop `calendar/` wherever tooling lives in the repo (e.g. `tools/calendar/`). Two
placement notes worth a decision:

- **Canon data vs. the tool.** `data/canon/yavanna.json` is canon and currently
  ships *inside* the tool for a clean, self-contained drop-in. If you'd rather keep
  canonical calendars beside the prose they belong to (e.g. next to `eutaxia.md`),
  move `yavanna.json` there and point at it by path - nothing in the engine assumes
  its location except the short-name lookup in `fcal/paths.py`, which is a two-line
  change.
- **`reference/` is deliberately not canon.** The Gregorian calendar is only a
  real-world yardstick for the leap-rule and conversion machinery. It is segregated
  under `data/reference/` so nobody browsing the repo mistakes it for Black Shard
  material.

## Install / run

The engine has no runtime dependencies; the only third-party package is `pytest`,
declared as a dev dependency group. With [uv](https://docs.astral.sh/uv/):

```bash
uv sync                              # create .venv, install fcal (editable) + dev tools
uv run fcal info yavanna             # console script inside the synced env
uv run python -m fcal.cli examples   # (re)build data/ + rendered/
uv run pytest                        # 4 tests
```

`uv sync` installs the project itself in editable mode, so `import fcal`, the `fcal`
command, and the short-name → `data/` resolution all work against the source tree.
The environment is pinned by `.python-version` (3.12) and locked by `uv.lock`.

You can also run it with no install at all, straight from the `calendar/` directory:

```bash
python -m fcal.cli examples
python -m fcal.cli info yavanna
python -m fcal.cli render yavanna --year 812
python -m fcal.cli date yavanna --year 812 --block plerosis --day 1
python -m fcal.cli convert \
    --from yavanna --to gregorian \
    --anchor-from 812:m01:1 --anchor-to 2026:jul:19 \
    --date 812:plerosis:1
```

Calendars are referenced by **short name** (`yavanna`, `gregorian`) - resolved
against `data/canon` then `data/reference` - or by an explicit path to any `.json`.

From Python:

```python
from fcal import Calendar, Date, Converter, render_year_html, paths

yav = Calendar.load(paths.canon("yavanna"))
o   = yav.date_to_ordinal(Date(812, "m01", 1))
print(yav.weekday_name_of_ordinal(o), yav.moon_phases(o))
html = render_year_html(yav, 812)
```

## Tests

```bash
python -m pytest            # from the calendar/ directory
# or run either file directly:
python tests/test_engine.py
python tests/test_convert.py
```

The engine is validated against Python's own proleptic Gregorian calendar (year
lengths and weekdays match exactly across the 1900/2000 leap boundaries), all
ordinal↔date and cross-calendar conversions round-trip, and the tests independently
re-derive the source's coprimality claim (`gcd(361, 378) = 1` ⇒ a 378-year
conjunction return).

## Multiple calendars: the world timeline

The world will have more than one calendar (the pre-Severance Yavanna reckoning, the
Reckoners' computed feast, the Vestrn Bordas, regional systems, …). They all share one
atomic unit - the day - so they are placed on a single shared axis and convert to one
another with no per-pair bookkeeping.

**The anchor.** World-day 0 is *day 1 of the Eutaxian (post-Severance) calendar* -
`1 Monarchē, Year 1`. Because that is simply Yavanna's own `ordinal 0`, Yavanna sits on
the axis at `epoch_offset = 0`, and nothing about its encoding had to change to adopt
the timeline.

**Each calendar declares one integer.** `epoch_offset` is the world-day number of that
calendar's own day 1 - how far its day 1 sits from world-day 0 (negative for anything
predating the Severance). With every calendar on the axis, conversion composes:
`world_day = ordinal + epoch_offset`, and any calendar → any other goes through the
shared number. A calendar with `epoch_offset = null` is deliberately *off* the axis
(the Gregorian reference is), and can only be converted via an explicit anchor.

```bash
fcal calendars                       # list the world's calendars + their offsets
fcal date yavanna --year 812 --block m01 --day 1     # now also prints world-day
fcal convert --from yavanna --to <other> --date 812:m01:1   # no anchor needed on-axis
```

```python
from fcal import World, Date
w = World.load()
w.convert(Date(812, "m01", 1), "yavanna", "old_yavanna")   # once old_yavanna exists
w.to_world_day(Date(812, "m01", 1), "yavanna")             # -> 292771
```

**`data/world.json`** is the registry: it names the calendars, records the anchor, and
is validated on load (the anchor calendar's `epoch_offset` must match the declared
world-day; every non-reference calendar must be on the axis).

### Adding a new calendar

1. Build it (a `*_calendar()` constructor in `examples/build_calendars.py`, or hand-write
   the JSON) and set its **`epoch_offset`** to the number of days from Yavanna's day 1 to
   its own day 1. If you know a real correspondence instead - e.g. "the Severance fell on
   such-and-such a day of the old calendar" - compute the offset from that: load both,
   take `new.date_to_ordinal(new_day1) - 0` against the shared day, or just set the offset
   so a known shared date lands identically, then confirm with a round-trip.
2. Drop the JSON in `data/canon/` (or `data/historical/`, `data/regional/` - any
   subfolder; the registry references files by relative path).
3. Add an entry to `data/world.json` (`name`, `file`, `status`, `note`).
4. `fcal calendars` to check it resolves, and `fcal convert` to sanity-check a date you
   already know in both systems.

Until a calendar is on the axis you can still convert it against any other by supplying an
explicit shared anchor (`--anchor-from` / `--anchor-to`), exactly as before - that path is
unchanged and still how off-axis references like Gregorian are handled.

## What it supports

- **Year length**, `hard_year=True` (always identical) or `False` (leap years may differ).
- **Months** with individual day counts; a month's count can change in leap years via a
  leap rule (so months are hard/soft too).
- **Intercalary periods** - day-runs that sit *between* months and belong to none
  (`after_month` places them; `in_week` decides whether they carry weekdays).
- **Out-of-week days *inside* a month** via `out_of_week_tail` - for festivals like the
  Plerosis that must stay within the year's day-count (see below).
- **Weeks** of any length with named days; `week.hard=False` permits out-of-week days.
- **Moons** - any number, each with a `cycle` length and a `shift` (phase offset at the
  epoch); phases are drawn on every day.
- **Epoch** - `current_year` ("what year it is") and `start_weekday` (which weekday the
  epoch year opens on).
- **JSON** save / load, and **conversion** by anchoring one shared real day in each
  calendar (the engine counts days and reports the matching date in the other system).

Every day maps to an **ordinal** (an absolute integer; ordinal 0 = first day of the
epoch year). Weekday, moon phase, and conversion are pure ordinal arithmetic; dates are
a readable face on top. Out-of-week days are counted separately so they don't advance
the weekday cycle.

## Notes on the Yavanna encoding (please confirm)

Encoded from *The Hierophancy of Sophras*. A few choices are worth your eye, because the
source is emphatic about several numbers at once:

1. **The Plerosis is the last four days of month 19, marked out-of-week** - not a
   separate block added on top. This is the only reading that satisfies *all* the doc's
   numbers at once: 361 total, `19×19`, "the square is intact," and "fifty-one weeks and
   four days more" (357 in-week days = exactly 51×7, which is why Monda heads the year
   forever). A separate 4-day block would force either a 365-day year or a 15-day month
   19. If you'd rather the Plerosis read as its own festival between years, that's a
   small switch - say the word.
2. **Month names** - only Monarchē, Theurion, Desmia are given in the source; months
   4–19 are placeholders (`Month 4` …).
3. **Moon cycles (Monē 27, Mania 14)** are *inferred* from "seven out and seven back"
   (14) and "twenty-seven such runs to the year, one for each day of her sister's course"
   (27). Their LCM is 378 - matching the canon conjunction period - which is a good sign,
   but the numbers are provisional, as are the moon `shift` values.
4. **The epoch** - year 1 is anchored opening on Monda; the year-812 view follows from
   that. If canon fixes a different epoch weekday or founding date, set `start_weekday` /
   `epoch_year` in `examples/build_calendars.py` and rebuild.

Editing any of the above: change `examples/build_calendars.py`, then
`python -m fcal.cli examples` to rewrite `data/` and `rendered/`.
