/**
 * Feature 7 — Model Transparency Panel.
 * Shows honest model metadata. Never exaggerates performance.
 */
import { useState } from 'react'
import { ChevronDown, ChevronUp, Info, AlertTriangle } from 'lucide-react'

function ModelBlock({ title, data }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="border border-surface-500 rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 bg-surface-600 text-sm text-left"
      >
        <span className="font-medium text-gray-200">{title}</span>
        {open ? <ChevronUp size={14} className="text-surface-200" /> : <ChevronDown size={14} className="text-surface-200" />}
      </button>
      {open && (
        <div className="px-4 py-3 space-y-2 text-xs">
          {data.algorithm && <Row k="Algorithm" v={data.algorithm} />}
          {data.training_data && <Row k="Training data" v={data.training_data} />}
          {data.held_out_mae_min && <Row k="Held-out test MAE" v={`${data.held_out_mae_min} min`} />}
          {data.uncertainty_method && <Row k="Uncertainty" v={data.uncertainty_method} />}
          {data.rules && <Row k="Rules" v={data.rules} />}
          {data.note && <Row k="Note" v={data.note} />}
          {data.features_used?.length > 0 && (
            <div>
              <div className="text-surface-100 mb-1">Features used:</div>
              {data.features_used.map((f, i) => (
                <div key={i} className="text-gray-400 pl-2">· {f}</div>
              ))}
            </div>
          )}
          {data.limitations?.length > 0 && (
            <div>
              <div className="text-amber-400 mb-1 flex items-center gap-1"><AlertTriangle size={10} /> Limitations:</div>
              {data.limitations.map((l, i) => (
                <div key={i} className="text-amber-300/70 pl-2 text-xs">· {l}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function Row({ k, v }) {
  return (
    <div className="flex gap-2">
      <span className="text-surface-100 shrink-0 w-32">{k}:</span>
      <span className="text-gray-300">{String(v)}</span>
    </div>
  )
}

export default function ModelTransparencyPanel({ data }) {
  if (!data) return null
  return (
    <div className="card space-y-3">
      <div className="flex items-center gap-2">
        <Info size={14} className="text-blue-400" />
        <span className="section-title mb-0">Model Transparency</span>
      </div>

      <div className="space-y-2">
        {data.eta_model      && <ModelBlock title="ETA Prediction — Linear Regression"         data={data.eta_model} />}
        {data.behavior_model && <ModelBlock title="Behavior Anomaly — Isolation Forest + MAD"  data={data.behavior_model} />}
        {data.safety_engine  && <ModelBlock title="Safety Engine — Deterministic Rules"        data={data.safety_engine} />}
        {data.weather_model  && <ModelBlock title="Weather Impact — Lookup Table"              data={data.weather_model} />}
      </div>

      {data.general_disclaimer && (
        <div className="bg-amber-900/10 border border-amber-700/30 rounded-lg px-3 py-2 text-xs text-amber-300 flex gap-2">
          <AlertTriangle size={12} className="mt-0.5 shrink-0" />
          <span>{data.general_disclaimer}</span>
        </div>
      )}
    </div>
  )
}
