/**
 * Feature 10 — Evidence panel for AI Copilot responses.
 * Clearly distinguishes OBSERVED / MODEL OUTPUT / MODEL EXPLANATION / RECOMMENDATION.
 */
import { useState } from 'react'
import { Eye, Cpu, FlaskConical, Lightbulb, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const SECTIONS = [
  { key: 'observed',          Icon: Eye,          label: 'Observed',          cls: 'text-blue-400' },
  { key: 'model_output',      Icon: Cpu,          label: 'Model Output',      cls: 'text-cat-500' },
  { key: 'model_explanation', Icon: FlaskConical, label: 'Model Explanation', cls: 'text-purple-400' },
  { key: 'recommendations',   Icon: Lightbulb,    label: 'Recommendations',   cls: 'text-green-400' },
]

function DirIcon({ dir }) {
  if (dir === 'increase') return <TrendingUp size={10} className="text-red-400 shrink-0" />
  if (dir === 'decrease') return <TrendingDown size={10} className="text-green-400 shrink-0" />
  return <Minus size={10} className="text-surface-200 shrink-0" />
}

export default function EvidencePanel({ evidence }) {
  const [open, setOpen] = useState(false)
  if (!evidence) return null

  const hasContent = SECTIONS.some(s => evidence[s.key]?.length > 0)
  if (!hasContent) return null

  return (
    <div className="mt-3 border border-surface-500 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-surface-600 text-xs text-left"
      >
        <span className="font-medium text-surface-100">Why I say this — Evidence</span>
        {open ? <ChevronUp size={12} className="text-surface-200" /> : <ChevronDown size={12} className="text-surface-200" />}
      </button>

      {open && (
        <div className="p-4 space-y-4 bg-surface-700">
          {SECTIONS.map(({ key, Icon, label, cls }) => {
            const items = evidence[key]
            if (!items?.length) return null
            return (
              <div key={key}>
                <div className={clsx('flex items-center gap-1.5 text-xs font-semibold mb-2 uppercase tracking-wider', cls)}>
                  <Icon size={11} /> {label}
                </div>
                <div className="space-y-1.5">
                  {key === 'observed' && items.map((item, i) => (
                    <div key={i} className="flex items-center justify-between text-xs px-2 py-1 bg-surface-600 rounded">
                      <span className="text-surface-100">{item.label}</span>
                      <span className="text-gray-200 font-medium">{String(item.value)}</span>
                    </div>
                  ))}
                  {key === 'model_output' && items.map((item, i) => (
                    <div key={i} className="px-2 py-1.5 bg-surface-600 rounded text-xs space-y-0.5">
                      <div className="flex items-center justify-between">
                        <span className="text-surface-100">{item.label}</span>
                        <span className="text-cat-500 font-semibold">{String(item.value)}</span>
                      </div>
                      {item.detail && <div className="text-surface-100">{item.detail}</div>}
                      <div className="text-surface-200 font-mono text-xs">source: {item.source}</div>
                    </div>
                  ))}
                  {key === 'model_explanation' && items.map((item, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs px-2 py-1 bg-surface-600 rounded">
                      <DirIcon dir={item.direction} />
                      <span className="text-gray-300 flex-1">{item.label}</span>
                      <span className="text-surface-100">{item.value}</span>
                      {item.contribution && (
                        <span className={clsx(
                          'font-mono px-1 rounded text-xs',
                          item.direction === 'increase' ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'
                        )}>{item.contribution}</span>
                      )}
                    </div>
                  ))}
                  {key === 'recommendations' && items.map((item, i) => (
                    <div key={i} className="flex gap-2 text-xs px-2 py-1.5 bg-surface-600 rounded">
                      <span className="text-green-400 shrink-0 font-bold">{i + 1}.</span>
                      <span className="text-gray-300 flex-1">{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}

          {evidence.evidence_note && (
            <p className="text-xs text-surface-200 italic pt-1 border-t border-surface-500">{evidence.evidence_note}</p>
          )}
        </div>
      )}
    </div>
  )
}
