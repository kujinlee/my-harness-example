# Step 3: ui-guide

## Files to read

- `/docs/PRD.md`
- `/docs/UI_GUIDE.md` (template)
- `/docs/ADR.md`

## Work

1. If the product has **no meaningful UI** (CLI-only, library, API-only): replace `docs/UI_GUIDE.md` with a short document stating that, what “UI” means if anything (e.g. `--help` only), and point to future work—**and remove all `{placeholder}` lines** from the old template.
2. If there **is** a UI: fill `UI_GUIDE.md` with concrete principles, colors, components, layout, typography, and allowed animation—aligned with PRD and ADRs.

## Acceptance Criteria

```bash
! grep -F '{Principle 1' docs/UI_GUIDE.md
! grep -F '{e.g. #0a0a0a}' docs/UI_GUIDE.md
```

## Verification procedure

1. Run AC; ensure UI guide does not contradict PRD “Design” section.
2. Update `phases/0-discovery/index.json` step `3`.

## Do not

- Do not leave the long “AI slop” table without deciding what still applies; trim or keep explicitly.
