import clsx from 'clsx'

const STATUS_MAP = {
  NORMAL:       'badge-normal',
  OPERATIONAL:  'badge-normal',
  GOOD:         'badge-normal',
  CONTINUE:     'badge-normal',
  'CONTINUE WITH CAUTION': 'badge-caution',
  CAUTION:      'badge-caution',
  ATTENTION:    'badge-caution',
  IDLE:         'badge-caution',
  MEDIUM:       'badge-caution',
  HIGH:         'badge-critical',
  CRITICAL:     'badge-critical',
  'STOP / ESCALATE': 'badge-critical',
  'SAFETY CHECK RECOMMENDED': 'badge-caution',
  MAINTENANCE:  'badge-info',
  INFO:         'badge-info',
  IN_PROGRESS:  'badge-info',
  ANOMALY:      'badge-critical',
  LOW:          'badge-caution',
}

const DOT_MAP = {
  NORMAL: 'bg-green-400', OPERATIONAL: 'bg-green-400', GOOD: 'bg-green-400',
  CAUTION: 'bg-amber-400', ATTENTION: 'bg-amber-400', MEDIUM: 'bg-amber-400', IDLE: 'bg-amber-400',
  HIGH: 'bg-red-400', CRITICAL: 'bg-red-400', ANOMALY: 'bg-red-400',
  MAINTENANCE: 'bg-blue-400', INFO: 'bg-blue-400', IN_PROGRESS: 'bg-blue-400',
  LOW: 'bg-amber-400',
}

export default function StatusBadge({ status, dot = true, className }) {
  const key = (status || '').toUpperCase()
  const cls = STATUS_MAP[key] || 'badge-info'
  const dotCls = DOT_MAP[key] || 'bg-gray-400'
  return (
    <span className={clsx(cls, className)}>
      {dot && <span className={clsx('w-1.5 h-1.5 rounded-full inline-block', dotCls)} />}
      {status}
    </span>
  )
}
