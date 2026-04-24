# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is the **Harness framework** — a Python-based orchestration layer that drives multi-step, agentic Claude Code sessions. It is a meta-framework: you use it to automate implementation of *other* projects by breaking work into phases → steps → prompts, then running them unattended with self-correction and git integration.

## Commands

```bash
# Run a phase (executes all pending steps sequentially)
python3 scripts/execute.py <phase-dir>

# Run a phase and push the feature branch when done
python3 scripts/execute.py <phase-dir> --push

# Run tests
pytest scripts/test_execute.py

# Run a single test class
pytest scripts/test_execute.py::TestInvokeClaude

# Run a single test method
pytest scripts/test_execute.py::TestInvokeClaude::test_timeout_is_1800
```

## Architecture

### Core concept

Work is organized as: **phases** → **steps**. Each step is a markdown prompt file; `execute.py` runs it via `claude -p --dangerously-skip-permissions`, reads `index.json` to see if it completed/blocked/failed, retries up to 3× on failure, then commits and advances.

### Key files

- `scripts/execute.py` — the entire harness runtime (`StepExecutor` class). The only executable.
- `scripts/test_execute.py` — pytest safety-net tests; mock git and subprocess to stay unit-level.
- `.claude/commands/harness.md` — the `/harness` slash command: workflow guide for designing phases/steps.
- `.claude/commands/discover.md` — the `/discover` slash command: interactive discovery before implementation.
- `templates/discovery/0-discovery/` — copy-paste template for running discovery as a harness phase.

### Phase layout (runtime, not in this repo yet)

```
phases/
  index.json                     # top-level rollup (optional)
  <phase-dir>/
    index.json                   # step list + status (the control plane)
    step0.md, step1.md, ...      # prompt files (one per step)
    step0-output.json, ...       # Claude's raw stdout/stderr (written by harness)
```

### How `execute.py` drives a step

1. Reads `phases/<phase>/index.json` for the first `"pending"` step.
2. Builds a prompt: `CLAUDE.md` + `docs/*.md` (guardrails) + completed-step summaries + `stepN.md`.
3. Calls `claude -p --dangerously-skip-permissions --output-format json <prompt>` with a 1800s timeout.
4. Re-reads `index.json` — success is determined solely by the agent setting `status` to `"completed"`.
5. On non-completed: retries up to `MAX_RETRIES=3`, injecting the prior error into the prompt.
6. Commits: `feat(<phase>): step N — <name>` for code, `chore(<phase>): step N output` for metadata.

Branch and commit message prefix use the `"phase"` field from `index.json`, not the directory name. For example, directory `0-mvp` with `"phase": "mvp"` creates branch `feat-mvp` and commits like `feat(mvp): step 0 — setup`.

### `index.json` status machine

| Status | Meaning |
|---|---|
| `pending` | Eligible to run |
| `completed` | Agent set this; harness commits and advances |
| `blocked` | Human intervention needed; harness exits 2 |
| `error` | Failed after MAX_RETRIES; harness exits 1 |

To recover: set the step's `status` back to `"pending"`, remove `error_message`/`blocked_reason`, re-run.

## Development process

- CRITICAL: For new features, write tests first, then implement until tests pass (TDD)
- CRITICAL: Step files must include test setup in the first step of any phase, and `npm test` (or `pytest`) must be part of every step's Acceptance Criteria. Never use `npm run build` alone as the AC.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`)
- Harness tests mock `subprocess.run` and patch `ex.ROOT`; never hit real git or Claude in tests.
- Frontend tests use Vitest with `environment: 'node'` for service/logic tests; mock `fetch` with `vi.spyOn(globalThis, 'fetch')`.

## Slash commands

- `/harness` — workflow guide for designing phases and steps
- `/discover` — interactive discovery before implementation
- `/review` — review changed files against CLAUDE.md, ARCHITECTURE.md, and ADR

## Starting a new project with this framework

1. Fill in `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md` (currently template placeholders). These files are injected as guardrails into every step prompt, so fill them before running any phase.
2. If docs still have `{...}` placeholders, run discovery first:
   - Chat-led: follow `.claude/commands/discover.md`
   - Harness-led: `cp -R templates/discovery/0-discovery phases/0-discovery` then `python3 scripts/execute.py 0-discovery`
3. Use `/harness` to design phases and step files, then run `execute.py`.
