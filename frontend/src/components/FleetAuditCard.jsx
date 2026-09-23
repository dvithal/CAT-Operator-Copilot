/**
 * Feature 8 — Fleet attribution audit card.
 * Shows observed statistics only. Never claims fairness certification.
 */
import { BarChart2, AlertTriangle } from 'lucide-react'

export default function FleetAuditCard({ data }) {
  if (!data) return null
  const dist = data.attribution_distribution || {}

  return (
    <div className="card space-y-4">
      <div className="flex items-center gap-2">
        <BarChart2 size={14} className="text-purple-400" />
        <span className="section-title mb-0">Fleet Attribution Audit</span>
      </div>

      <div className="text-xs text-surface-100">{data.period}</div>

      <div className="grid grid-cols-3 gap-3">
        <AuditStat label="Operator flagged"    value={dist.operator_flagged_count}   color="text-amber-400" />
        <AuditStat label="Context explained"   value={dist.context_explained_count}  color="text-blue-400" />
        <AuditStat label="Machine context"     value={dist.machine_context_count}    color="text-purple-400" />
      </div>

      {dist.note && <p className="text-xs text-surface-100 italic">{dist.note}</p>}

      {/* Per-operator breakdown */}
      {data.by_operator?.length > 0 && (
        <div>
          <div className="text-xs text-surface-100 uppercase tracking-wider mb-2">By Operator</div>
          <div className="space-y-1.5">
            {data.by_operator.filter(op => op.operator_id !== 'UNKNOWN').map((op, i) => (
              <div key={i} className="flex items-center justify-between text-xs bg-surface-600 rounded px-3 py-1.5">
                <span className="font-mono text-gray-300">{op.operator_id}</span>
                <div className="flex gap-3">
                  <span className="text-amber-400">{op.anomaly_count} anomalies</span>
                  <span className="text-red-400">{op.safety_count} safety</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-amber-900/10 border border-amber-700/30 rounded-lg px-3 py-2 text-xs text-amber-300 flex gap-2">
        <AlertTriangle size={11} className="mt-0.5 shrink-0" />
        <span>{data.disclaimer}</span>
      </div>

      <p className="text-xs text-surface-200 italic">{data.statistical_note}</p>
    </div>
  )
}

function AuditStat({ label, value, color }) {
  return (
    <div className="card-sm text-center">
      <div className={`text-2xl font-bold ${color}`}>{value ?? 0}</div>
      <div className="text-xs text-surface-100 mt-0.5">{label}</div>
    </div>
  )
}
