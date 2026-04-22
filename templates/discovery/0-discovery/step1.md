# Step 1: stack-arch-claude

## Files to read

- `/docs/DISCOVERY.md` (§3 Options, §4 Write artifacts)
- `/docs/PRD.md`
- `/docs/ARCHITECTURE.md` (template)
- `/CLAUDE.md` (template)

## Work

1. Apply **RALPLAN-lite** from `DISCOVERY.md`: document principles, drivers, **≥2** stack/architecture options with pros/cons, then state the **chosen** approach and why alternatives were rejected.
2. Rewrite `docs/ARCHITECTURE.md` to match the chosen approach (directory layout, patterns, data flow, state). Replace placeholders with real structure—even if some areas say “deferred to ADR-00x”.
3. Rewrite `CLAUDE.md`: real project name, **tech stack**, **CRITICAL** rules that match ADRs you will add next, and **Commands** that exist or will exist for this repo (adjust if not Node—e.g. `make test`).

## Acceptance Criteria

```bash
! grep -F '{Design patterns' docs/ARCHITECTURE.md
! grep -F '{How data flows' docs/ARCHITECTURE.md
! grep -F '# Project: {project name}' CLAUDE.md
! grep -F '{Framework (e.g.' CLAUDE.md
```

## Verification procedure

1. Run AC commands; skim PRD vs ARCHITECTURE vs CLAUDE for contradictions.
2. Update `phases/0-discovery/index.json` step `1` with `status` and `summary`.

## Do not

- Do not claim tools in `CLAUDE.md` **Commands** that are not true for this repo (fix the section to match reality).
