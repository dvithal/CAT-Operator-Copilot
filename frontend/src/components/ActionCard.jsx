/**
 * Feature 2 — WHAT SHOULD I DO card.
 * Renders a recommended_action object from any backend intelligence endpoint.
 */
import { ChevronDown, ChevronUp, Lightbulb } from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

const PRIORITY_STYLE = {
  HIGH:   'border-red-700/50 bg-red-900/10 text-red-400',
  MEDIUM: 'border-amber-700/50 bg-amber-900/10 text-amber-400',
  LOW:    'border-surface-500 bg-surface-600 text-gray-300',
  NONE:   'border-green-700/40 bg-green-900/10 text-green-400',
}

export default function ActionCard({ action, title = 'What Should I Do?' }) {
  const [open, setOpen] = useState(true)
  if (!action || action.priority === 'NONE') return null

  const style = PRIORITY_STYLE[action.priority] || PRIORITY_STYLE.LOW

  return (
    <div className={clsx('border rounded-xl overflow-hidden', style)}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2 font-semibold text-sm">
          <Lightbulb size={14} />
          {title}
          {action.priority && (
            <span className="text-xs font-normal opacity-70">{action.priority}</span>
          )}
        </div>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-2">
          <p className="text-sm text-gray-300">{action.action}</p>
          {action.steps?.length > 0 && (
            <ol className="space-y-1.5">
              {action.steps.map((step, i) => (
                <li key={i} className="flex gap-2 text-xs text-gray-400">
                  <span className="shrink-0 font-bold">{i + 1}.</span>
                  <span>{step}</span>
                </li>
              ))}
            </ol>
          )}
        </div>
      )}
    </div>
  )
}
