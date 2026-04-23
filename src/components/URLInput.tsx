import type { Status } from '../App'

interface Props {
  value: string
  onChange: (v: string) => void
  onSubmit: () => void
  disabled: boolean
  status: Status
}

export default function URLInput({ value, onChange, onSubmit, disabled, status }: Props) {
  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' && !disabled) {
      onSubmit()
    }
  }

  const buttonLabel =
    status === 'fetching' ? 'Fetching comments…' :
    status === 'analyzing' ? 'Analyzing…' :
    'Analyze'

  const showStatusLine = status === 'fetching' || status === 'analyzing'
  const statusLineText =
    status === 'fetching' ? 'Fetching top 100 comments…' :
    'Analyzing with Claude…'

  return (
    <div>
      <div className="flex gap-3">
        <input
          type="text"
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="https://www.youtube.com/watch?v=..."
          className="flex-1 rounded-md bg-neutral-900 border border-neutral-800 px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-neutral-600"
        />
        <button
          onClick={onSubmit}
          disabled={disabled}
          className={disabled
            ? 'rounded-md bg-neutral-800 text-neutral-500 cursor-not-allowed font-medium px-4 py-2 whitespace-nowrap'
            : 'rounded-md bg-white text-black font-medium px-4 py-2 hover:bg-neutral-200 whitespace-nowrap'
          }
        >
          {buttonLabel}
        </button>
      </div>
      {showStatusLine && (
        <p className="text-neutral-400 text-sm mt-2">{statusLineText}</p>
      )}
    </div>
  )
}
