# Architecture

## Directory structure
```
src/
├── components/    # React UI components (URLInput, ReportDisplay)
├── services/      # API clients: youtube.ts, analysis.ts
├── types/         # TypeScript interfaces (Comment, AnalysisReport)
└── App.tsx        # Root component: owns all state, orchestrates the flow
index.html
vite.config.ts
.env               # VITE_YOUTUBE_API_KEY, VITE_ANTHROPIC_API_KEY (not committed)
.env.example       # committed template with empty values
```

## Patterns
- Functional React components with hooks only. No class components.
- All API logic lives in `src/services/`. Components never call APIs directly.
- Single source of truth: `App.tsx` owns all state (`url`, `status`, `report`, `errorMessage`).

## Data flow
```
User inputs YouTube URL
  → App.tsx calls parseVideoId() to extract video ID
  → services/youtube.ts fetches top 100 comments via YouTube Data API v3
  → services/analysis.ts sends comments to Claude API, returns AnalysisReport JSON
  → ReportDisplay component renders the structured report
```

## State management
Local React state in `App.tsx` only (`useState`). No Redux, Zustand, or Context needed.
