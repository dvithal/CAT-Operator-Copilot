/**
 * Feature 3 — Closed-loop operator feedback buttons.
 * ACKNOWLEDGE / NOT_RELEVANT / SOMETHING_ELSE
 */
import { useState } from 'react'
import { CheckCircle, XCircle, MessageSquare, RefreshCw, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { submitFeedback, getFeedbackComparison } from '../api/client.js'
import clsx from 'clsx'

const CHOICES = [
  { id: 'ACKNOWLEDGE',   label: 'Acknowledge',   Icon: CheckCircle, cls: 'border-green-700/50 text-green-400 hover:bg-green-900/20' },
  { id: 'NOT_RELEVANT',  label: 'Not Relevant',  Icon: XCircle,     cls: 'border-amber-700/50 text-amber-400 hover:bg-amber-900/20' },
  { id: 'SOMETHING_ELSE',label: 'Something Else',Icon: MessageSquare,cls:'border-blue-700/50 text-blue-400 hover:bg-blue-900/20' },
]

const TREND_ICON = { IMPROVED: TrendingUp, WORSENED: TrendingDown, UNCHANGED: Minus }
const TREND_CLS  = { IMPROVED: 'text-green-400', WORSENED: 'text-red-400', UNCHANGED: 'text-surface-100' }

export default function FeedbackButtons({ machineId, operatorId = 'OP-07', eventType = 'anomaly', eventId }) {
  const [selected, setSelected]     = useState(null)
  const [note, setNote]             = useState('')
  const [submitted, setSubmitted]   = useState(false)
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading]       = useState(false)

  const submit = async (choice) => {
    setLoading(true)
    try {
      await submitFeedback(machineId, {
        operator_id: operatorId,
        event_type:  eventType,
        event_id:    eventId || `${machineId}-${Date.now()}`,
        choice,
        note,
      })
      setSelected(choice)
      setSubmitted(true)

      // Fetch before/after comparison
      const cmp = await getFeedbackComparison(machineId)
      if (cmp && cmp.trend) setComparison(cmp)
    } catch {}
    finally { setLoading(false) }
  }

  if (submitted) {
    const TrendIcon = TREND_ICON[comparison?.trend] || Minus
    const trendCls  = TREND_CLS[comparison?.trend] || 'text-surface-100'
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2 text-xs text-green-400">
          <CheckCircle size={12} /> Feedback recorded: {selected?.replace('_', ' ')}
        </div>
        {comparison && (
          <div className="border border-surface-500 rounded-lg p-3 text-xs space-y-2">
            <div className="text-surface-100 uppercase tracking-wider text-xs">Before / After Observation</div>
            <div className="flex items-center gap-3">
              <span className="text-gray-300">Before: <strong>{comparison.before?.severity}</strong> ({comparison.before?.anomaly_score})</span>
              <TrendIcon size={14} className={trendCls} />
              <span className="text-gray-300">After: <strong>{comparison.after?.severity}</strong> ({comparison.after?.anomaly_score})</span>
            </div>
            <div className={clsx('font-medium', trendCls)}>{comparison.summary}</div>
            <p className="text-surface-200 italic">{comparison.disclaimer}</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2 flex-wrap">
        {CHOICES.map(({ id, label, Icon, cls }) => (
          <button
            key={id}
            onClick={() => submit(id)}
            disabled={loading}
            className={clsx('flex items-center gap-1.5 px-3 py-1.5 border rounded-lg text-xs font-medium transition-colors disabled:opacity-40', cls)}
          >
            <Icon size={12} /> {label}
          </button>
        ))}
      </div>
      <input
        className="input text-xs py-1.5"
        placeholder="Optional note (e.g. 'Idle caused by material wait')"
        value={note}
        onChange={e => setNote(e.target.value)}
      />
    </div>
  )
}
