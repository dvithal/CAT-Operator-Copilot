/**
 * Feature 5 — Shift timeline component.
 * Renders a vertical timeline of events with severity colours.
 * Clearly marks simulated/demo events.
 */
import { Clock, AlertTriangle, ShieldAlert, Activity, CheckCircle, Play, Flag } from 'lucide-react'
import clsx from 'clsx'

const EVENT_ICONS = {
  shift_start:      Play,
  task_start:       Play,
  safety_event:     ShieldAlert,
  safety_check:     CheckCircle,
  anomaly_detected: AlertTriangle,
  behavior_normal:  Activity,
  feedback:         CheckCircle,
  current:          Flag,
}

const SEV_STYLE = {
  critical: 'border-red-600 bg-red-900/20 text-red-400',
  high:     'border-red-500 bg-red-900/10 text-red-400',
  medium:   'border-amber-600 bg-amber-900/20 text-amber-400',
  low:      'border-amber-500 bg-amber-900/10 text-amber-300',
  info:     'border-surface-500 bg-surface-600 text-gray-300',
}

const DOT_STYLE = {
  critical: 'bg-red-500',
  high:     'bg-red-400',
  medium:   'bg-amber-400',
  low:      'bg-amber-300',
  info:     'bg-surface-300',
}

export default function ShiftTimeline({ events = [], maxItems = 8 }) {
  if (!events.length) return (
    <div className="text-sm text-surface-100 text-center py-4">No timeline events yet.</div>
  )

  const displayed = events.slice(-maxItems)

  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-[11px] top-0 bottom-0 w-px bg-surface-500" />

      <div className="space-y-3">
        {displayed.map((ev, i) => {
          const sev  = (ev.severity || 'info').toLowerCase()
          const Icon = EVENT_ICONS[ev.event_type] || Clock
          const dotCls = DOT_STYLE[sev] || DOT_STYLE.info

          return (
            <div key={i} className="flex gap-3 relative">
              {/* Dot */}
              <div className={clsx('w-6 h-6 rounded-full flex items-center justify-center shrink-0 z-10 border border-surface-600', dotCls.replace('bg-', 'bg-').replace('-500','-500'))}>
                <Icon size={10} className="text-white" />
              </div>

              {/* Content */}
              <div className={clsx('flex-1 rounded-lg border px-3 py-2 text-xs', SEV_STYLE[sev] || SEV_STYLE.info)}>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{ev.label}</span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span className="font-mono text-surface-100">{ev.time_label}</span>
                    {ev.is_simulated && (
                      <span className="px-1 py-0.5 bg-surface-500 text-surface-100 rounded text-xs">demo</span>
                    )}
                  </div>
                </div>
                {ev.detail && <div className="text-surface-100 mt-0.5 line-clamp-2">{ev.detail}</div>}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
