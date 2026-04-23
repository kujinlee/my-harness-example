# Step 2: analysis-client

## Files to read

- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/src/types/index.ts`
- `/src/services/youtube.ts`

Read the types file carefully — `analyzeComments` must return `AnalysisReport` exactly as defined there.

## Work

Create `src/services/analysis.ts` with one exported function.

### Function: `analyzeComments`

```typescript
export async function analyzeComments(comments: Comment[]): Promise<AnalysisReport>
```

### API call

Call the Anthropic Messages API via `fetch`:

- **Endpoint**: `https://api.anthropic.com/v1/messages`
- **Method**: POST
- **Headers**:
  ```
  x-api-key: <VITE_ANTHROPIC_API_KEY>
  anthropic-version: 2023-06-01
  anthropic-dangerous-direct-browser-access: true
  Content-Type: application/json
  ```
- **Model**: `claude-haiku-4-5-20251001`
- **Max tokens**: 1024

Throw `Error('Anthropic API key is not configured')` if `import.meta.env.VITE_ANTHROPIC_API_KEY` is empty.

### Prompt

**System**:
```
You are an expert content analyst. Analyze YouTube comments and return a structured JSON report. Return only valid JSON with no explanation or markdown formatting.
```

**User** — build this message dynamically:
```
Analyze these ${comments.length} YouTube comments and return a JSON object with this exact structure:

{
  "overallSentiment": "positive" | "neutral" | "negative" | "mixed",
  "sentimentBreakdown": {
    "positive": <integer 0-100>,
    "neutral": <integer 0-100>,
    "negative": <integer 0-100>
  },
  "strengths": [
    { "theme": "...", "description": "...", "exampleComment": "..." }
  ],
  "improvements": [
    { "theme": "...", "description": "...", "exampleComment": "..." }
  ],
  "commentCount": <number of comments analyzed>
}

Rules:
- sentimentBreakdown values must sum to exactly 100.
- Provide 2–4 strengths and 2–4 improvements.
- Each exampleComment must be a direct quote from the comments below.
- overallSentiment should reflect the dominant tone.

Comments (format: "[{likeCount} likes] {text}"):
${comments.map(c => `[${c.likeCount} likes] ${c.text}`).join('\n')}
```

### Parsing

- Parse `response.content[0].text` as JSON.
- Cast the result to `AnalysisReport` and return it.
- Throw a descriptive error if the API returns non-2xx or if JSON parsing fails.

## Acceptance Criteria

```bash
npm run build   # no TypeScript errors
```

## Verification procedure

1. Run `npm run build`. Must exit 0.
2. Confirm the function is exported from `src/services/analysis.ts`.
3. Confirm it throws `Error('Anthropic API key is not configured')` when the env var is missing (check the guard at the top of the function).
4. Update `/phases/0-mvp/index.json` step 2 to `"status": "completed"` with a one-line `"summary"`.

## Do not

- Do not install `@anthropic-ai/sdk`. Reason: ADR-002 specifies raw `fetch`.
- Do not use a model other than `claude-haiku-4-5-20251001`. Reason: cost efficiency for comment analysis.
- Do not truncate the comments list before sending. Reason: the 100-comment cap is already enforced in step 1.
