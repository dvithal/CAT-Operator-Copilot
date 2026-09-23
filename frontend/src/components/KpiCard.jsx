import clsx from 'clsx'

export default function KpiCard({ label, value, unit, icon: Icon, status, sub, className }) {
  const statusColor = {
    NORMAL: 'text-green-400', GOOD: 'text-green-400',
    CAUTION: 'text-amber-400', ATTENTION: 'text-amber-400', MEDIUM: 'text-amber-400',
    CRITICAL: 'text-red-400', HIGH: 'text-red-400', ANOMALY: 'text-red-400',
    INFO: 'text-blue-400',
  }[status?.toUpperCase()] || 'text-gray-200'

  return (
    <div className={clsx('kpi-card', className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs text-surface-100 font-medium uppercase tracking-wider">{label}</span>
        {Icon && <Icon size={16} className="text-surface-200" />}
      </div>
      <div className={clsx('text-2xl font-bold', statusColor)}>
        {value ?? '—'}{unit && <span className="text-sm font-normal text-surface-100 ml-1">{unit}</span>}
      </div>
      {sub && <div className="text-xs text-surface-100 truncate">{sub}</div>}
    </div>
  )
}
