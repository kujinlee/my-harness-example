import type { AnalysisReport } from '../types'

interface Props {
  report: AnalysisReport
}

function sentimentPillClass(sentiment: string) {
  const s = sentiment.toLowerCase()
  if (s === 'positive') return 'bg-[#22c55e]/10 text-[#22c55e] border border-[#22c55e]/20'
  if (s === 'negative') return 'bg-[#ef4444]/10 text-[#ef4444] border border-[#ef4444]/20'
  return 'bg-neutral-800 text-neutral-300 border border-neutral-700'
}

function sentimentLabel(sentiment: string) {
  const s = sentiment.toLowerCase()
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export default function ReportDisplay({ report }: Props) {
  const { overallSentiment, sentimentBreakdown, strengths, improvements, commentCount } = report

  return (
    <div className="space-y-8">
      <div>
        <p className="text-xs font-medium text-neutral-400 uppercase tracking-wide mb-3">Overall Sentiment</p>
        <span className={`inline-block px-3 py-1 rounded-md text-sm font-medium ${sentimentPillClass(overallSentiment)}`}>
          {sentimentLabel(overallSentiment)}
        </span>
      </div>

      <div>
        <p className="text-xs font-medium text-neutral-400 uppercase tracking-wide mb-3">Sentiment Breakdown</p>
        <div className="space-y-2">
          {[
            { label: 'Positive', pct: sentimentBreakdown.positive, color: '#22c55e' },
            { label: 'Neutral', pct: sentimentBreakdown.neutral, color: '#525252' },
            { label: 'Negative', pct: sentimentBreakdown.negative, color: '#ef4444' },
          ].map(({ label, pct, color }) => (
            <div key={label} className="flex items-center gap-3">
              <span className="text-xs text-neutral-400 w-16">{label}</span>
              <div className="flex-1 bg-neutral-800 h-2 rounded-sm overflow-hidden">
                <div
                  className="h-2 rounded-sm"
                  style={{ width: `${pct}%`, backgroundColor: color }}
                />
              </div>
              <span className="text-xs text-neutral-400 w-8 text-right">{pct}%</span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="text-base font-medium text-white mb-3">What's Working</p>
        <div className="space-y-3">
          {strengths.map((item, i) => (
            <div key={i} className="rounded-md bg-[#141414] border border-neutral-800 p-4">
              <p className="text-sm font-medium text-white">{item.theme}</p>
              <p className="text-sm text-neutral-300 mt-1">{item.description}</p>
              <p className="text-xs text-neutral-500 italic mt-2">"{item.exampleComment}"</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="text-base font-medium text-white mb-3">Areas to Improve</p>
        <div className="space-y-3">
          {improvements.map((item, i) => (
            <div key={i} className="rounded-md bg-[#141414] border border-neutral-800 p-4">
              <p className="text-sm font-medium text-white">{item.theme}</p>
              <p className="text-sm text-neutral-300 mt-1">{item.description}</p>
              <p className="text-xs text-neutral-500 italic mt-2">"{item.exampleComment}"</p>
            </div>
          ))}
        </div>
      </div>

      <p className="text-xs text-neutral-500 mt-6">Based on {commentCount} comments</p>
    </div>
  )
}
