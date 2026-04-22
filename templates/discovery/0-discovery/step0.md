# Step 0: prd-from-brief

## Files to read

- `/docs/DISCOVERY.md`
- `/docs/PRD.md` (current template)
- `/CLAUDE.md` (for context only; do not rewrite this step)

## Work

1. Follow **§2 Interview** in `DISCOVERY.md`: confirm greenfield vs brownfield; ask one focused question at a time if anything material is still unknown.
2. Replace `docs/PRD.md` entirely with a real PRD: concrete **Goal**, **Users**, **Core features**, **Out of scope for MVP**, **Design**. No `{placeholder}` tokens.

## Acceptance Criteria

```bash
test -f docs/PRD.md
! grep -F '# PRD: {Project name}' docs/PRD.md
! grep -F '{One-line summary' docs/PRD.md
```

## Verification procedure

1. Run the AC commands above.
2. Re-read PRD: would a new engineer know what to *not* build?
3. Update `phases/0-discovery/index.json` step `0`: success → `"status": "completed"` and a one-line `"summary"`; otherwise follow harness retry rules.

## Do not

- Do not leave curly-brace template fragments in `docs/PRD.md`.
- Do not start implementation work in this step.
