# Step 4: verify-docs

## Files to read

- `/docs/PRD.md`, `/docs/ARCHITECTURE.md`, `/docs/ADR.md`, `/docs/UI_GUIDE.md`, `/CLAUDE.md`
- `/docs/DISCOVERY.md` (§5 analyst/architect/critic pass)

## Work

1. Run an **analyst → architect → critic** pass (single session): list any contradictions or vague spots; **fix the docs** in this step if fixes are small. If something needs user input, set step to `blocked` with a clear `blocked_reason`.
2. Confirm no template skeleton remains for the patterns below (extend the script if you changed templates).

## Acceptance Criteria

```bash
set -e
for f in docs/PRD.md docs/ARCHITECTURE.md docs/ADR.md docs/UI_GUIDE.md CLAUDE.md; do
  test -f "$f"
done
! grep -F '# PRD: {Project name}' docs/PRD.md
! grep -F '# Project: {project name}' CLAUDE.md
! grep -F '### ADR-001: {Decision' docs/ADR.md
! grep -F '{Design patterns' docs/ARCHITECTURE.md
! grep -F '{Principle 1' docs/UI_GUIDE.md
```

## Verification procedure

1. Run AC commands; read all five files end-to-end once.
2. Optionally remove `docs/_discovery_notes.md` if present and no longer needed.
3. Update `phases/0-discovery/index.json` step `4` to `completed` with a summary listing the five files as ready for implementation planning.

## Do not

- Do not mark complete if any AC command fails.
