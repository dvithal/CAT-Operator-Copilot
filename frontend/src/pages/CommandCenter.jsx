import { useState, useEffect } from 'react'
import { Activity, ShieldCheck, Clock, Fuel, Timer, Brain, AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { getContext, getXAITask, getXAIBehavior, getXAIMachine, getWeatherRisk } from '../api/client.js'
import KpiCard from '../components/KpiCard.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import ScoreRing from '../components/ScoreRing.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'

function FactorBar({ label, value, impact, direction }) {
  const color = direction === 'increase' ? 'bg-red-500' : direction === 'decrease' ? 'bg-green-500' : 'bg-surface-400'
  const pct = Math.min(100, Math.abs(impact || 0) * 10)
  const Icon = direction === 'increase' ? TrendingUp : direction === 'decrease' ? TrendingDown : Minus
  return (
    <div className="flex items-center gap-3">
      <Icon size={12} className={direction === 'increase' ? 'text-red-400' : direction === 'decrease' ? 'text-green-400' : 'text-surface-200'} />
      <div className="flex-1 min-w-0">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-300 truncate">{label}</span>
          <span className="text-surface-100 ml-2">{value}</span>
        </div>
        <div className="h-1.5 bg-surface-500 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  )
}

function SectionLabel({ children }) {
  return <div className="section-title">{children}</div>
}

export default function CommandCenter({ machineId }) {
  const [ctx, setCtx]         = useState(null)
  const [etaXAI, setEtaXAI]   = useState(null)
  const [behXAI, setBehXAI]   = useState(null)
  const [mchXAI, setMchXAI]   = useState(null)
  const [wxRisk, setWxRisk]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const context = await getContext(machineId)
      setCtx(context)
      const taskId = context?.task?.task_id
      const etaMin = context?.task_prediction?.predicted_time_min

      const [beh, mch, wx] = await Promise.all([
        getXAIBehavior(machineId),
        getXAIMachine(machineId),
        getWeatherRisk(machineId, etaMin),
      ])
      setBehXAI(beh); setMchXAI(mch); setWxRisk(wx)

      if (taskId) {
        const eta = await getXAITask(taskId)
        setEtaXAI(eta)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Command Center…" />
  if (error)   return <ErrorState message={error} onRetry={load} />

  const m  = ctx?.machine   || {}
  const op = ctx?.operator  || {}
  const t  = ctx?.task      || {}
  const s  = ctx?.safety    || {}
  const eta = ctx?.task_prediction || {}
  const beh = ctx?.behavior_prediction || {}
  const w  = ctx?.weather?.current || {}

  const safetyScore = s.safety_score ?? 100
  const healthScore = mchXAI?.health_score ?? 100
  const etaDiff     = eta.difference_min ?? 0
  const etaSign     = etaDiff > 0 ? `+${etaDiff.toFixed(0)}` : etaDiff.toFixed(0)

  return (
    <div className="space-y-6 max-w-7xl mx-auto">

      {/* ── Hero strip ─────────────────────────────────────── */}
      <div className="card flex items-center justify-between gap-4 border-l-4 border-cat-500">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-bold text-white">{machineId}</span>
            <StatusBadge status={m.status} />
          </div>
          <div className="flex items-center gap-4 mt-1 text-sm text-surface-100">
            <span>Operator: <span className="text-gray-200">{op.name || '—'}</span></span>
            <span>Task: <span className="text-gray-200">{t.task_type || 'None'}</span></span>
            <span>Zone: <span className="text-gray-200">{t.zone || '—'}</span></span>
          </div>
        </div>
        <div className="flex items-center gap-4 shrink-0">
          <ScoreRing score={safetyScore} label="Safety"  size={72} />
          <ScoreRing score={healthScore} label="Health"  size={72} />
        </div>
      </div>

      {/* ── KPI row ────────────────────────────────────────── */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KpiCard label="Machine Health"  value={healthScore}              unit="/100"  icon={Activity}   status={mchXAI?.health_status} />
        <KpiCard label="Safety Score"    value={safetyScore}              unit="/100"  icon={ShieldCheck} status={s.safety_status} />
        <KpiCard label="Task ETA"        value={eta.predicted_time_min?.toFixed(0) ?? '—'} unit="min" icon={Clock} status={etaDiff > 5 ? 'CAUTION' : 'NORMAL'} sub={eta.predicted_time_min ? `${etaSign} min vs estimate` : null} />
        <KpiCard label="Fuel Level"      value={m.fuel_level_pct ?? '—'}  unit="%"     icon={Fuel}       status={m.fuel_level_pct < 20 ? 'CRITICAL' : 'NORMAL'} />
        <KpiCard label="Idle Time"       value={m.idling_time_min ?? '—'} unit="min"   icon={Timer}      status={m.idling_time_min > 40 ? 'CAUTION' : 'NORMAL'} />
        <KpiCard label="Behavior"        value={beh.anomaly ? 'ANOMALY' : 'NORMAL'}    icon={Brain}      status={beh.anomaly ? 'ANOMALY' : 'NORMAL'} />
      </div>

      {/* ── Context + Predictions ──────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Current Context */}
        <div className="card space-y-4">
          <SectionLabel>Current Context</SectionLabel>
          <Row label="Machine"     value={`${m.machine_type} — ${machineId}`} />
          <Row label="Model"       value={m.model} />
          <Row label="Operator"    value={op.name}       sub={op.skill_level} />
          <Row label="Task"        value={t.task_type || 'None'} />
          <Row label="Phase"       value={t.phase || '—'} />
          <Row label="Weather"     value={w.condition}   sub={`${w.temperature_c ?? '—'}°C · Wind ${w.wind_kph ?? '—'} kph`} />
          <Row label="Engine Hrs"  value={m.engine_hours} />
          <Row label="Seatbelt"    value={m.seatbelt_status} highlight={m.seatbelt_status === 'Unfastened'} />
        </div>

        {/* Predictions */}
        <div className="card space-y-4">
          <SectionLabel>ML Predictions</SectionLabel>

          <PredBlock
            title="Task ETA"
            value={eta.predicted_time_min ? `${eta.predicted_time_min.toFixed(0)} min` : 'N/A'}
            sub={eta.baseline_time_min ? `Estimate: ${eta.baseline_time_min} min  (${etaSign} min)` : null}
            status={etaDiff > 5 ? 'CAUTION' : 'NORMAL'}
          />
          <PredBlock
            title="Behavior Anomaly"
            value={beh.anomaly ? 'ANOMALY DETECTED' : 'NORMAL'}
            sub={beh.anomaly ? `Score: ${beh.anomaly_score}` : 'Operating within baseline'}
            status={beh.anomaly ? 'CRITICAL' : 'NORMAL'}
          />
          <PredBlock
            title="Machine Health"
            value={`${healthScore}/100`}
            sub={mchXAI?.health_status}
            status={mchXAI?.health_status}
          />
          <PredBlock
            title="Weather Risk"
            value={wxRisk?.current_risk_level ?? '—'}
            sub={wxRisk?.current_condition}
            status={wxRisk?.current_risk_level === 'HIGH' ? 'CRITICAL' : wxRisk?.current_risk_level === 'MEDIUM' ? 'CAUTION' : 'NORMAL'}
          />
        </div>

        {/* What Happens Next */}
        <div className="card space-y-4">
          <SectionLabel>What Happens Next</SectionLabel>
          {wxRisk?.task_weather_overlap && (
            <div className="bg-amber-900/20 border border-amber-700/40 rounded-lg p-3 text-sm text-amber-300">
              <div className="flex gap-2">
                <AlertTriangle size={14} className="mt-0.5 shrink-0" />
                <div>
                  <div className="font-semibold mb-1">Weather–Task Overlap</div>
                  <div className="text-xs">{wxRisk.overlap_advisory}</div>
                </div>
              </div>
            </div>
          )}
          {wxRisk?.worst_upcoming_condition && (
            <div className="text-sm space-y-1">
              <div className="text-surface-100 text-xs">Worst upcoming condition</div>
              <div className="font-medium text-gray-200">
                {wxRisk.worst_upcoming_condition.condition} @ {wxRisk.worst_upcoming_condition.time}
              </div>
            </div>
          )}
          {beh.anomaly && (
            <div className="bg-red-900/20 border border-red-700/40 rounded-lg p-3 text-sm text-red-300">
              <div className="font-semibold mb-1">Behavioral Anomaly Active</div>
              <div className="text-xs">Review operator activity and machine telemetry.</div>
            </div>
          )}
          {s.recommendations?.slice(0, 2).map((r, i) => (
            <div key={i} className="bg-surface-600 rounded-lg p-3 text-xs text-gray-300">
              {r}
            </div>
          ))}
          {!wxRisk?.task_weather_overlap && !beh.anomaly && !s.recommendations?.length && (
            <div className="text-sm text-surface-100">No immediate risks detected.</div>
          )}
        </div>
      </div>

      {/* ── XAI Explanation Cards ──────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">

        {/* ETA XAI */}
        {etaXAI && !etaXAI.error && (
          <div className="card space-y-3">
            <SectionLabel>Why is ETA {etaDiff >= 0 ? 'longer' : 'shorter'}?</SectionLabel>
            <p className="text-xs text-surface-100 leading-relaxed">{etaXAI.explanation}</p>
            <div className="space-y-2">
              {etaXAI.top_factors?.filter(f => f.impact > 0).slice(0, 4).map((f, i) => (
                <FactorBar key={i} label={f.feature} value={f.value} impact={f.impact} direction={f.direction} />
              ))}
            </div>
          </div>
        )}

        {/* Behavior XAI */}
        {behXAI && !behXAI.error && (
          <div className="card space-y-3">
            <SectionLabel>Behavior Analysis</SectionLabel>
            <p className="text-xs text-surface-100 leading-relaxed">{behXAI.explanation}</p>
            <div className="space-y-2">
              {behXAI.top_factors?.slice(0, 4).map((f, i) => (
                <FactorBar key={i} label={f.feature} value={`${f.current_value} vs ${f.baseline_median}`} impact={f.impact} direction={f.direction} />
              ))}
            </div>
          </div>
        )}

        {/* Health XAI */}
        {mchXAI && !mchXAI.error && (
          <div className="card space-y-3">
            <SectionLabel>Machine Health Factors</SectionLabel>
            <p className="text-xs text-surface-100 leading-relaxed">{mchXAI.explanation}</p>
            <div className="space-y-2">
              {mchXAI.top_factors?.slice(0, 4).map((f, i) => (
                <FactorBar key={i} label={f.feature} value={f.value} impact={f.impact} direction={f.direction} />
              ))}
            </div>
            <div className="text-xs text-surface-200 italic">{mchXAI.note}</div>
          </div>
        )}
      </div>
    </div>
  )
}

function Row({ label, value, sub, highlight }) {
  return (
    <div className="flex items-start justify-between gap-2 text-sm">
      <span className="text-surface-100 shrink-0">{label}</span>
      <div className="text-right min-w-0">
        <div className={highlight ? 'text-red-400 font-semibold' : 'text-gray-200'}>{value ?? '—'}</div>
        {sub && <div className="text-xs text-surface-100">{sub}</div>}
      </div>
    </div>
  )
}

function PredBlock({ title, value, sub, status }) {
  const color = {
    NORMAL: 'border-green-700/40 bg-green-900/10',
    CAUTION: 'border-amber-700/40 bg-amber-900/10',
    CRITICAL: 'border-red-700/40 bg-red-900/10',
    ANOMALY: 'border-red-700/40 bg-red-900/10',
    HIGH: 'border-red-700/40 bg-red-900/10',
    GOOD: 'border-green-700/40 bg-green-900/10',
    ATTENTION: 'border-amber-700/40 bg-amber-900/10',
    MEDIUM: 'border-amber-700/40 bg-amber-900/10',
  }[status?.toUpperCase()] || 'border-surface-500 bg-surface-600'

  return (
    <div className={`border rounded-lg p-3 space-y-1 ${color}`}>
      <div className="text-xs text-surface-100 uppercase tracking-wider">{title}</div>
      <div className="font-semibold text-white">{value}</div>
      {sub && <div className="text-xs text-surface-100">{sub}</div>}
    </div>
  )
}
