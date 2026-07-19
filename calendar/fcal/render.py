"""
render.py

Render a :class:`fantasy_calendar.Calendar` year to a standalone HTML page (a
"wall calendar": one grid per month, moon phases on every day, out-of-week
festivals shown as banners) or to plain text.
"""

from __future__ import annotations

from html import escape
from typing import List

from .engine import Calendar, Segment


def _moon_svg(index8: int, color: str, r: float = 7.0) -> str:
    size = r * 2
    dark = "#1e293b"
    light = color
    c = f'<circle cx="{r}" cy="{r}" r="{r}"'

    if index8 == 0:  # new
        body = f'{c} fill="{dark}"/>'

    elif index8 == 4:  # full
        body = f'{c} fill="{light}"/>'

    elif index8 == 2:  # first quarter (right lit)
        body = (
            f'{c} fill="{dark}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 1 {r},{size} Z" fill="{light}"/>'
        )

    elif index8 == 6:  # last quarter (left lit)
        body = (
            f'{c} fill="{dark}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 0 {r},{size} Z" fill="{light}"/>'
        )

    elif index8 == 1:  # waxing crescent (right)
        body = (
            f'{c} fill="{dark}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 1 {r},{size} '
            f'A{r/2},{r} 0 0 0 {r},0 Z" fill="{light}"/>'
        )

    elif index8 == 3:  # waxing gibbous
        body = (
            f'{c} fill="{light}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 0 {r},{size} '
            f'A{r/2},{r} 0 0 1 {r},0 Z" fill="{dark}"/>'
        )

    elif index8 == 5:  # waning gibbous
        body = (
            f'{c} fill="{light}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 1 {r},{size} '
            f'A{r/2},{r} 0 0 0 {r},0 Z" fill="{dark}"/>'
        )

    else:  # 7 waning crescent (left)
        body = (
            f'{c} fill="{dark}"/>'
            f'<path d="M{r},0 A{r},{r} 0 0 0 {r},{size} '
            f'A{r/2},{r} 0 0 1 {r},0 Z" fill="{light}"/>'
        )

    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        f'class="moon">{body}<circle cx="{r}" cy="{r}" r="{r}" '
        f'fill="none" stroke="#0f172a" stroke-opacity=".35"/></svg>'
    )


def _day_moons(cal: Calendar, ordinal: int) -> str:
    if not cal.moons:
        return ""

    cells = []
    for m in cal.moons:
        idx = cal.moon_phase_index(m, ordinal, 8)
        title = f"{m.name}: {cal.moon_phase_name(m, ordinal)}"
        cells.append(f'<span title="{escape(title)}">{_moon_svg(idx, m.color)}</span>')

    return f'<div class="moons">{"".join(cells)}</div>'


def render_year_html(cal: Calendar, year: int, title: str = None) -> str:
    L = cal.week.length

    weekday_names = [cal.week.name_for(i) for i in range(L)]
    ordinal = cal._days_before_year(year)
    blocks_html: List[str] = []

    for seg in cal.segments(year):
        if seg.in_week:
            blocks_html.append(_month_block(cal, seg, ordinal, L, weekday_names))

        else:
            blocks_html.append(_festival_block(cal, seg, ordinal))

        ordinal += seg.days

    new_year_wd = cal.new_year_weekday(year)
    subtitle = f"Year {year}"

    if new_year_wd is not None:
        subtitle += f" · opens on {cal.week.name_for(new_year_wd)}"

    subtitle += f" · {cal.year_length(year)} days"

    moon_legend = " ".join(
        f'<span class="lg">{_moon_svg(4, m.color)} {escape(m.name)}</span>'
        for m in cal.moons
    )

    return _PAGE.format(
        title=escape(title or cal.name),
        subtitle=escape(subtitle),
        legend=moon_legend,
        weekcols=L,
        blocks="\n".join(blocks_html),
    )


def _month_block(cal, seg: Segment, start_ord: int, L: int, weekday_names) -> str:
    header = "".join(f'<div class="wd">{escape(n)}</div>' for n in weekday_names)

    first_wd = cal.weekday_of_ordinal(start_ord) or 0
    cells = ['<div class="cell blank"></div>'] * first_wd

    for d in range(seg.days):
        o = start_ord + d
        cells.append(
            f'<div class="cell"><div class="num">{d + 1}</div>'
            f"{_day_moons(cal, o)}</div>"
        )

    while len(cells) % L:
        cells.append('<div class="cell blank"></div>')

    return (
        f'<section class="month"><h2>{escape(seg.name)}</h2>'
        f'<div class="grid" style="--cols:{L}">{header}{"".join(cells)}</div>'
        f"</section>"
    )


def _festival_block(cal, seg: Segment, start_ord: int) -> str:
    cells = []

    for d in range(seg.days):
        ord = start_ord + d
        cells.append(
            f'<div class="cell fest"><div class="num">{d + 1}</div>'
            f"{_day_moons(cal, ord)}</div>"
        )

    return (
        f'<section class="festival"><h2>{escape(seg.name)} '
        f'<span class="tag">outside the week</span></h2>'
        f'<div class="fgrid">{"".join(cells)}</div></section>'
    )


_PAGE = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - {subtitle}</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; padding:2rem 1.25rem 4rem; background:#f4f1ea; color:#1f2430;
    font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }}
  header {{ max-width:1100px; margin:0 auto 1.75rem; }}
  h1 {{ font-size:1.9rem; margin:0 0 .2rem; letter-spacing:.01em; }}
  .sub {{ color:#5b6472; font-size:1rem; }}
  .legend {{ margin-top:.6rem; display:flex; gap:1.1rem; flex-wrap:wrap; color:#5b6472;
    font-size:.85rem; align-items:center; }}
  .legend .lg {{ display:inline-flex; align-items:center; gap:.35rem; }}
  main {{ max-width:1100px; margin:0 auto; display:grid;
    grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:1.4rem; }}
  section {{ background:#fbfaf6; border:1px solid #e2ddd0; border-radius:12px;
    padding:1rem 1rem 1.15rem; box-shadow:0 1px 2px rgba(0,0,0,.04); }}
  h2 {{ font-size:1.05rem; margin:.1rem 0 .8rem; display:flex; align-items:baseline;
    justify-content:space-between; }}
  .tag {{ font-size:.62rem; text-transform:uppercase; letter-spacing:.12em;
    color:#8a6a3b; background:#f1e6d2; padding:.15rem .45rem; border-radius:999px; }}
  .grid {{ display:grid; grid-template-columns:repeat(var(--cols),1fr); gap:3px; }}
  .wd {{ font-size:.62rem; text-transform:uppercase; letter-spacing:.05em;
    color:#8b93a1; text-align:center; padding-bottom:.25rem; }}
  .cell {{ aspect-ratio:1/1; border:1px solid #ece7db; border-radius:7px;
    padding:.25rem; display:flex; flex-direction:column; justify-content:space-between;
    background:#fff; }}
  .cell.blank {{ background:transparent; border:none; }}
  .num {{ font-size:.9rem; font-variant-numeric:tabular-nums; color:#2b3140; }}
  .moons {{ display:flex; gap:2px; justify-content:flex-end; }}
  .moon {{ display:block; }}
  .festival {{ background:linear-gradient(180deg,#fdf6e9,#fbf3e0); border-color:#e7d6b4; }}
  .festival .fgrid {{ display:flex; gap:6px; flex-wrap:wrap; }}
  .cell.fest {{ flex:1 1 60px; aspect-ratio:auto; min-height:64px;
    background:#fffdf7; border-color:#ecdcbb; }}
</style>
<header>
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="legend">{legend}</div>
</header>
<main>
{blocks}
</main>
</html>"""


def render_year_text(cal: Calendar, year: int) -> str:
    L = cal.week.length
    out = [f"{cal.name} - Year {year} ({cal.year_length(year)} days)"]
    ordinal = cal._days_before_year(year)

    for seg in cal.segments(year):
        out.append("")
        out.append(f"  {seg.name}" + ("" if seg.in_week else "   [outside the week]"))

        if seg.in_week:
            out.append(
                "   " + " ".join(f"{cal.week.name_for(i)[:3]:>3}" for i in range(L))
            )
            row = ["   "]
            fw = cal.weekday_of_ordinal(ordinal) or 0
            row += ["   "] * fw

            for d in range(seg.days):
                row.append(f"{d + 1:>3}")
                if len(row) - 1 == L:
                    out.append(" ".join(row))
                    row = ["   "]

            if len(row) > 1:
                out.append(" ".join(row))

        else:
            out.append("   " + "  ".join(f"[{d + 1}]" for d in range(seg.days)))
        ordinal += seg.days

    return "\n".join(out)
