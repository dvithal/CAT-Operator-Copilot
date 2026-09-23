import { useState, useEffect } from 'react'
import { FileText, Download, RefreshCw, TrendingUp } from 'lucide-react'
import { getShiftHandover, getDailyReport } from '../api/client.js'
import ScoreRing from '../components/ScoreRing.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function ReportsPage({ machineId }) {
  const [tab, setTab]             = useState('daily')
  const [handover, setHandover]   = useState(null)
  const [daily, setDaily]         = useState(null)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const [h, d] = await Promise.all([getShiftHandover(machineId), getDailyReport(machineId)])
      setHandover(h); setDaily(d)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [machineId])

  const exportText = (text, filename) => {
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = filename; a.click()
    URL.revokeObjectURL(url)
  }

  if (loading) return <LoadingSpinner label="Generating Reports…" />
  if (error)   return <ErrorState message={error} onRetry={load} />

  const d = daily || {}
  const h = handover || {}
  const summary = d.summary || {}
  const history = d.history || []

  return (
    <div className="space-y-6 max-w-6xl mx-auto">

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: 'daily',    label: 'Daily Report' },
          { id: 'handover', label: 'Shift Handover' },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === t.id ? 'bg-cat-500 text-surface-900' : 'bg-surface-600 text-gray-300 hover:bg-surface-500'}`}>
            {t.label}
          </button>
        ))}
        <div className="ml-auto flex gap-2">
          <button onClick={load} className="btn-secondary">
            <RefreshCw size={13} /> Regenerate
          </button>
          {tab === 'handover' && h.handover_text && (
            <button onClick={() => exportText(h.handover_text, `shift-handover-${machineId}.txt`)} className="btn-secondary">
              <Download size={13} /> Export
            </button>
          )}
        </div>
      </div>

      {/* ── DAILY REPORT ───────────────────────────────────── */}
      {tab === 'daily' && (
        <div className="space-y-5">
          <div className="card border-l-4 border-cat-500">
            <div className="flex items-start justify-between">
              <div>
                <div className="text-lg font-bold text-white">Daily Operations Report</div>
                <div className="text-sm text-surface-100">{machineId} · {d.machine_model} · Last 7 days</div>
                <div className="text-xs text-surface-200 mt-0.5">{d.generated_at ? new Date(d.generated_at).toLocaleString() : ''}</div>
              </div>
              <div className="flex gap-3">
                <ScoreRing score={d.safety?.score ?? 100} label="Safety" size={64} />
                <ScoreRing score={d.machine_health?.score ?? 100} label="Health" size={64} />
              </div>
            </div>
          </div>

          {/* KPI summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Stat label="Engine Hours"    value={summary.total_engine_hours}       unit="hrs" />
            <Stat label="Fuel Used"       value={summary.total_fuel_used_l}        unit="L" />
            <Stat label="Load Cycles"     value={summary.total_load_cycles} />
            <Stat label="Idle %"          value={summary.idle_pct}                 unit="%" warn={summary.idle_pct > 20} />
            <Stat label="Tasks Completed" value={summary.tasks_completed} />
            <Stat label="Fuel/Cycle"      value={summary.fuel_per_load_cycle}      unit="L" />
            <Stat label="Safety Events"   value={d.safety?.events_count}           warn={d.safety?.events_count > 0} />
            <Stat label="Anomaly Days"    value={d.behavior?.anomaly_days}         warn={d.behavior?.anomaly_days > 0} />
          </div>

          {/* Charts */}
          {history.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="card">
                <div className="section-title">Engine Hours / Day</div>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#232b3a" />
                    <XAxis dataKey="date" tick={{ fill: '#718096', fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                    <YAxis tick={{ fill: '#718096', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }} />
                    <Bar dataKey="engine_hours" name="Engine Hrs" fill="#FFCD11" radius={[2,2,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="card">
                <div className="section-title">Fuel Used / Day (L)</div>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={history}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#232b3a" />
                    <XAxis dataKey="date" tick={{ fill: '#718096', fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                    <YAxis tick={{ fill: '#718096', fontSize: 10 }} />
                    <Tooltip contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }} />
                    <Bar dataKey="fuel_used_l" name="Fuel (L)" fill="#3b82f6" radius={[2,2,0,0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Incidents */}
          {d.incidents?.length > 0 && (
            <div className="card">
              <div className="section-title">Incidents</div>
              {d.incidents.map((inc, i) => (
                <div key={i} className="flex items-center justify-between text-sm py-2 border-b border-surface-500 last:border-0">
                  <span className="font-mono text-xs text-surface-100">{inc.incident_id}</span>
                  <span className="text-gray-300 flex-1 mx-3">{inc.description}</span>
                  <StatusBadge status={inc.severity} dot={false} />
                </div>
              ))}
            </div>
          )}

          <p className="text-xs text-surface-200 italic">{d.note}</p>
        </div>
      )}

      {/* ── SHIFT HANDOVER ─────────────────────────────────── */}
      {tab === 'handover' && (
        <div className="space-y-5">
          <div className="card border-l-4 border-blue-500">
            <div className="text-lg font-bold text-white">Shift Handover</div>
            <div className="text-sm text-surface-100">{machineId} · {h.machine_model}</div>
          </div>

          {/* Summary grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Stat label="Safety Score"    value={h.safety_score}   unit="/100" warn={h.safety_score < 70} />
            <Stat label="Health"          value={h.machine_condition} />
            <Stat label="Safety Events"   value={h.safety_events_count} warn={h.safety_events_count > 0} />
            <Stat label="Incidents"       value={h.incidents_count} warn={h.incidents_count > 0} />
          </div>

          {/* Training recs */}
          {h.training_recommendations?.length > 0 && (
            <div className="card">
              <div className="section-title">Training Recommendations for Next Operator</div>
              {h.training_recommendations.slice(0, 3).map((r, i) => (
                <div key={i} className="flex items-start gap-2 text-sm py-1.5">
                  <span className="text-cat-500 font-bold shrink-0">{i+1}.</span>
                  <div>
                    <div className="font-medium text-white">{r.module}</div>
                    <div className="text-xs text-surface-100">{r.reason}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Full text */}
          {h.handover_text && (
            <div className="card">
              <div className="section-title">Full Handover Document</div>
              <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap leading-relaxed bg-surface-800 rounded-lg p-4">
                {h.handover_text}
              </pre>
            </div>
          )}

          <p className="text-xs text-surface-200 italic">{h.note}</p>
        </div>
      )}
    </div>
  )
}

function Stat({ label, value, unit, warn }) {
  return (
    <div className="card-sm text-center">
      <div className="text-xs text-surface-100 mb-1">{label}</div>
      <div className={`text-xl font-bold ${warn ? 'text-red-400' : 'text-gray-200'}`}>
        {value ?? '—'}{unit && <span className="text-sm text-surface-100 ml-1">{unit}</span>}
      </div>
    </div>
  )
}
