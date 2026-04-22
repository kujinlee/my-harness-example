Review the changes in this project.

First read the following documents:
- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/docs/PRD.md`
- `/docs/UI_GUIDE.md`

Then inspect the changed files and verify them against the checklist below:

## Checklist

1. **Architecture compliance**: Does the change follow the directory structure defined in ARCHITECTURE.md?
2. **Tech stack compliance**: Does the change stay within the technology choices defined in the ADR?
3. **Tests present**: Are there tests for any new functionality?
4. **CRITICAL rules**: Does the change violate any CRITICAL rules in CLAUDE.md?
5. **Build succeeds**: Does the build command complete without errors?
6. **Product requirements**: Does the change align with the goals and scope defined in PRD.md?
7. **UI guidelines**: Does the change follow the patterns and standards defined in UI_GUIDE.md?

## Output format

| Item | Result | Notes |
|------|--------|-------|
| Architecture compliance | ✅/❌ | {details} |
| Tech stack compliance | ✅/❌ | {details} |
| Tests present | ✅/❌ | {details} |
| CRITICAL rules | ✅/❌ | {details} |
| Build succeeds | ✅/❌ | {details} |
| Product requirements | ✅/❌ | {details} |
| UI guidelines | ✅/❌ | {details} |

If anything fails, propose concrete fixes.
