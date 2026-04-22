# Discovery — from vague idea to filled docs

This document is the **ideation spine** for this repo. It condenses useful patterns from **oh-my-claudecode** (OMC) skills—**deep-interview** (Socratic clarification), **omc-plan** (interview vs direct planning), and **RALPLAN-DR-style** option comparison—into a **self-contained** workflow. **OMC does not need to be installed** to use the Harness framework.

Use it when `docs/PRD.md`, `ARCHITECTURE.md`, `ADR.md`, and `UI_GUIDE.md` (and `CLAUDE.md`) still contain template placeholders.

---

## 1. Decide greenfield vs brownfield

- **Brownfield**: repo already has meaningful code or product behavior. **Read the codebase first** (tree, package manifest, main entrypoints), then ask the user only questions you cannot answer from the repo.
- **Greenfield**: empty or scaffold-only. Rely on the user’s brief and constraints.

---

## 2. Interview (lightweight “deep interview”)

Goals: expose assumptions, nail scope, surface constraints—not to build a feature list in one pass.

Rules (from OMC deep-interview / plan):

1. **One question at a time** (or one small batch only if tightly related).
2. **Prefer questions that falsify assumptions** (“What would make this approach wrong?”) over open-ended brainstorming.
3. **Name the weakest area** before each question (e.g. “We still don’t know who pays or what ‘done’ means.”).
4. Stop when you can state **goal**, **primary user**, **MVP boundary**, and **top 3 risks** in your own words without hedging—or when the user asks to proceed.

Optional: keep a scratch file `docs/_discovery_notes.md` during the session; delete or trim it before marking the discovery phase complete.

---

## 3. Options before commitment (“RALPLAN-lite”)

Before writing real ADRs, produce a short **comparison block** (in chat or in `_discovery_notes.md`):

| Section | Content |
|--------|---------|
| **Principles** | 3–5 non-negotiables (e.g. “minimal deps”, “must work offline”). |
| **Decision drivers** | Top 3 forces (team skill, time-to-ship, compliance, etc.). |
| **Options** | At least **2** viable stacks or architectures; for each: **pros**, **cons**, **what we give up**. |
| **Recommendation** | One primary choice + **why alternatives were rejected**. |

High-risk areas (auth, PII, migrations, public API): expand **risks** and **verification** ideas; consider a second review pass before locking ADRs.

---

## 4. Write artifacts (map to repo files)

| Output | File | Intent |
|--------|------|--------|
| Product intent | `docs/PRD.md` | Goal, users, MVP features, **out of scope**, rough design direction |
| System shape | `docs/ARCHITECTURE.md` | Layout, patterns, data flow, state—aligned with PRD |
| Decisions | `docs/ADR.md` | ADR-001… with **Decision / Rationale / Tradeoffs** (link options above) |
| UI constraints | `docs/UI_GUIDE.md` | Principles, colors, components—only if the product has UI |
| Agent + stack rules | `CLAUDE.md` | Real project name, stack, CRITICAL rules, commands |

Replace every `{placeholder}` from the templates with concrete text. If something is genuinely undecided, write **TBD** plus **who decides by when**—do not leave curly-brace template tokens.

---

## 5. Analyst / architect / critic (single-agent simulation)

OMC runs separate agent roles; here you approximate **one session, three passes**:

1. **Analyst pass** — Hidden requirements, edge cases, “what if user does X?”, metrics for success.
2. **Architect pass** — Boundaries, failure modes, consistency with ADRs and directory layout.
3. **Critic pass** — Contradictions between PRD and ARCHITECTURE, vague ADRs, untestable claims.

Fix gaps in the docs; do not start implementation phases until contradictions are resolved or explicitly accepted by the user.

---

## 6. Invoking discovery in this repo

- **Chat-only**: follow this file and the **Discover** command (`.claude/commands/discover.md`).
- **Harness phase**: copy `templates/discovery/0-discovery/` → `phases/0-discovery/`, edit `index.json` (`project`, `phase`), then run `python3 scripts/execute.py 0-discovery` so each step runs with the same guardrails as implementation phases.

---

## Attribution

Discovery methodology here is **inspired by** OMC’s **deep-interview**, **plan (omc-plan)**, and **RALPLAN-DR** option structure. This framework ships **documentation only**; it does not copy OMC code, hooks, or MCP. More OMC ideas can be folded into this file later as needed.
