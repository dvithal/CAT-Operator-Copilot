import { AlertTriangle, RefreshCw } from 'lucide-react'

export default function ErrorState({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4 text-surface-100">
      <AlertTriangle size={32} className="text-amber-400" />
      <p className="text-sm text-center max-w-xs">{message || 'Failed to load data.'}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary text-xs">
          <RefreshCw size={14} /> Retry
        </button>
      )}
    </div>
  )
}
