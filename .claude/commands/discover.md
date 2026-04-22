# Discover — fill initial project docs (no OMC required)

Use this command when the project owner has a **vague or partial idea** and the repo still has **template placeholders** in `docs/` or `CLAUDE.md`.

## Read first

1. `docs/DISCOVERY.md` — full ideation spine (interview → options → docs → self-review).
2. Current templates: `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`, `docs/UI_GUIDE.md`, `CLAUDE.md`.

## Your job

1. Classify **greenfield vs brownfield**; if brownfield, explore the repo before asking obvious questions.
2. Run a **lightweight interview** (one question at a time) until goal, user, MVP boundary, and top risks are clear—or the user says to proceed.
3. Produce **RALPLAN-lite**: principles, decision drivers, **≥2 options** with pros/cons, recommendation and rejected alternatives.
4. **Rewrite** the five files above: no `{curly brace}` template fragments; use real names, stacks, and rules. For UI-light projects, still fill `UI_GUIDE.md` with “N/A” sections or point to a future milestone—do not leave skeleton tutorial text if it would mislead implementers.
5. **Analyst → architect → critic** pass on your own output; fix contradictions.
6. Tell the user to run **verification** in `templates/discovery/0-discovery/step4.md` (or run that phase via `execute.py` if they copied the template).

## Optional: runnable discovery phase

To run discovery like other harness phases, copy the folder:

`cp -R templates/discovery/0-discovery phases/0-discovery`

Edit `phases/0-discovery/index.json` (`project`, `phase` if you rename the directory). Append `0-discovery` to `phases/index.json` if you use the rollup file. Then:

`python3 scripts/execute.py 0-discovery`

## After discovery

When docs are real, use `.claude/commands/harness.md` to design **implementation** phases (`1-mvp`, etc.) and run `execute.py` on those.
