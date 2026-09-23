import { useState } from 'react'
import { X, Wrench, CheckCircle } from 'lucide-react'
import { createSupportRequest, getXAIBehavior, getSafety } from '../api/client.js'

const STEPS = [
  'Check engine temperature and oil pressure gauges.',
  'Inspect hydraulic lines for visible leaks or unusual sounds.',
  'Review recent load cycles and compare with normal operation.',
  'Check for unusual vibrations or noises during movement.',
  'Ensure all fluid levels are within normal operating range.',
]

export default function SupportModal({ machineId, onClose }) {
  const [step, setStep] = useState(0) // 0=describe, 1=troubleshoot, 2=brief
  const [description, setDescription] = useState('')
  const [checkedSteps, setCheckedSteps] = useState([])
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const toggleStep = (i) => setCheckedSteps(p => p.includes(i) ? p.filter(x => x !== i) : [...p, i])

  const createRequest = async () => {
    setLoading(true)
    try {
      const [beh, saf] = await Promise.all([getXAIBehavior(machineId), getSafety(machineId)])
      const xaiFindings = beh?.explanation || 'No XAI data available.'
      const safetyState = saf?.decision || 'UNKNOWN'
      const completedSteps = checkedSteps.map(i => STEPS[i])
      const res = await createSupportRequest({
        machine_id: machineId,
        operator_id: 'OP-07',
        description,
        troubleshooting_steps: completedSteps,
        xai_findings: xaiFindings,
        safety_state: safetyState,
      })
      setResult({ req: res, xai: beh, safety: saf })
      setStep(2)
    } catch {}
    finally { setLoading(false) }
  }

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="card max-w-lg w-full space-y-5 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-red-400">
            <Wrench size={18} />
            <span className="font-semibold">Get Help — CAT Support</span>
          </div>
          <button onClick={onClose} className="text-surface-200 hover:text-gray-100"><X size={18} /></button>
        </div>

        {step === 0 && (
          <div className="space-y-4">
            <p className="text-sm text-surface-100">Describe what you're experiencing with the machine.</p>
            <textarea
              className="input h-28 resize-none"
              placeholder="e.g. The bucket movement feels slower than usual…"
              value={description}
              onChange={e => setDescription(e.target.value)}
            />
            <div className="flex gap-2">
              <button onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
              <button onClick={() => setStep(1)} disabled={!description.trim()} className="btn-primary flex-1 justify-center">
                Start Troubleshooting
              </button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <p className="text-sm text-surface-100">Work through these checks. Tick each one you've completed.</p>
            <div className="space-y-2">
              {STEPS.map((s, i) => (
                <label key={i} className="flex items-start gap-3 cursor-pointer group">
                  <input type="checkbox" className="mt-0.5 accent-cat-500" checked={checkedSteps.includes(i)} onChange={() => toggleStep(i)} />
                  <span className={`text-sm ${checkedSteps.includes(i) ? 'line-through text-surface-100' : 'text-gray-200'}`}>{s}</span>
                </label>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={() => setStep(0)} className="btn-secondary flex-1 justify-center">Back</button>
              <button onClick={createRequest} disabled={loading} className="btn-danger flex-1 justify-center">
                {loading ? 'Generating Brief…' : 'Connect to CAT Expert'}
              </button>
            </div>
          </div>
        )}

        {step === 2 && result && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-green-400">
              <CheckCircle size={16} />
              <span className="font-semibold text-sm">Support Request Created — {result.req.request_id}</span>
            </div>

            <div className="bg-surface-600 rounded-lg p-4 space-y-2 text-xs font-mono">
              <div className="text-cat-500 font-bold text-sm mb-2">CAT TECHNICIAN SUPPORT BRIEF</div>
              <BriefRow k="Machine"     v={machineId} />
              <BriefRow k="Operator"    v={result.req.operator_id} />
              <BriefRow k="Safety"      v={result.req.safety_state} />
              <BriefRow k="Observation" v={description} />
              <div className="border-t border-surface-500 pt-2 mt-2">
                <div className="text-surface-100 mb-1">Troubleshooting Completed:</div>
                {result.req.troubleshooting_steps.length
                  ? result.req.troubleshooting_steps.map((s, i) => <div key={i} className="text-gray-300">✓ {s}</div>)
                  : <div className="text-surface-100">None completed.</div>}
              </div>
              {result.xai?.explanation && (
                <div className="border-t border-surface-500 pt-2 mt-2">
                  <div className="text-surface-100 mb-1">XAI Findings:</div>
                  <div className="text-gray-300 whitespace-pre-wrap">{result.xai.explanation}</div>
                </div>
              )}
            </div>

            <div className="bg-red-900/20 border border-red-700/40 rounded-lg p-3 text-sm text-red-300 text-center font-semibold">
              🔧 CONNECT TO CAT EXPERT (Simulated for Demo)
            </div>
            <button onClick={onClose} className="btn-primary w-full justify-center">Close</button>
          </div>
        )}
      </div>
    </div>
  )
}

function BriefRow({ k, v }) {
  return (
    <div className="flex gap-2">
      <span className="text-surface-100 w-24 shrink-0">{k}:</span>
      <span className="text-gray-200">{v}</span>
    </div>
  )
}
