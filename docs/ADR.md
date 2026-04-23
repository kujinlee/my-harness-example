# Architecture Decision Records

## Philosophy
Ship the MVP fast. No server, no database, no auth. Everything runs in the browser. Minimize dependencies.

---

### ADR-001: Vite + React + TypeScript
**Decision**: Use Vite as the build tool with React and TypeScript.
**Rationale**: No server-side rendering needed. Vite is fast to set up with no backend required. TypeScript prevents API shape mismatches.
**Tradeoffs**: API keys are exposed in the browser bundle — acceptable for a personal/local tool. Do not deploy publicly without adding a backend proxy.

### ADR-002: Claude API called client-side via fetch
**Decision**: Call the Anthropic API directly from the browser using `fetch`, with `VITE_ANTHROPIC_API_KEY` from `.env`. Do not install `@anthropic-ai/sdk`.
**Rationale**: No backend to maintain. Raw `fetch` is sufficient for a single POST call.
**Tradeoffs**: API key is visible in the browser bundle; acceptable for local/personal use only.

### ADR-003: YouTube Data API v3, top 100 by relevance
**Decision**: Use `commentThreads.list` with `order=relevance` and `maxResults=100`.
**Rationale**: "Relevance" order surfaces the most engaged comments, the best available proxy for top-by-likes without a secondary sort pass.
**Tradeoffs**: Not a strict like-count sort; highly recent comments may rank lower than expected.
