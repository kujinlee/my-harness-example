import type { Comment } from '../types'

export function parseVideoId(url: string): string | null {
  try {
    const parsed = new URL(url)
    if (parsed.hostname === 'youtu.be') {
      const id = parsed.pathname.slice(1)
      return id || null
    }
    if (parsed.hostname === 'www.youtube.com' || parsed.hostname === 'youtube.com') {
      if (parsed.pathname === '/watch') {
        return parsed.searchParams.get('v')
      }
      if (parsed.pathname.startsWith('/shorts/')) {
        const id = parsed.pathname.slice('/shorts/'.length)
        return id || null
      }
    }
    return null
  } catch {
    return null
  }
}

export async function fetchComments(videoId: string): Promise<Comment[]> {
  const apiKey = import.meta.env.VITE_YOUTUBE_API_KEY
  if (!apiKey) {
    throw new Error('YouTube API key is not configured')
  }

  const params = new URLSearchParams({
    part: 'snippet',
    videoId,
    order: 'relevance',
    maxResults: '100',
    key: apiKey,
  })

  const res = await fetch(`https://www.googleapis.com/youtube/v3/commentThreads?${params}`)

  if (!res.ok) {
    let message = `YouTube API error: ${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      const apiMessage = body?.error?.message
      if (apiMessage) message = `YouTube API error: ${apiMessage}`
    } catch {
      // ignore parse failure, use status message
    }
    throw new Error(message)
  }

  const data = await res.json()

  return (data.items ?? []).map((item: any): Comment => ({
    id: item.id,
    text: item.snippet.topLevelComment.snippet.textDisplay,
    likeCount: item.snippet.topLevelComment.snippet.likeCount,
    authorName: item.snippet.topLevelComment.snippet.authorDisplayName,
    publishedAt: item.snippet.topLevelComment.snippet.publishedAt,
  }))
}
