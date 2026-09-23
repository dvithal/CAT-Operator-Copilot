import { Bell, RefreshCw } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'
import MachinePicker from './MachinePicker.jsx'

export default function TopBar({ machineId, onMachineChange, status = 'OPERATIONAL', operator = '', task = '' }) {
  return (
    <header className="h-14 bg-surface-800 border-b border-surface-600 px-6 flex items-center gap-6 shrink-0">
      <div className="flex items-center gap-2 min-w-0">
        <span className="text-xs text-surface-100 uppercase tracking-wider">Machine</span>
        <MachinePicker value={machineId} onChange={onMachineChange} />
        <StatusBadge status={status} />
      </div>

      {operator && (
        <div className="hidden md:flex items-center gap-1.5 text-sm min-w-0">
          <span className="text-surface-100">Operator:</span>
          <span className="font-medium text-gray-200 truncate">{operator}</span>
        </div>
      )}

      {task && (
        <div className="hidden lg:flex items-center gap-1.5 text-sm min-w-0">
          <span className="text-surface-100">Task:</span>
          <span className="font-medium text-gray-200 truncate">{task}</span>
        </div>
      )}

      <div className="ml-auto flex items-center gap-3">
        <button className="p-1.5 text-surface-200 hover:text-gray-100 transition-colors">
          <Bell size={16} />
        </button>
        <div className="text-xs text-surface-100 font-mono">
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </header>
  )
}
