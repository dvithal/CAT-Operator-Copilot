/**
 * Feature 9 — Safety counterfactual card.
 * Shows what the deterministic safety engine would produce with changed inputs.
 */
import { FlaskConical } from 'lucide-react'
import clsx from 'clsx'

const scoreColor = s => s >= 85 ? 'text-green-400' : s >= 70 ? 'text-amber-400' : s >= 50 ? 'text-orange-400' : 'text-red-400'
const decisionColor = d => {
  if (d === 'NORMAL') return 'text-green-400'
  if (d?.includes('CAUTION')) return 'text-amber-400'
  if (d?.includes('CHECK')) return 'text-orange-400'
  return 'text-red-400'
}

export default function CounterfactualCard({ data }) {
  if (!data || !data.actual) return null

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <FlaskConical size={14} className="text-blue-400" />
        <span className="section-title mb-0">Safety What-If Scenarios</span>
      </div>

      {/* Actual */}
      <div className="bg-surface-600 border border-surface-500 rounded-lg p-3">
        <div className="text-xs text-surface-100 uppercase tracking-wider mb-2">Current State</div>
        <div className="flex items-center justify-between">
          <span className={clsx('text-xl font-bold', scoreColor(data.actual.safety_score))}>
            {data.actual.safety_score}/100
          </span>
          <span className={clsx('text-sm font-semibold', decisionColor(data.actual.decision))}>
            {data.actual.decision}
          </span>
        </div>
      </div>

      {/* Counterfactuals */}
      <div className="space-y-2">
        {data.counterfactuals?.map((cf, i) => (
          <div key={i} className="border border-surface-500 rounded-lg p-3 space-y-1">
            <div className="text-xs text-blue-400 font-semibold">{cf.label}</div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={clsx('text-lg font-bold', scoreColor(cf.safety_score))}>
                  {cf.safety_score}/100
                </span>
                <span className={clsx('text-xs font-semibold', decisionColor(cf.decision))}>
                  {cf.decision}
                </span>
              </div>
              <span className={clsx(
                'text-sm font-bold',
                cf.score_delta > 0 ? 'text-green-400' : cf.score_delta < 0 ? 'text-red-400' : 'text-surface-100'
              )}>
                {cf.score_delta > 0 ? '+' : ''}{cf.score_delta} pts
              </span>
            </div>
          </div>
        ))}
      </div>

      <p className="text-xs text-surface-100 italic">{data.disclaimer}</p>
    </div>
  )
}
