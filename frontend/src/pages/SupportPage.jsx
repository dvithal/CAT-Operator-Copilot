import { useState, useEffect } from 'react'
import { Headphones, Plus, CheckCircle, Clock, AlertTriangle } from 'lucide-react'
import { getSupportRequests, getIncidents } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import SupportModal from './SupportModal.jsx'

export default function SupportPage({ machineId }) {
  const [requests, setRequests] = useState([])
  const [incidents, setIncidents] = useState([])
  const [loading, setLoading]   = useState(true)
  const [showModal, setShowModal] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const [r, i] = await Promise.all([
        getSupportRequests(machineId),
        getIncidents(machineId),
      ])
      setRequests(r); setIncidents(i)
    } catch {}
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [machineId])

  if (loading) return <LoadingSpinner label="Loading Support…" />

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Headphones size={20} className="text-cat-500" /> Support & Incidents
        </h1>
        <button onClick={() => setShowModal(true)} className="btn-primary">
          <Plus size={14} /> New Support Request
        </button>
      </div>

      {/* Incidents */}
      <div className="card">
        <div className="section-title">Operator Observations & Incidents</div>
        {incidents.length === 0 ? (
          <div className="text-sm text-surface-100 py-4 text-center">No incidents recorded for {machineId}.</div>
        ) : (
          <div className="space-y-2">
            {incidents.map((inc, i) => (
              <div key={i} className="flex items-start gap-3 border border-surface-500 rounded-lg p-3 text-sm">
                <AlertTriangle size={14} className={`mt-0.5 shrink-0 ${inc.severity === 'CRITICAL' || inc.severity === 'HIGH' ? 'text-red-400' : 'text-amber-400'}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-mono text-xs text-surface-100">{inc.incident_id}</span>
                    <StatusBadge status={inc.severity} dot={false} />
                    <span className="text-xs text-surface-100">{inc.category?.replace(/_/g,' ')}</span>
                  </div>
                  <div className="text-gray-300">{inc.description}</div>
                  <div className="text-xs text-surface-100 mt-0.5">{new Date(inc.timestamp).toLocaleString()}</div>
                </div>
                <StatusBadge status={inc.status} dot={false} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Support requests */}
      <div className="card">
        <div className="section-title">Support Requests</div>
        {requests.length === 0 ? (
          <div className="text-sm text-surface-100 py-4 text-center">No support requests for {machineId}.</div>
        ) : (
          <div className="space-y-3">
            {requests.map((r, i) => (
              <div key={i} className="border border-surface-500 rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-cat-500">{r.request_id}</span>
                  <StatusBadge status={r.status} />
                </div>
                <p className="text-sm text-gray-300">{r.description}</p>
                {r.troubleshooting_steps?.length > 0 && (
                  <div className="text-xs text-surface-100 space-y-1">
                    <div className="font-semibold text-gray-300 mb-1">Troubleshooting completed:</div>
                    {r.troubleshooting_steps.map((s, j) => (
                      <div key={j} className="flex items-center gap-1.5">
                        <CheckCircle size={11} className="text-green-400" /> {s}
                      </div>
                    ))}
                  </div>
                )}
                {r.xai_findings && (
                  <div className="bg-surface-600 rounded p-2 text-xs text-surface-100">
                    <strong className="text-gray-300">XAI: </strong>{r.xai_findings}
                  </div>
                )}
                <div className="flex items-center gap-2 text-xs text-surface-100">
                  <Clock size={11} /> {new Date(r.timestamp).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showModal && <SupportModal machineId={machineId} onClose={() => { setShowModal(false); load() }} />}
    </div>
  )
}
