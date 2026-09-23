import { useState, useEffect } from 'react'
import { ChevronRight, Cpu, Fuel, Clock } from 'lucide-react'
import { getMachines } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import ScoreRing from '../components/ScoreRing.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import ErrorState from '../components/ErrorState.jsx'

export default function FleetPage({ onSelect }) {
  const [machines, setMachines] = useState([])
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)

  const load = async () => {
    setLoading(true); setError(null)
    try { setMachines(await getMachines()) }
    catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  if (loading) return <LoadingSpinner label="Loading Fleet Overview…" />
  if (error)   return <ErrorState message={error} onRetry={load} />

  const critical = machines.filter(m => m.safety_score < 50 || m.health_score < 50)
  const caution  = machines.filter(m => !critical.includes(m) && (m.safety_score < 85 || m.health_score < 65 || m.behavior_anomaly))
  const normal   = machines.filter(m => !critical.includes(m) && !caution.includes(m))

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Fleet Overview</h1>
        <div className="flex gap-4 text-sm">
          <div className="text-green-400 font-semibold">{normal.length} Normal</div>
          <div className="text-amber-400 font-semibold">{caution.length} Caution</div>
          <div className="text-red-400 font-semibold">{critical.length} Critical</div>
        </div>
      </div>

      {critical.length > 0 && (
        <Section title="Critical" color="border-red-500" machines={critical} onSelect={onSelect} />
      )}
      {caution.length > 0 && (
        <Section title="Caution" color="border-amber-500" machines={caution} onSelect={onSelect} />
      )}
      {normal.length > 0 && (
        <Section title="Normal" color="border-green-500" machines={normal} onSelect={onSelect} />
      )}
    </div>
  )
}

function Section({ title, color, machines, onSelect }) {
  return (
    <div>
      <div className={`section-title border-l-2 pl-2 ${color}`}>{title}</div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {machines.map(m => <MachineCard key={m.machine_id} machine={m} onSelect={onSelect} />)}
      </div>
    </div>
  )
}

function MachineCard({ machine: m, onSelect }) {
  return (
    <div
      onClick={() => onSelect(m.machine_id)}
      className="card cursor-pointer hover:border-cat-500/50 transition-colors group space-y-3"
    >
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono font-bold text-cat-500">{m.machine_id}</span>
            <StatusBadge status={m.status} />
          </div>
          <div className="text-xs text-surface-100 mt-0.5">{m.model} · {m.machine_type}</div>
        </div>
        <ChevronRight size={16} className="text-surface-200 group-hover:text-cat-500 transition-colors" />
      </div>

      <div className="flex gap-3">
        <ScoreRing score={m.safety_score ?? 100} label="Safety" size={56} />
        <ScoreRing score={m.health_score  ?? 100} label="Health" size={56} />
        <div className="flex-1 space-y-1.5 text-xs">
          <InfoRow icon={Cpu}   label="Operator" value={m.current_operator_id || 'None'} />
          <InfoRow icon={Clock} label="Task"      value={m.current_task || 'Idle'} />
          <InfoRow icon={Fuel}  label="Fuel"      value={`${m.fuel_level_pct ?? '—'}%`} warn={m.fuel_level_pct < 20} />
        </div>
      </div>

      {m.behavior_anomaly && (
        <div className="text-xs text-red-400 bg-red-900/10 border border-red-700/30 rounded px-2 py-1">
          Behavioral anomaly detected
        </div>
      )}

      <div className="text-xs text-surface-100 truncate">{m.location}</div>
    </div>
  )
}

function InfoRow({ icon: Icon, label, value, warn }) {
  return (
    <div className="flex items-center gap-1.5">
      <Icon size={11} className="text-surface-200 shrink-0" />
      <span className="text-surface-100">{label}:</span>
      <span className={warn ? 'text-red-400' : 'text-gray-300'}>{value}</span>
    </div>
  )
}
