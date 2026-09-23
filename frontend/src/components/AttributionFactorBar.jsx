/**
 * Feature 1 — Model-attributed contribution bar.
 * Replaces the old FactorBar with proper attribution terminology.
 */
import { TrendingUp, TrendingDown, Minus, Info } from 'lucide-react'
import clsx from 'clsx'

export default function AttributionFactorBar({ factor }) {
  const { feature, value, model_contribution_min, impact, direction, attribution_type, note } = factor

  const pct   = Math.min(100, Math.abs(impact || 0) * 9)
  const color = direction === 'increase' ? 'bg-red-500'
              : direction === 'decrease' ? 'bg-green-500'
              : 'bg-surface-400'
  const Icon  = direction === 'increase' ? TrendingUp
              : direction === 'decrease' ? TrendingDown
              : Minus
  const iconCls = direction === 'increase' ? 'text-red-400'
                : direction === 'decrease' ? 'text-green-400'
                : 'text-surface-200'

  const contribLabel = model_contribution_min != null
    ? `${model_contribution_min >= 0 ? '+' : ''}${model_contribution_min.toFixed(1)} min`
    : null

  return (
    <div className="flex items-start gap-2.5">
      <Icon size={12} className={clsx('mt-1 shrink-0', iconCls)} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between text-xs mb-0.5 gap-2">
          <span className="text-gray-300 truncate font-medium">{feature}</span>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-surface-100">{value}</span>
            {contribLabel && (
              <span className={clsx(
                'font-mono text-xs px-1.5 py-0.5 rounded',
                direction === 'increase' ? 'bg-red-900/30 text-red-300'
                : direction === 'decrease' ? 'bg-green-900/30 text-green-300'
                : 'bg-surface-500 text-surface-100'
              )}>
                {contribLabel}
              </span>
            )}
          </div>
        </div>
        <div className="h-1.5 bg-surface-500 rounded-full overflow-hidden">
          <div className={clsx('h-full rounded-full', color)} style={{ width: `${pct}%` }} />
        </div>
        {note && (
          <div className="text-xs text-surface-100 mt-0.5 truncate">{note}</div>
        )}
      </div>
    </div>
  )
}
