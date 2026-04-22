# Step 2: adr-decisions

## Files to read

- `/docs/DISCOVERY.md` (§5 self-review hint)
- `/docs/ADR.md` (template)
- `/docs/ARCHITECTURE.md`
- `/CLAUDE.md`

## Work

1. Replace `docs/ADR.md` with at least **three** real ADRs (rename titles from `ADR-001`, …). Each must include **Decision**, **Rationale**, **Tradeoffs**—not placeholders.
2. ADRs should encode the big choices from step 1 (framework, data layer, auth/deployment, etc.). Link decisions to the options you rejected where helpful.

## Acceptance Criteria

```bash
! grep -F '### ADR-001: {Decision' docs/ADR.md
! grep -F '{What was chosen}' docs/ADR.md
```

## Verification procedure

1. Run AC; do a quick **critic pass**: does any ADR contradict `ARCHITECTURE.md` or `CLAUDE.md`?
2. Update `phases/0-discovery/index.json` step `2`.

## Do not

- Do not leave generic `{Decision` / `{Rationale` template lines.
