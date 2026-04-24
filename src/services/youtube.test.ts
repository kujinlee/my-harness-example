import { describe, it, expect, vi, beforeEach } from 'vitest'
import { parseVideoId, fetchComments } from './youtube'

// --- parseVideoId ---

describe('parseVideoId', () => {
  it('parses watch URL', () => {
    expect(parseVideoId('https://www.youtube.com/watch?v=AQOvNx87Urs')).toBe('AQOvNx87Urs')
  })

  it('parses youtu.be short URL', () => {
    expect(parseVideoId('https://youtu.be/AQOvNx87Urs')).toBe('AQOvNx87Urs')
  })

  it('parses shorts URL', () => {
    expect(parseVideoId('https://www.youtube.com/shorts/AQOvNx87Urs')).toBe('AQOvNx87Urs')
  })

  it('returns null for invalid URL', () => {
    expect(parseVideoId('not-a-url')).toBeNull()
  })

  it('returns null for unrecognised domain', () => {
    expect(parseVideoId('https://vimeo.com/123456')).toBeNull()
  })

  it('returns null for youtube.com without video ID', () => {
    expect(parseVideoId('https://www.youtube.com/')).toBeNull()
  })
})

// --- fetchComments ---

describe('fetchComments', () => {
  beforeEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it('throws when API key is not configured', async () => {
    vi.stubEnv('VITE_YOUTUBE_API_KEY', '')
    await expect(fetchComments('abc123')).rejects.toThrow('YouTube API key is not configured')
  })

  it('throws with API error message on non-2xx response', async () => {
    vi.stubEnv('VITE_YOUTUBE_API_KEY', 'fake-key')
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ error: { message: 'API key not valid' } }), { status: 400 })
    )
    await expect(fetchComments('abc123')).rejects.toThrow('YouTube API error: API key not valid')
  })

  it('maps API response to Comment[]', async () => {
    vi.stubEnv('VITE_YOUTUBE_API_KEY', 'fake-key')
    const mockItem = {
      id: 'comment-1',
      snippet: {
        topLevelComment: {
          snippet: {
            textDisplay: 'Great video!',
            likeCount: 42,
            authorDisplayName: 'Alice',
            publishedAt: '2024-01-01T00:00:00Z',
          },
        },
      },
    }
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ items: [mockItem] }), { status: 200 })
    )
    const comments = await fetchComments('abc123')
    expect(comments).toHaveLength(1)
    expect(comments[0]).toEqual({
      id: 'comment-1',
      text: 'Great video!',
      likeCount: 42,
      authorName: 'Alice',
      publishedAt: '2024-01-01T00:00:00Z',
    })
  })
})
