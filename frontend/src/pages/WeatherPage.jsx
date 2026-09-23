import { useState, useEffect } from 'react'
import { CloudRain, Wind, Thermometer, Eye, AlertTriangle } from 'lucide-react'
import { getWeather, getWeatherRisk, getCurrentTask, getTaskETA } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'

const WEATHER_ICONS = {
  Sunny:  '☀️', Cloudy: '☁️', Rainy: '🌧️', Windy: '💨', Stormy: '⛈️',
}
const RISK_BG = {
  NORMAL: 'border-green-700/40 bg-green-900/10',
  LOW:    'border-amber-700/30 bg-amber-900/10',
  MEDIUM: 'border-amber-700/40 bg-amber-900/20',
  HIGH:   'border-red-700/40 bg-red-900/20',
}

export default function WeatherPage({ machineId }) {
  const [wx, setWx]       = useState(null)
  const [risk, setRisk]   = useState(null)
  const [etaMin, setEtaMin] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      // Get current task ETA to overlay on the timeline
      let taskEtaMin = null
      try {
        const cur = await getCurrentTask(machineId)
        if (cur?.task_id) {
          const eta = await getTaskETA(cur.task_id)
          taskEtaMin = eta?.eta?.predicted_time_min ?? null
        }
      } catch {}
      setEtaMin(taskEtaMin)

      const [weather, wxRisk] = await Promise.all([
        getWeather(machineId),
        getWeatherRisk(machineId, taskEtaMin),
      ])
      setWx(weather); setRisk(wxRisk)
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Weather Intelligence…" />
  if (error)   return <ErrorState message={error} onRetry={load} />

  const cur = wx?.current || {}
  const forecast = wx?.forecast || []
  const chartData = [
    { time: 'Now', risk: risk?.current_risk_score ?? 0, condition: cur.condition },
    ...forecast.map(f => ({ time: f.time, risk: f.risk_score, condition: f.condition, offset: f.offset_min })),
  ]

  return (
    <div className="space-y-6 max-w-5xl mx-auto">

      {/* ── Current weather hero ────────────────────────────── */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-4xl mb-2">{WEATHER_ICONS[cur.condition] || '🌤️'}</div>
            <div className="text-2xl font-bold text-white">{cur.condition}</div>
            <div className="text-sm text-surface-100 mt-1">{machineId} · {cur.observed_at ? new Date(cur.observed_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : '—'}</div>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <WeatherStat icon={Thermometer} label="Temperature" value={`${cur.temperature_c ?? '—'}°C`} />
            <WeatherStat icon={Wind}        label="Wind Speed"  value={`${cur.wind_kph ?? '—'} kph`} />
            <WeatherStat icon={Eye}         label="Visibility"  value={`${(cur.visibility_m / 1000)?.toFixed(1) ?? '—'} km`} />
            <WeatherStat icon={CloudRain}   label="Humidity"    value={`${cur.humidity_pct ?? '—'}%`} />
          </div>
          <div className="text-right">
            <StatusBadge status={cur.risk_level || 'NORMAL'} />
            <p className="text-xs text-surface-100 mt-2 max-w-xs">{cur.operational_impact}</p>
          </div>
        </div>
      </div>

      {/* ── Weather-Task overlap alert ─────────────────────── */}
      {risk?.task_weather_overlap && (
        <div className="card bg-amber-900/15 border-amber-700/50">
          <div className="flex gap-3">
            <AlertTriangle size={20} className="text-amber-400 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold text-amber-400 mb-1">Weather / Task Overlap Detected</div>
              <p className="text-sm text-amber-300">{risk.overlap_advisory}</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Risk timeline chart ─────────────────────────────── */}
      <div className="card">
        <div className="section-title">Risk Timeline (Next 90 min)</div>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#232b3a" />
            <XAxis dataKey="time" tick={{ fill: '#718096', fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: '#718096', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }}
              formatter={(v, n, p) => [`${v} (${p.payload.condition})`, 'Risk Score']}
            />
            {etaMin && (
              <ReferenceLine
                x={chartData.find(d => d.offset >= etaMin)?.time || ''}
                stroke="#FFCD11" strokeDasharray="4 4"
                label={{ value: 'Task ETA', fill: '#FFCD11', fontSize: 11 }}
              />
            )}
            <Line type="monotone" dataKey="risk" stroke="#ef4444" strokeWidth={2} dot={{ fill: '#ef4444', r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
        {etaMin && (
          <div className="mt-2 text-xs text-surface-100">
            <span className="text-cat-500">━━</span> Task predicted to complete in ~{etaMin?.toFixed(0)} min
          </div>
        )}
      </div>

      {/* ── Forecast slots ─────────────────────────────────── */}
      <div className="card">
        <div className="section-title">Forecast Timeline</div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {forecast.map((slot, i) => (
            <div key={i} className={`rounded-lg p-3 border text-center space-y-1 ${RISK_BG[slot.risk_level] || RISK_BG.NORMAL}`}>
              <div className="text-xs text-surface-100">+{slot.offset_min} min</div>
              <div className="text-lg">{WEATHER_ICONS[slot.condition] || '🌤️'}</div>
              <div className="text-xs font-medium text-gray-200">{slot.condition}</div>
              <div className="text-xs text-surface-100">{slot.time}</div>
              <StatusBadge status={slot.risk_level} dot={false} className="text-xs" />
            </div>
          ))}
        </div>
      </div>

      {/* ── Worst upcoming ─────────────────────────────────── */}
      {risk?.worst_upcoming_condition && (
        <div className="card">
          <div className="section-title">Worst Upcoming Condition</div>
          <div className="flex items-center gap-4">
            <div className="text-3xl">{WEATHER_ICONS[risk.worst_upcoming_condition.condition] || '⛅'}</div>
            <div>
              <div className="text-lg font-semibold text-white">{risk.worst_upcoming_condition.condition}</div>
              <div className="text-sm text-surface-100">Expected around {risk.worst_upcoming_condition.time} (+{risk.worst_upcoming_condition.offset_min} min)</div>
              <StatusBadge status={risk.worst_upcoming_condition.risk_level} className="mt-1" />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function WeatherStat({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-2 bg-surface-600 rounded-lg px-3 py-2">
      <Icon size={14} className="text-surface-200 shrink-0" />
      <div>
        <div className="text-xs text-surface-100">{label}</div>
        <div className="font-medium text-gray-200">{value}</div>
      </div>
    </div>
  )
}
