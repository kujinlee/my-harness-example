# Discovery phase template

Copy this tree into the repo root so the harness can run it like any other phase:

```bash
cp -R templates/discovery/0-discovery phases/0-discovery
```

Then:

1. Edit `phases/0-discovery/index.json` — set `"project"` and ensure `"phase"` matches the phase slug you use for the git branch (`feat-<phase>`).
2. If you use `phases/index.json`, add `{ "dir": "0-discovery", "status": "pending" }` to the `phases` array.
3. Read `docs/DISCOVERY.md` with the user (or let Claude follow `.claude/commands/discover.md`).
4. Run: `python3 scripts/execute.py 0-discovery`

Remove or archive `docs/_discovery_notes.md` after the phase if you used it.
