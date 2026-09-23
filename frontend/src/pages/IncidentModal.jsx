import { useState } from 'react'
import { X, AlertTriangle } from 'lucide-react'
import { createIncident } from '../api/client.js'

const CATEGORIES = ['machine_performance', 'safety_concern', 'environmental', 'operator_comfort', 'other']
const SEVERITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

export default function IncidentModal({ machineId, onClose }) {
  const [form, setForm] = useState({ category: 'machine_performance', description: '', severity: 'MEDIUM', operator_id: 'OP-07' })
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(null)

  const submit = async () => {
    if (!form.description.trim()) return
    setSubmitting(true)
    try {
      const res = await createIncident({ machine_id: machineId, ...form })
      setDone(res)
    } catch {}
    finally { setSubmitting(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="card max-w-md w-full space-y-5" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle size={18} />
            <span className="font-semibold">Something Feels Wrong</span>
          </div>
          <button onClick={onClose} className="text-surface-200 hover:text-gray-100"><X size={18} /></button>
        </div>

        {done ? (
          <div className="space-y-3">
            <div className="bg-green-900/20 border border-green-700/40 rounded-lg p-4 text-sm">
              <div className="font-semibold text-green-400 mb-1">Incident Recorded</div>
              <div className="text-surface-100">ID: <span className="font-mono text-gray-200">{done.incident_id}</span></div>
              <div className="text-surface-100 mt-1">{done.description}</div>
            </div>
            <button onClick={onClose} className="btn-primary w-full justify-center">Close</button>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="text-xs text-surface-100 block mb-1">Category</label>
              <select value={form.category} onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                className="input">
                {CATEGORIES.map(c => <option key={c} value={c}>{c.replace(/_/g,' ')}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-surface-100 block mb-1">Severity</label>
              <select value={form.severity} onChange={e => setForm(f => ({ ...f, severity: e.target.value }))}
                className="input">
                {SEVERITIES.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-surface-100 block mb-1">Description</label>
              <textarea
                className="input h-24 resize-none"
                placeholder="Describe what you observed…"
                value={form.description}
                onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              />
            </div>
            <div className="flex gap-2">
              <button onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
              <button onClick={submit} disabled={submitting || !form.description.trim()} className="btn-primary flex-1 justify-center">
                {submitting ? 'Saving…' : 'Record Incident'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
