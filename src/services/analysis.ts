import type { Comment, AnalysisReport } from '../types'

export async function analyzeComments(comments: Comment[]): Promise<AnalysisReport> {
  const apiKey = import.meta.env.VITE_ANTHROPIC_API_KEY
  if (!apiKey) {
    throw new Error('Anthropic API key is not configured')
  }

  const userMessage = `Analyze these ${comments.length} YouTube comments and return a JSON object with this exact structure:

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
${comments.map(c => `[${c.likeCount} likes] ${c.text}`).join('\n')}`

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'claude-haiku-4-5-20251001',
      max_tokens: 1024,
      system: 'You are an expert content analyst. Analyze YouTube comments and return a structured JSON report. Return only valid JSON with no explanation or markdown formatting.',
      messages: [{ role: 'user', content: userMessage }],
    }),
  })

  if (!res.ok) {
    let message = `Anthropic API error: ${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      const apiMessage = body?.error?.message
      if (apiMessage) message = `Anthropic API error: ${apiMessage}`
    } catch {
      // ignore parse failure, use status message
    }
    throw new Error(message)
  }

  const data = await res.json()

  let report: AnalysisReport
  try {
    report = JSON.parse(data.content[0].text) as AnalysisReport
  } catch {
    throw new Error('Failed to parse analysis response as JSON')
  }

  return report
}
