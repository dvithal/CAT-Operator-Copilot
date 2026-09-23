import { useState, useEffect } from 'react'
import { BookOpen, CheckCircle, AlertTriangle, ChevronRight } from 'lucide-react'
import { getTraining } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'

const PRIORITY_MAP = { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }
const PRIORITY_COLOR = {
  CRITICAL: 'border-red-700/40 bg-red-900/10 text-red-400',
  HIGH:     'border-amber-700/40 bg-amber-900/10 text-amber-400',
  MEDIUM:   'border-surface-400 bg-surface-600 text-gray-300',
  LOW:      'border-surface-500 bg-surface-700 text-surface-100',
}

// Operator for current machine
const MACHINE_OPERATOR = {
  EXC001: 'OP-07', EXC002: 'OP-03', EXC003: null, LD003: 'OP-11', DZ004: 'OP-05',
}

export default function TrainingPage({ machineId }) {
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  const operatorId = MACHINE_OPERATOR[machineId]

  const load = async () => {
    setLoading(true); setError(null)
    try {
      if (!operatorId) { setData(null); setLoading(false); return }
      setData(await getTraining(operatorId))
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Training Recommendations…" />
  if (error)   return <ErrorState message={error} onRetry={load} />
  if (!operatorId || !data) return (
    <div className="flex flex-col items-center justify-center py-24 text-surface-100">
      <BookOpen size={40} className="mb-3" />
      <p className="text-sm">No operator assigned to {machineId}</p>
    </div>
  )

  const recs = data.recommendations || []

  return (
    <div className="space-y-6 max-w-4xl mx-auto">

      {/* Operator card */}
      <div className="card border-l-4 border-cat-500">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-lg font-bold text-white">{data.operator_name}</div>
            <div className="flex items-center gap-3 mt-1 text-sm text-surface-100">
              <span>ID: <span className="font-mono text-gray-200">{data.operator_id}</span></span>
              <span>Skill: <span className="text-gray-200">{data.skill_level}</span></span>
              <span>Last training: <span className="text-gray-200">{data.last_training_date}</span></span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-cat-500">{recs.length}</div>
            <div className="text-xs text-surface-100">Recommendations</div>
          </div>
        </div>
      </div>

      {/* Completed modules */}
      {data.completed_modules?.length > 0 && (
        <div className="card">
          <div className="section-title">Completed Training</div>
          <div className="flex flex-wrap gap-2">
            {data.completed_modules.map((m, i) => (
              <span key={i} className="flex items-center gap-1.5 px-3 py-1.5 bg-green-900/20 border border-green-700/30 rounded-full text-sm text-green-400">
                <CheckCircle size={12} /> {m}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="space-y-3">
        <div className="section-title">Training Recommendations</div>
        {recs.length === 0 ? (
          <div className="card text-sm text-surface-100 text-center py-8">
            No training recommendations at this time. Operator performance is within acceptable range.
          </div>
        ) : (
          recs.map((r, i) => (
            <div key={i} className={`card border ${PRIORITY_COLOR[r.priority]} space-y-2`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-bold px-2 py-0.5 rounded ${PRIORITY_COLOR[r.priority]}`}>
                    {r.priority}
                  </span>
                  <span className="font-semibold text-white">{r.module}</span>
                  {r.already_completed && (
                    <span className="text-xs text-green-400 flex items-center gap-1">
                      <CheckCircle size={12} /> Refresher
                    </span>
                  )}
                </div>
                <ChevronRight size={16} className="text-surface-200" />
              </div>
              <div className="flex items-start gap-2 text-sm text-gray-300">
                <AlertTriangle size={13} className="mt-0.5 text-amber-400 shrink-0" />
                <span>{r.reason}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
