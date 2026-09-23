import { ChevronDown } from 'lucide-react'

const MACHINES = ['EXC001', 'EXC002', 'EXC003', 'LD003', 'DZ004']

export default function MachinePicker({ value, onChange }) {
  return (
    <div className="relative inline-flex items-center gap-1">
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        className="appearance-none bg-surface-600 border border-surface-400 rounded-lg pl-3 pr-8 py-1.5 text-sm font-mono font-semibold text-cat-500 focus:outline-none focus:border-cat-500 cursor-pointer"
      >
        {MACHINES.map(m => <option key={m} value={m}>{m}</option>)}
      </select>
      <ChevronDown size={14} className="absolute right-2 text-surface-200 pointer-events-none" />
    </div>
  )
}
