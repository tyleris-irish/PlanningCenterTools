#!/usr/bin/env python3
"""
Sunday Teams rotation builder — ANNUAL TEMPLATE, not a ready-to-run tool.

This is a scaffold of the script Claude writes fresh every fall when it does the
big schedule revamp (see the "Planning Center" wiki collection, doc "Fall
Semester Schedule Revamp"). It contains NO real names — every person below is
fictional ("Alex Example", "Jordan Sample", ...) so this can live in a public
repo. Point Claude at this file each year and say "use the pattern in
rotation-builder/build_rotation_template.py, fed with this year's CSVs" rather
than starting from a blank page.

WHAT THIS DOES
  1. Parses each team's roster CSV (`sample_input/Sunday Teams - <Team>.csv`) —
     the ONLY source of who is on a team and what position they hold. A
     person's team/role never comes from the prior-year export or the
     recommitment form; those are read-only context for WEEK placement and
     scheduling constraints (pairings, "can't serve with X the same day", etc).
  2. Fills in a week (of a 3-week rotation) for every person: default = their
     own last-year week from the roster file; only overridden for a hard
     constraint (see WEEK_OVERRIDE) or because they're new (see NEW_WEEK).
  3. Optionally locks one team's rotation verbatim (e.g. if that ministry
     builds its own schedule and hands it to you as-is — see LOCKED_TEAMS).
  4. Writes the three per-week CSVs Planning Center imports
     (`id,name,team,position,rotation`, id left blank = import as new) plus an
     xlsx "By Person" cross-check that flags anyone scheduled 2+ times.

WHAT REAL YEARS ADD ON TOP (ask Claude for these; not in this template because
they need real per-person judgment calls, not generic code):
  - "LG Ministry" (or any other Planning Center custom field) balancing across
    weeks — pull via the `planningcenter` MCP `people_field_data` /
    `people_search` tools, join by name, then swap a HANDFUL of unconstrained
    people between weeks to fix only the worst imbalance. Don't force perfect
    balance — some cohorts (e.g. spouses on one team) can't move.
  - Publix/volunteer "pick-up" style roles that ride along with someone's real
    assignment rather than adding a duplicate row for them.
  - A phone-friendly, dependency-free HTML the schedule can be texted to a
    group chat (search-a-name, by-week, by-team views, "still needed" tags
    driven off Planning Center's per-position weekly counts).
  - A richer internal HTML with conflict highlighting, for the person building
    the schedule to iterate in.
  See the wiki doc "Reference: How the Rotation System Works" for the full
  rule set (locked-team same-day rule, pairing types, flag taxonomy, etc).

Run it as: python build_rotation_template.py   (writes ./output/*.csv + .xlsx)
"""
import csv
import collections
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_DIR = os.path.join(HERE, "sample_input")
OUT_DIR = os.path.join(HERE, "output")

WEEKS = ["W1", "W2", "W3"]
ROT_LABEL = {"W1": "2026-2027 Week 1", "W2": "2026-2027 Week 2", "W3": "2026-2027 Week 3"}

# ---------------------------------------------------------------------------
# 1) Teams. One roster file per team, named "Sunday Teams - <Team>.csv".
# ---------------------------------------------------------------------------
TEAM_FILE = {
    "Sunday Teams - Example Team.csv.example": "Example Team",
}

# A team whose rotation is dictated by someone else (e.g. a ministry that
# builds its own 3-week schedule and hands you a screenshot). Transcribe it
# verbatim as {position: [week1_name, week2_name, week3_name]}; a blank string
# means that ministry left the slot open on purpose — leave it open, don't fill it.
LOCKED_TEAMS = {
    # "Kids Ministry Team": {
    #     "Oversight": ["Alex Example", "Jordan Sample", "Taylor Demo"],
    #     "Pre K: Teacher": ["Casey Placeholder", "Jamie Fixture", ""],  # W3 intentionally open
    # },
}

# name as written in a roster/locked-team file -> the one canonical spelling
# to use everywhere (nicknames, typos, "Firstname (Nickname) Lastname", etc.)
NAME_FIX = {
    # "Bobby Tables": "Robert Tables",
}
def canon(name: str) -> str:
    name = name.strip()
    return NAME_FIX.get(name, name)


def week_of(rotation_text: str):
    """'2025-2026 Week 2' -> 'W2'; blank/unrecognized -> None."""
    text = (rotation_text or "").strip()
    for w in WEEKS:
        if text.endswith("Week " + w[1]):
            return w
    return None


# best-guess role for a roster row with no position (a brand-new volunteer) -
# never a Team Lead / specialist role, only a catch-all
GUESS_ROLE = {
    "Example Team": "General",
}

# ---------------------------------------------------------------------------
# 2) Hard, per-person overrides. Everything else defaults to the roster file's
#    OWN last-year week. Only touch a week here when a real constraint forces
#    it (a spouse/roommate/sibling pairing, "can't serve two roles the same
#    Sunday", someone new who needs a week assigned). Comment WHY on every line
#    - a future you (or a future Claude) needs the reason, not just the result.
# ---------------------------------------------------------------------------
WEEK_OVERRIDE = {
    # ("Alex Example", "Example Team", "Team Lead"): "W2",  # = spouse Jordan Sample, locked Kids W2
}
NEW_WEEK = {
    # ("Casey Placeholder", "Example Team"): "W1",  # new volunteer, placed to balance headcount
}

# people removed from ONE team even though a roster file still lists them
# (their own form said they're stepping down / switching teams / etc.)
DROP = {
    # ("Alex Example", "Example Team"),
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def load_roster():
    raw = []
    for filename, team in TEAM_FILE.items():
        path = os.path.join(IN_DIR, filename)
        with open(path, newline="") as f:
            for row in csv.reader(f):
                if not row or not row[0].strip() or row[0].strip().lower() == "name":
                    continue
                name = canon(row[0])
                position = row[2].strip() if len(row) > 2 else ""
                file_week = week_of(row[3]) if len(row) > 3 else None
                returning = (row[6].strip().lower() if len(row) > 6 else "") == "returning"
                is_new = (not returning) or position == ""
                raw.append({"name": name, "team": team, "pos": position,
                            "fw": file_week, "new": is_new})
    raw = [d for d in raw if (d["name"], d["team"]) not in DROP]
    for d in raw:
        if d["pos"] == "":
            d["pos"] = GUESS_ROLE.get(d["team"], "General")
    return raw


def assign_weeks(raw):
    rows = []  # (week, team, position, name, tag)
    for d in raw:
        key3 = (d["name"], d["team"], d["pos"])
        key2 = (d["name"], d["team"])
        week = WEEK_OVERRIDE.get(key3) or d["fw"] or NEW_WEEK.get(key2) or "W1"
        tag = "guess" if key3 in WEEK_OVERRIDE else ("new" if d["new"] else "")
        rows.append((week, d["team"], d["pos"], d["name"], tag))
    for team, positions in LOCKED_TEAMS.items():
        for position, names in positions.items():
            for i, week in enumerate(WEEKS):
                if names[i].strip():
                    rows.append((week, team, position, canon(names[i]), "locked"))
    return rows


def write_week_csvs(rows):
    os.makedirs(OUT_DIR, exist_ok=True)
    for week in WEEKS:
        path = os.path.join(OUT_DIR, f"Rotation - {ROT_LABEL[week]}.csv")
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "name", "team", "position", "rotation"])
            for wk, team, position, name, _tag in sorted(rows, key=lambda r: (r[1], r[2], r[3])):
                if wk == week and name.strip():
                    # `id` left blank on purpose: last year's PCO export id is a
                    # per-ASSIGNMENT id, not a stable per-person id - reusing it
                    # risks Planning Center editing an old assignment. Import
                    # these rows as brand new schedule entries.
                    w.writerow(["", name, team, position, ROT_LABEL[week]])
        print("wrote", path)


def write_by_person_xlsx(rows):
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
    except ImportError:
        print("openpyxl not installed - skipping the xlsx cross-check (pip install openpyxl)")
        return

    by_person = collections.defaultdict(lambda: collections.defaultdict(list))
    for week, team, position, name, tag in rows:
        if name.strip():
            by_person[name][week].append((team, position))

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "By Person"
    ws.append(["Name", "# weeks", "Week 1", "Week 2", "Week 3"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    amber = PatternFill("solid", fgColor="FFE8B3")
    red = PatternFill("solid", fgColor="FFC9C2")
    for name in sorted(by_person):
        weeks = by_person[name]
        nweeks = sum(1 for w in WEEKS if weeks[w])
        row = [name, nweeks] + [
            "; ".join(f"{t} - {p}" for t, p in weeks[w]) for w in WEEKS
        ]
        ws.append(row)
        if nweeks >= 3:
            fill = red
        elif nweeks == 2:
            fill = amber
        else:
            fill = None
        if fill:
            for cell in ws[ws.max_row]:
                cell.fill = fill
    ws.column_dimensions["A"].width = 22
    for c in "CDE":
        ws.column_dimensions[c].width = 34

    path = os.path.join(OUT_DIR, "Rotation - By Person.xlsx")
    wb.save(path)
    print("wrote", path)
    print(
        "Amber rows = scheduled twice (fine if it's a second team); "
        "red = 3+ (almost always a mistake, unless it's a weekly staff/lead role)."
    )


if __name__ == "__main__":
    people = load_roster()
    schedule_rows = assign_weeks(people)
    write_week_csvs(schedule_rows)
    write_by_person_xlsx(schedule_rows)
