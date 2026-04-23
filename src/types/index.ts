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
