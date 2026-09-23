import { useState, useEffect } from 'react'
import { QrCode, RefreshCw, AlertTriangle, Wrench, Thermometer, Droplets, Activity } from 'lucide-react'
import { getPassport, getMachineQR, getMachineHistory } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import ScoreRing from '../components/ScoreRing.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import IncidentModal from './IncidentModal.jsx'
import SupportModal from './SupportModal.jsx'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function MachinePage({ machineId }) {
  const [passport, setPassport]   = useState(null)
  const [qr, setQr]               = useState(null)
  const [history, setHistory]     = useState([])
  const [showQR, setShowQR]       = useState(false)
  const [showIncident, setShowIncident] = useState(false)
  const [showSupport, setShowSupport]   = useState(false)
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try {
      const [p, h] = await Promise.all([getPassport(machineId), getMachineHistory(machineId)])
      setPassport(p)
      setHistory(h.history || [])
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  const loadQR = async () => {
    try { const q = await getMachineQR(machineId); setQr(q); setShowQR(true) }
    catch {}
  }

  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Machine Passport…" />
  if (error)   return <ErrorState message={error} onRetry={load} />

  const p = passport || {}
  const op = p.current_operator || {}
  const task = p.current_task || {}
  const health = p.health || {}
  const behavior = p.behavior || {}
  const weather = p.weather || {}

  return (
    <div className="space-y-6 max-w-7xl mx-auto">

      {/* ── Header ─────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-3">
            Machine Digital Passport
            <StatusBadge status={p.status} />
          </h1>
          <p className="text-sm text-surface-100 mt-0.5">{p.model} · {p.machine_type} · {p.location}</p>
        </div>
        <div className="flex gap-2 shrink-0">
          <button onClick={loadQR} className="btn-secondary">
            <QrCode size={14} /> Show QR
          </button>
          <button onClick={() => setShowIncident(true)} className="btn-secondary text-amber-400 border-amber-700/40">
            <AlertTriangle size={14} /> Something Feels Wrong
          </button>
          <button onClick={() => setShowSupport(true)} className="btn-danger">
            <Wrench size={14} /> Get Help
          </button>
        </div>
      </div>

      {/* ── QR Modal ───────────────────────────────────────── */}
      {showQR && qr && (
        <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center" onClick={() => setShowQR(false)}>
          <div className="card max-w-xs w-full text-center space-y-4" onClick={e => e.stopPropagation()}>
            <div className="text-sm font-semibold text-cat-500">Machine QR Code</div>
            <div className="text-xs text-surface-100 font-mono">{qr.qr_data}</div>
            {qr.qr_image_base64
              ? <img src={`data:image/png;base64,${qr.qr_image_base64}`} alt="QR" className="mx-auto w-48 h-48 rounded-lg" />
              : <div className="text-surface-100 text-sm">QR library not installed on backend.</div>
            }
            <p className="text-xs text-surface-100">{qr.note}</p>
            <button onClick={() => setShowQR(false)} className="btn-secondary w-full">Close</button>
          </div>
        </div>
      )}

      {/* ── Passport Grid ──────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

        {/* Identity */}
        <div className="card space-y-3">
          <div className="section-title">Machine Identity</div>
          <PassportRow label="Machine ID"     value={p.machine_id} mono />
          <PassportRow label="Type"           value={p.machine_type} />
          <PassportRow label="Model"          value={p.model} />
          <PassportRow label="Year"           value={p.year} />
          <PassportRow label="Serial"         value={p.serial_number} mono />
          <PassportRow label="Location"       value={p.location} />
          <PassportRow label="Status"         value={<StatusBadge status={p.status} />} />
          <PassportRow label="Last Service"   value={p.last_service_date} />
          <PassportRow label="Next Service"   value={`@ ${p.next_service_hours?.toLocaleString()} hrs`} />
        </div>

        {/* Telemetry */}
        <div className="card space-y-3">
          <div className="section-title">Current Telemetry</div>
          <PassportRow label="Engine Hours"   value={p.engine_hours?.toLocaleString()} unit="hrs" />
          <PassportRow label="Fuel Used"      value={p.fuel_used_l} unit="L" />
          <PassportRow label="Fuel Level"     value={p.fuel_level_pct} unit="%" highlight={p.fuel_level_pct < 20} />
          <PassportRow label="Load Cycles"    value={p.load_cycles} />
          <PassportRow label="Idle Time"      value={p.idle_time_min} unit="min" highlight={p.idle_time_min > 40} />
          <PassportRow label="Seatbelt"       value={p.seatbelt_status} highlight={p.seatbelt_status === 'Unfastened'} />
          <PassportRow label="Safety Alert"   value={p.safety_alert} highlight={p.safety_alert === 'Yes'} />

          {/* Gauges */}
          <div className="grid grid-cols-3 gap-2 pt-2">
            <Gauge icon={Thermometer} label="Engine" value={`${p.hydraulic_temp_c ?? '—'}°C`} warn={(p.engine_temp_c||0) > 95} />
            <Gauge icon={Activity}    label="Oil PSI" value={`${p.oil_pressure_bar ?? '—'} bar`} warn={(p.oil_pressure_bar||4) < 3.5} />
            <Gauge icon={Droplets}    label="Hydraul" value={`${p.hydraulic_temp_c ?? '—'}°C`} />
          </div>
        </div>

        {/* Scores + Status */}
        <div className="card space-y-4">
          <div className="section-title">Status Overview</div>
          <div className="flex justify-around">
            <ScoreRing score={p.safety_score ?? 100} label="Safety" size={80} />
            <ScoreRing score={health.score ?? 100}   label="Health" size={80} />
          </div>

          <div className="space-y-2 text-sm">
            <PassportRow label="Safety Decision"  value={p.safety_decision} />
            <PassportRow label="Health Status"    value={health.status} />
            <PassportRow label="Behavior"         value={<StatusBadge status={behavior.status || 'NORMAL'} />} />
          </div>

          <div className="border-t border-surface-500 pt-3 space-y-2">
            <div className="section-title">Current Operator</div>
            {op.name ? <>
              <PassportRow label="Name"   value={op.name} />
              <PassportRow label="Skill"  value={op.skill_level} />
              <PassportRow label="Shift"  value={op.shift} />
            </> : <div className="text-sm text-surface-100">None assigned</div>}
          </div>

          <div className="border-t border-surface-500 pt-3 space-y-2">
            <div className="section-title">Current Task</div>
            {task.task_type ? <>
              <PassportRow label="Task"     value={task.task_type} />
              <PassportRow label="Status"   value={<StatusBadge status={p.task_status || 'IN_PROGRESS'} />} />
              <PassportRow label="Weather"  value={weather.condition} />
              <PassportRow label="Risk"     value={weather.risk_level} />
            </> : <div className="text-sm text-surface-100">No active task</div>}
          </div>
        </div>
      </div>

      {/* ── History Chart ──────────────────────────────────── */}
      {history.length > 0 && (
        <div className="card">
          <div className="section-title">7-Day Machine History</div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={history} barGap={2}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232b3a" />
              <XAxis dataKey="date" tick={{ fill: '#718096', fontSize: 11 }} />
              <YAxis tick={{ fill: '#718096', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#161b24', border: '1px solid #232b3a', borderRadius: 8 }} />
              <Bar dataKey="engine_hours"  name="Engine Hrs"  fill="#FFCD11" radius={[2,2,0,0]} />
              <Bar dataKey="load_cycles"   name="Load Cycles" fill="#3b82f6" radius={[2,2,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Modals */}
      {showIncident && <IncidentModal machineId={machineId} onClose={() => setShowIncident(false)} />}
      {showSupport  && <SupportModal  machineId={machineId} onClose={() => setShowSupport(false)} />}
    </div>
  )
}

function PassportRow({ label, value, unit, mono, highlight }) {
  return (
    <div className="flex items-center justify-between text-sm gap-2">
      <span className="text-surface-100 shrink-0">{label}</span>
      <span className={`${mono ? 'font-mono text-xs' : ''} ${highlight ? 'text-red-400 font-semibold' : 'text-gray-200'}`}>
        {value ?? '—'}{unit && <span className="text-surface-100 ml-1 text-xs">{unit}</span>}
      </span>
    </div>
  )
}

function Gauge({ icon: Icon, label, value, warn }) {
  return (
    <div className={`rounded-lg p-2 text-center border ${warn ? 'border-red-700/50 bg-red-900/10' : 'border-surface-500 bg-surface-600'}`}>
      <Icon size={14} className={`mx-auto mb-1 ${warn ? 'text-red-400' : 'text-surface-200'}`} />
      <div className={`text-xs font-semibold ${warn ? 'text-red-400' : 'text-gray-200'}`}>{value}</div>
      <div className="text-xs text-surface-100">{label}</div>
    </div>
  )
}
