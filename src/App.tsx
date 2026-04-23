import { useState } from 'react'
import type { AnalysisReport } from './types'
import { parseVideoId, fetchComments } from './services/youtube'
import { analyzeComments } from './services/analysis'
import URLInput from './components/URLInput'
import ReportDisplay from './components/ReportDisplay'

export type Status = 'idle' | 'fetching' | 'analyzing' | 'done' | 'error'

export default function App() {
  const [url, setUrl] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [report, setReport] = useState<AnalysisReport | null>(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [urlError, setUrlError] = useState('')

  async function handleSubmit() {
    setUrlError('')
    const videoId = parseVideoId(url)
    if (!videoId) {
      setUrlError('Invalid YouTube URL')
      return
    }

    try {
      setStatus('fetching')
      const comments = await fetchComments(videoId)
      setStatus('analyzing')
      const result = await analyzeComments(comments)
      setStatus('done')
      setReport(result)
    } catch (err) {
      setStatus('error')
      setErrorMessage(err instanceof Error ? err.message : 'An unexpected error occurred')
    }
  }

  const disabled = status === 'fetching' || status === 'analyzing'

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white px-6 py-12">
      <div className="max-w-3xl">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-white">YouTube Comment Analyzer</h1>
          <p className="text-sm text-neutral-400 mt-1">Paste a video URL to get audience feedback</p>
        </header>

        <URLInput
          value={url}
          onChange={setUrl}
          onSubmit={handleSubmit}
          disabled={disabled}
          status={status}
        />

        {urlError && (
          <p className="text-[#ef4444] text-sm mt-3">{urlError}</p>
        )}

        {status === 'error' && (
          <p className="text-[#ef4444] text-sm mt-3">{errorMessage}</p>
        )}

        {status === 'done' && report && (
          <div className="mt-8 animate-fade-in">
            <ReportDisplay report={report} />
          </div>
        )}
      </div>
    </div>
  )
}
