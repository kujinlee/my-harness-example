import { describe, it, expect, vi, beforeEach } from 'vitest'
import { analyzeComments } from './analysis'
import type { Comment } from '../types'

const mockComments: Comment[] = [
  { id: '1', text: 'Love this!', likeCount: 10, authorName: 'Alice', publishedAt: '2024-01-01T00:00:00Z' },
  { id: '2', text: 'Very helpful', likeCount: 5, authorName: 'Bob', publishedAt: '2024-01-02T00:00:00Z' },
]

const validReport = {
  overallSentiment: 'positive',
  sentimentBreakdown: { positive: 80, neutral: 15, negative: 5 },
  strengths: [{ theme: 'Content quality', description: 'Clear explanations', exampleComment: 'Love this!' }],
  improvements: [{ theme: 'Pacing', description: 'Could be faster', exampleComment: 'Very helpful' }],
  commentCount: 2,
}

describe('analyzeComments', () => {
  beforeEach(() => {
    vi.unstubAllEnvs()
    vi.restoreAllMocks()
  })

  it('throws when API key is not configured', async () => {
    vi.stubEnv('VITE_ANTHROPIC_API_KEY', '')
    await expect(analyzeComments(mockComments)).rejects.toThrow('Anthropic API key is not configured')
  })

  it('throws on non-2xx API response', async () => {
    vi.stubEnv('VITE_ANTHROPIC_API_KEY', 'fake-key')
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ error: { message: 'Invalid API key' } }), { status: 401 })
    )
    await expect(analyzeComments(mockComments)).rejects.toThrow('Anthropic API error: Invalid API key')
  })

  it('parses plain JSON response', async () => {
    vi.stubEnv('VITE_ANTHROPIC_API_KEY', 'fake-key')
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        content: [{ text: JSON.stringify(validReport) }],
      }), { status: 200 })
    )
    const report = await analyzeComments(mockComments)
    expect(report.overallSentiment).toBe('positive')
    expect(report.commentCount).toBe(2)
  })

  it('strips markdown code fences before parsing', async () => {
    vi.stubEnv('VITE_ANTHROPIC_API_KEY', 'fake-key')
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        content: [{ text: `\`\`\`json\n${JSON.stringify(validReport)}\n\`\`\`` }],
      }), { status: 200 })
    )
    const report = await analyzeComments(mockComments)
    expect(report.overallSentiment).toBe('positive')
  })

  it('throws when response is not valid JSON', async () => {
    vi.stubEnv('VITE_ANTHROPIC_API_KEY', 'fake-key')
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({
        content: [{ text: 'Sorry, I cannot analyze this.' }],
      }), { status: 200 })
    )
    await expect(analyzeComments(mockComments)).rejects.toThrow('Failed to parse analysis response as JSON')
  })
})
