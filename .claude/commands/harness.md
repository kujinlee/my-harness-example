This project uses the Harness framework. Follow the workflow below when working.

---

## Before implementation

If `docs/PRD.md`, `ARCHITECTURE.md`, `ADR.md`, or `UI_GUIDE.md` (or `CLAUDE.md`) still use **template placeholders** (`{...}`), run **discovery** first so implementation phases have real guardrails:

- **Chat-led:** follow `.claude/commands/discover.md` and `docs/DISCOVERY.md`.
- **Harness-led:** copy `templates/discovery/0-discovery` → `phases/0-discovery`, edit `index.json`, add the phase to `phases/index.json` if used, then `python3 scripts/execute.py 0-discovery` (see `templates/discovery/README.md`).

Discovery content is **self-contained** (patterns adapted from oh-my-claudecode; OMC does not need to be installed).

---

## Workflow

### A. Explore

Read documentation under `/docs/` (PRD, ARCHITECTURE, ADR, etc.) to understand the project’s product intent, architecture, and design goals. Use Explore agents in parallel when helpful.

### B. Discuss

When something must be clarified or decided technically before implementation, surface it to the user and discuss.

### C. Step design

When the user asks for an implementation plan, produce a draft split into multiple steps and ask for feedback.

Design principles:

1. **Minimize scope** — Each step covers one layer or module only. If several modules must change at once, split the steps.
2. **Self-contained** — Each step file runs in an independent Claude session. Do not use external references like “as discussed in the previous conversation.” Put everything needed inside the file.
3. **Force upfront prep** — List relevant document paths and paths of files created or modified in prior steps. Encourage the session to read code and build context before acting.
4. **Signature-level direction** — Specify function/class interfaces only; leave internals to the agent. Still spell out non-negotiable rules from the design intent (idempotency, security, data integrity, etc.).
5. **ACs are runnable commands** — Avoid vague statements like “X should work.” Include real verification commands such as `npm run build && npm test`.
6. **Warnings must be concrete** — Instead of “be careful,” write “Do not do X. Reason: Y.”
7. **Naming** — Step names are kebab-case slugs expressing the core module or work in one or two words (e.g. `project-setup`, `api-layer`, `auth-flow`).

### D. File creation

After the user approves, create the following files.

#### D-1. `phases/index.json` (overall status)

Top-level index for managing multiple tasks. If it already exists, append a new entry to the `phases` array.

```json
{
  "phases": [
    {
      "dir": "0-mvp",
      "status": "pending"
    }
  ]
}
```

- `dir`: Task directory name.
- `status`: `"pending"` | `"completed"` | `"error"` | `"blocked"`. `execute.py` updates this automatically while running.
- Timestamps (`completed_at`, `failed_at`, `blocked_at`) are recorded automatically by `execute.py` on status changes. Do not set them when creating the file.

#### D-2. `phases/{task-name}/index.json` (task detail)

```json
{
  "project": "<project-name>",
  "phase": "<task-name>",
  "steps": [
    { "step": 0, "name": "project-setup", "status": "pending" },
    { "step": 1, "name": "core-types", "status": "pending" },
    { "step": 2, "name": "api-layer", "status": "pending" }
  ]
}
```

Field rules:

- `project`: Project name (see CLAUDE.md).
- `phase`: Task name. Must match the directory name.
- `steps[].step`: Zero-based sequence number.
- `steps[].name`: kebab-case slug.
- `steps[].status`: Initial value is always `"pending"`.

Status transitions and auto-recorded fields:

| Transition | Fields recorded | Recorded by |
|------|-------------|----------|
| → `completed` | `completed_at`, `summary` | Claude session (summary), execute.py (timestamp) |
| → `error` | `failed_at`, `error_message` | Claude session (message), execute.py (timestamp) |
| → `blocked` | `blocked_at`, `blocked_reason` | Claude session (reason), execute.py (timestamp) |

`summary` is a one-line description of the step’s output when it completes; `execute.py` accumulates it as context for the next step’s prompt. Include information useful for the next step (created files, key decisions, etc.).

`created_at` is written once at task level by `execute.py` on first run. Step-level `started_at` is also written automatically by `execute.py` when each step starts. Do not set these when creating the file.

#### D-3. `phases/{task-name}/step{N}.md` (one per step)

```markdown
# Step {N}: {name}

## Files to read

Read the following first to understand the project’s architecture and design intent:

- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {paths of files created or modified in previous steps}

Read code from prior steps carefully and understand the design intent before working.

## Work

{Concrete implementation instructions: file paths, class/function signatures, logic description.
Keep code snippets at interface/signature level only; leave implementations to the agent.
Still spell out non-negotiable rules that must not diverge from the design intent.}

## Acceptance Criteria

```bash
npm run build   # no compile errors
npm test        # tests pass
```

## Verification procedure

1. Run the AC commands above.
2. Check the architecture checklist:
   - Does the layout follow ARCHITECTURE.md?
   - Does the stack stay within ADR?
   - Are there any CLAUDE.md CRITICAL rule violations?
3. Update the corresponding step in `phases/{task-name}/index.json` based on the outcome:
   - Success → `"status": "completed"`, `"summary": "one-line summary of output"`
   - Still failing after three fix attempts → `"status": "error"`, `"error_message": "specific error details"`
   - User intervention required (API keys, external auth, manual setup, etc.) → `"status": "blocked"`, `"blocked_reason": "specific reason"` then stop immediately

## Do not

- {What this step must not do. Use “Do not do X. Reason: Y.”}
- Do not break existing tests
```

### E. Execution

```bash
python3 scripts/execute.py {task-name}        # run sequentially
python3 scripts/execute.py {task-name} --push  # run then push
```

What `execute.py` handles automatically:

- Create/checkout `feat-{task-name}` branch
- Guardrail injection — include CLAUDE.md + docs/*.md in every step’s prompt
- Context accumulation — pass completed step summaries into the next step’s prompt
- Self-correction — on failure, up to three retries with prior error messages fed back into the prompt
- Two-phase commits — separate commits for code changes (`feat`) and metadata (`chore`)
- Timestamps — automatic `started_at`, `completed_at`, `failed_at`, `blocked_at`

Error recovery:

- **On error**: In `phases/{task-name}/index.json`, set that step’s `status` back to `"pending"`, remove `error_message`, then re-run.
- **On blocked**: Resolve what `blocked_reason` describes, set `status` to `"pending"`, remove `blocked_reason`, then re-run.
