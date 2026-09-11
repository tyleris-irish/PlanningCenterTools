# Rotation builder (annual Sunday Teams schedule)

This folder is a **template**, not a CLI tool you run standalone (unlike the rest of
this repo). The real, once-a-year job — turning each team's roster + a
recommitment form + a pile of scheduling requests into a 3-week rotation — has too
many one-off human judgment calls to fully automate. Instead, Claude writes a
fresh copy of `build_rotation_template.py` every fall, working from this
scaffold, and iterates on it live with whoever's building the schedule.

Full process, copy-paste starter prompts, and the complete rule set live in the
**"Planning Center" collection on the wiki**:

- **Fall Semester Schedule Revamp** — the annual from-scratch build
- **Small Schedule Changes** — day-to-day adds/moves/swaps once the rotation exists
- **Reference: How the Rotation System Works** — every rule, flag type, and
  deliverable explained

## What's here

- `build_rotation_template.py` — a runnable, fully-commented scaffold: parses
  team roster CSVs, assigns each person a week (defaulting to their prior-year
  week, overridden only for a real constraint), and writes the Planning
  Center import CSVs + an xlsx "who's scheduled twice" cross-check.
- `sample_input/` — fabricated example roster CSV (fake names, `.csv.example`
  like the rest of the repo's samples) showing the exact shape Claude expects:
  `name,team,position,rotation,Notes,26-27 Yes?,Returning/New`. Real team
  files are the same shape, one file per team, named
  `Sunday Teams - <Team>.csv`.

Run it as-is against the sample data:

```bash
cd rotation-builder
python build_rotation_template.py   # writes ./output/*.csv (+ .xlsx if openpyxl is installed)
```

**No real volunteer names, notes, or scheduling requests ever belong in this
repo** (it's public). Each year's actual input CSVs and the script Claude
customizes from this template stay local to whoever's running the build —
see the wiki for the exact prompt to hand Claude with that year's files
attached.
