import { useState, useEffect } from 'react'
import { Clock, TrendingUp, TrendingDown, Minus, CloudRain, AlertTriangle } from 'lucide-react'
import { getTaskETA, getXAITask, getCurrentTask, getWhatIf } from '../api/client.js'
import ScoreRing from '../components/ScoreRing.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import AttributionFactorBar from '../components/AttributionFactorBar.jsx'
import ActionCard from '../components/ActionCard.jsx'
import WhatIfPanel from '../components/WhatIfPanel.jsx'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function TasksPage({ machineId }) {
  const [taskEta, setTaskEta] = useState(null)
  const [xai, setXai]         = useState(null)
  const [whatIf, setWhatIf]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const cur = await getCurrentTask(machineId)
      if (!cur || cur.message) {
        setTaskEta(null); setXai(null); setWhatIf(null)
        setLoading(false); return
      }
      const [eta, x, wi] = await Promise.all([
        getTaskETA(cur.task_id),
        getXAITask(cur.task_id),
        getWhatIf(machineId, cur.task_id),
      ])
      setTaskEta(eta); setXai(x); setWhatIf(wi)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Task Intelligence…" />
  if (error)   return <ErrorState message={error} onRetry={load} />
  if (!taskEta) return (
    <div className="flex flex-col items-center justify-center py-24 text-surface-100">
      <Clock size={40} className="mb-3" />
      <p className="text-sm">No active task for {machineId}</p>
    </div>
  )

  const eta = taskEta.eta || {}
  const diff = eta.difference_min ?? 0
  const diffSign = diff > 0 ? `+${diff.toFixed(1)}` : diff.toFixed(1)
  const wxRisk = taskEta.weather_risk || {}
  const scenarios = taskEta.what_if_scenarios?.scenarios || []
  const progressPct = taskEta.progress_pct ?? 0

  const chartData = scenarios.map(s => ({
    name: s.scenario,
    eta: s.predicted_eta_min,
    diff: s.change_from_current_min,
  }))

  return (
    <div className="space-y-6 max-w-5xl mx-auto">

      {/* ── Task header ────────────────────────────────────── */}
      <div className="card border-l-4 border-cat-500">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="text-xl font-bold text-white">{taskEta.task_type}</span>
              <StatusBadge status={taskEta.status} />
            </div>
            <div className="text-sm text-surface-100">
              Machine: <span className="text-gray-200">{machineId}</span> ·
              Weather: <span className="text-gray-200">{taskEta.current_weather}</span> ·
              Operator: <span className="text-gray-200">{taskEta.operator_skill}</span>
            </div>
          </div>
          {diff !== 0 && (
            <div className={`flex items-center gap-1 px-3 py-1.5 rounded-lg border text-sm font-semibold ${diff > 0 ? 'text-red-400 bg-red-900/20 border-red-700/40' : 'text-green-400 bg-green-900/10 border-green-700/30'}`}>
              {diff > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              {diffSign} min
            </div>
          )}
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-surface-100 mb-1">
            <span>Progress</span>
            <span>{progressPct}%</span>
          </div>
          <div className="h-2 bg-surface-500 rounded-full overflow-hidden">
            <div className="h-full bg-cat-500 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

        {/* ETA Cards */}
        <div className="card space-y-4">
          <div className="section-title">ETA Breakdown</div>
          <ETABlock label="Original Estimate" value={`${eta.baseline_time_min} min`} />
          <ETABlock label="ML Prediction"     value={`${eta.predicted_time_min?.toFixed(0)} min`} highlight />
          <ETABlock label="Difference"        value={`${diffSign} min`} warn={diff > 5} />
          <ETABlock label="Lower Bound"       value={`${eta.lower_bound_min?.toFixed(0)} min`} />
          <ETABlock label="Upper Bound"       value={`${eta.upper_bound_min?.toFixed(0)} min`} />
        </div>

        {/* XAI factors — Feature 1 */}
        <div className="card space-y-3">
          <div className="section-title">Why? — Model Attribution</div>
          {xai?.explanation && <p className="text-xs text-surface-100 leading-relaxed">{xai.explanation}</p>}
          <div className="space-y-2.5">
            {xai?.top_factors?.filter(f => f.impact > 0).map((f, i) => (
              <AttributionFactorBar key={i} factor={f} />
            ))}
          </div>
          {xai?.attribution_note && (
            <p className="text-xs text-surface-200 italic">{xai.attribution_note}</p>
          )}
          {/* Feature 2 — Action */}
          <ActionCard action={xai?.recommended_action} title="What Should I Do?" />
        </div>

        {/* Weather overlap */}
        <div className="card space-y-3">
          <div className="section-title">Weather Overlap</div>
          {wxRisk.task_weather_overlap ? (
            <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg p-3 text-sm text-amber-300">
              <div className="flex gap-2">
                <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                <div>{wxRisk.overlap_advisory}</div>
              </div>
            </div>
          ) : (
            <div className="text-sm text-green-400 flex items-center gap-2">
              <CloudRain size={14} /> No weather-task overlap detected.
            </div>
          )}
          <div className="space-y-2 pt-2">
            {wxRisk.forecast?.slice(0, 4).map((slot, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <span className="text-surface-100">+{slot.offset_min} min ({slot.time})</span>
                <StatusBadge status={slot.risk_level} dot={false} />
                <span className="text-gray-300">{slot.condition}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* What-if scenarios */}
      {chartData.length > 0 && (
        <div className="card">
          <div className="section-title">What-If Scenarios — ETA by Weather</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} barSize={40}>
              <XAxis dataKey="name" tick={{ fill: '#718096', fontSize: 12 }} />
              <YAxis tick={{ fill: '#718096', fontSize: 12 }} unit=" min" />
              <Tooltip contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }}
                formatter={(v, n) => [`${v.toFixed(1)} min`, n]} />
              <ReferenceLine y={eta.baseline_time_min} stroke="#FFCD11" strokeDasharray="4 4" label={{ value: 'Estimate', fill: '#FFCD11', fontSize: 11 }} />
              <Bar dataKey="eta" name="Predicted ETA"
                fill="#3b82f6" radius={[4,4,0,0]}
                label={{ position: 'top', fill: '#9ca3af', fontSize: 11, formatter: v => `${v.toFixed(0)}m` }} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      {/* Feature 6 — Advanced What-If */}
      {whatIf && <WhatIfPanel data={whatIf} />}
    </div>
  )
}

function ETABlock({ label, value, highlight, warn }) {
  return (
    <div className="flex justify-between items-center text-sm">
      <span className="text-surface-100">{label}</span>
      <span className={`font-semibold ${highlight ? 'text-cat-500' : warn ? 'text-red-400' : 'text-gray-200'}`}>{value}</span>
    </div>
  )
}
