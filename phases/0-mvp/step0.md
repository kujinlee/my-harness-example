# Step 0: project-setup

## Files to read

- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

## Work

Scaffold a Vite + React + TypeScript project at the repo root (`/`). The harness scripts live under `scripts/`; the app files (`package.json`, `index.html`, `src/`, etc.) live at the root alongside them.

### 1. Create `package.json`

```json
{
  "name": "yt-comment-analyzer",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

Then install dependencies:
```bash
npm install react react-dom
npm install -D vite @vitejs/plugin-react typescript @types/react @types/react-dom tailwindcss @tailwindcss/vite
```

### 2. Create `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})
```

### 3. Create `tsconfig.json` and `tsconfig.app.json`

Standard Vite React TypeScript config. `tsconfig.app.json` must have `"strict": true` and `"moduleResolution": "bundler"`.

### 4. Create `index.html`

Standard Vite HTML entry point: `<div id="root">` and `<script type="module" src="/src/main.tsx">`.

### 5. Create `.env.example`

```
VITE_YOUTUBE_API_KEY=your_youtube_data_api_v3_key_here
VITE_ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Also create `.env` at the repo root with the same two keys set to empty strings. The user will fill them in before running.

### 6. Create `src/index.css`

```css
@import "tailwindcss";
```

### 7. Create `src/types/index.ts`

```typescript
export interface Comment {
  id: string
  text: string
  likeCount: number
  authorName: string
  publishedAt: string
}

export interface SentimentBreakdown {
  positive: number  // percentage 0–100
  neutral: number
  negative: number
}

export interface FeedbackTheme {
  theme: string
  description: string
  exampleComment: string
}

export interface AnalysisReport {
  overallSentiment: 'positive' | 'neutral' | 'negative' | 'mixed'
  sentimentBreakdown: SentimentBreakdown
  strengths: FeedbackTheme[]
  improvements: FeedbackTheme[]
  commentCount: number
}
```

### 8. Create `src/main.tsx`

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

### 9. Create `src/App.tsx` stub

Render a minimal dark page so the build can be verified:

```tsx
export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white flex items-start justify-center px-6 py-12">
      <h1 className="text-2xl font-semibold">YouTube Comment Analyzer</h1>
    </div>
  )
}
```

### 10. Create empty service/component directories

Create placeholder files so TypeScript can resolve the structure later:
- `src/services/.gitkeep`
- `src/components/.gitkeep`

## Acceptance Criteria

```bash
npm run build   # must exit 0 with no TypeScript or Vite errors
```

## Verification procedure

1. Run `npm run build`. Must exit 0.
2. Run `npm run dev` and open the browser. Confirm "YouTube Comment Analyzer" renders on a dark (#0a0a0a) background.
3. Confirm `src/types/index.ts` exports all five interfaces: `Comment`, `SentimentBreakdown`, `FeedbackTheme`, `AnalysisReport`.
4. Confirm `.env` exists at repo root and `.env.example` is present alongside it.
5. Update `/phases/0-mvp/index.json` step 0 to `"status": "completed"` with a one-line `"summary"`.

## Do not

- Do not implement any API calls in this step. Reason: YouTube and Claude clients belong in steps 1 and 2.
- Do not use `npm create vite@latest` interactively. Reason: the harness runs non-interactively; create all files manually or use `npm create vite@latest . -- --template react-ts` with `--yes` flags if available.
- Do not install `@anthropic-ai/sdk`. Reason: ADR-002 specifies raw `fetch`.
