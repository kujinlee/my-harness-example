# Step 3: report-ui

## Files to read

- `/docs/ARCHITECTURE.md`
- `/docs/UI_GUIDE.md`
- `/src/types/index.ts`
- `/src/services/youtube.ts`
- `/src/services/analysis.ts`

Follow UI_GUIDE.md exactly. No colors, components, or patterns outside of it.

## Work

Build the complete UI across `src/App.tsx` and two components.

### `src/App.tsx` — state and orchestration

```typescript
type Status = 'idle' | 'fetching' | 'analyzing' | 'done' | 'error'

// State:
const [url, setUrl] = useState('')
const [status, setStatus] = useState<Status>('idle')
const [report, setReport] = useState<AnalysisReport | null>(null)
const [errorMessage, setErrorMessage] = useState('')
```

On form submit:
1. Call `parseVideoId(url)`. If `null`, set inline error "Invalid YouTube URL" without changing `status`.
2. `setStatus('fetching')` → `fetchComments(videoId)`
3. `setStatus('analyzing')` → `analyzeComments(comments)`
4. `setStatus('done')` → `setReport(result)`
5. On any thrown error: `setStatus('error')`, `setErrorMessage(err.message)`

Page layout (max-w-3xl, left-aligned, px-6 py-12):
```
<header>
  <h1>YouTube Comment Analyzer</h1>
  <p>Paste a video URL to get audience feedback</p>
</header>

<URLInput ... />

{status === 'error' && <p className="text-[#ef4444] text-sm mt-3">{errorMessage}</p>}

{status === 'done' && report && (
  <div className="mt-8 animate-fade-in">
    <ReportDisplay report={report} />
  </div>
)}
```

Add the fade-in keyframe to `src/index.css`:
```css
@keyframes fade-in {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 0.3s ease forwards;
}
```

### `src/components/URLInput.tsx`

Props:
```typescript
interface Props {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  disabled: boolean
  status: Status
}
```

Renders:
- A full-width text input (styled per UI_GUIDE Input fields spec). Placeholder: "https://www.youtube.com/watch?v=..."
- A submit button to the right labeled:
  - `"Analyze"` when `status` is `idle`, `done`, or `error`
  - `"Fetching comments…"` when `status === 'fetching'`
  - `"Analyzing…"` when `status === 'analyzing'`
  - Button is disabled (and styled per UI_GUIDE Disabled spec) when `disabled` is true
- A status line below the row in `text-neutral-400 text-sm` (only visible when fetching or analyzing):
  - `"Fetching top 100 comments…"` when fetching
  - `"Analyzing with Claude…"` when analyzing

### `src/components/ReportDisplay.tsx`

Props:
```typescript
interface Props {
  report: AnalysisReport
}
```

Renders top to bottom:

1. **Overall sentiment pill** — one pill badge:
   - `"Positive"` → `bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20`
   - `"Negative"` → `bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20`
   - `"Neutral"` or `"Mixed"` → `bg-neutral-800 text-neutral-300 border border-neutral-700`
   - No other colors.

2. **Sentiment breakdown bars** — three rows (Positive / Neutral / Negative). Each row:
   ```
   <label text-xs text-neutral-400 w-16> <bar div bg-color h-2 rounded-sm> <percentage text-xs text-neutral-400>
   ```
   Use inline `style={{ width: `${pct}%` }}` on the bar div. No chart library.
   Colors: Positive `#22c55e`, Negative `#ef4444`, Neutral `#525252`.

3. **Strengths section** — heading "What's Working", then for each `FeedbackTheme` in `report.strengths`:
   ```
   Card (rounded-md bg-[#141414] border border-neutral-800 p-4):
     <p className="text-sm font-medium text-white">{theme}</p>
     <p className="text-sm text-neutral-300 mt-1">{description}</p>
     <p className="text-xs text-neutral-500 italic mt-2">"{exampleComment}"</p>
   ```

4. **Improvements section** — heading "Areas to Improve", same card structure as strengths.

5. **Footer** — `text-xs text-neutral-500 mt-6`: "Based on {report.commentCount} comments"

## Acceptance Criteria

```bash
npm run build   # no TypeScript or Vite errors
npm run dev     # app loads, URL input visible on dark background
```

## Verification procedure

1. Run `npm run build`. Must exit 0.
2. Run `npm run dev`. Open the browser and confirm:
   - Dark (#0a0a0a) background with "YouTube Comment Analyzer" heading.
   - URL input and "Analyze" button are present.
   - Entering an invalid URL shows "Invalid YouTube URL" inline without crashing.
3. Visually inspect for AI slop antipatterns from UI_GUIDE.md: no blur, no gradient text, no purple/indigo, no glow animations.
4. Update `/phases/0-mvp/index.json` step 3 to `"status": "completed"` with a one-line `"summary"`.

## Do not

- Do not install charting libraries (recharts, chart.js, d3, etc.). Reason: sentiment bars are simple CSS width divs.
- Do not add animations beyond the report fade-in. Reason: UI_GUIDE.md disallows all other animation.
- Do not use purple, indigo, or gradient colors. Reason: UI slop antipatterns.
- Do not add features beyond this list (no export, no share, no history). Reason: MVP scope only per PRD.md.
