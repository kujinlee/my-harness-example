# Step 1: youtube-client

## Files to read

- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- `/src/types/index.ts`

Read the types file carefully — `fetchComments` must return `Comment[]` exactly as defined there.

## Work

Create `src/services/youtube.ts` with two exported functions.

### Function 1: `parseVideoId`

```typescript
export function parseVideoId(url: string): string | null
```

Handle these URL formats:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

Return the video ID string, or `null` if none found.

### Function 2: `fetchComments`

```typescript
export async function fetchComments(videoId: string): Promise<Comment[]>
```

Call the YouTube Data API v3 `commentThreads.list` endpoint:
```
GET https://www.googleapis.com/youtube/v3/commentThreads
  ?part=snippet
  &videoId={videoId}
  &order=relevance
  &maxResults=100
  &key={VITE_YOUTUBE_API_KEY}
```

- Read the API key from `import.meta.env.VITE_YOUTUBE_API_KEY`.
- Throw `Error('YouTube API key is not configured')` if the env var is empty.
- Throw a descriptive `Error` on any non-2xx response — include the API error message from the response body.
- Map each item in `response.items` to a `Comment`:
  - `id`: `item.id`
  - `text`: `item.snippet.topLevelComment.snippet.textDisplay`
  - `likeCount`: `item.snippet.topLevelComment.snippet.likeCount`
  - `authorName`: `item.snippet.topLevelComment.snippet.authorDisplayName`
  - `publishedAt`: `item.snippet.topLevelComment.snippet.publishedAt`

## Acceptance Criteria

```bash
npm run build   # no TypeScript errors
```

## Verification procedure

1. Run `npm run build`. Must exit 0.
2. Manually verify in the browser console (or a quick inline test) that `parseVideoId` returns the correct ID for all three URL formats and `null` for an invalid string.
3. Confirm the function file is at `src/services/youtube.ts` and exports exactly `parseVideoId` and `fetchComments`.
4. Update `/phases/0-mvp/index.json` step 1 to `"status": "completed"` with a one-line `"summary"`.

## Do not

- Do not call the Claude API in this step. Reason: that belongs in step 2.
- Do not paginate beyond one API request (maxResults=100). Reason: 100 comments is the MVP cap per ADR-003.
- Do not install any additional npm packages. Reason: use native `fetch` only.
