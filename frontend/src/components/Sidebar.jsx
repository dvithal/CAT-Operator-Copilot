import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Wrench, ShieldCheck, CheckSquare,
  CloudRain, Bot, BookOpen, FileText, Users, Headphones,
} from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { to: '/',          icon: LayoutDashboard, label: 'Command Center' },
  { to: '/machine',   icon: Wrench,          label: 'Machine'        },
  { to: '/safety',    icon: ShieldCheck,     label: 'Safety'         },
  { to: '/tasks',     icon: CheckSquare,     label: 'Tasks'          },
  { to: '/weather',   icon: CloudRain,       label: 'Weather'        },
  { to: '/copilot',   icon: Bot,             label: 'AI Copilot'     },
  { to: '/training',  icon: BookOpen,        label: 'Training'       },
  { to: '/reports',   icon: FileText,        label: 'Reports'        },
  { to: '/fleet',     icon: Users,           label: 'Fleet'          },
  { to: '/support',   icon: Headphones,      label: 'Support'        },
]

export default function Sidebar() {
  return (
    <aside className="w-56 shrink-0 h-screen bg-surface-800 border-r border-surface-600 flex flex-col sticky top-0">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-surface-600">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-cat-500 rounded-lg flex items-center justify-center">
            <span className="text-surface-900 font-bold text-xs">CAT</span>
          </div>
          <div>
            <div className="text-xs font-bold text-white leading-tight">SMART OPERATOR</div>
            <div className="text-xs text-surface-100 leading-tight">COPILOT</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 overflow-y-auto flex flex-col gap-0.5">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              clsx('nav-link', isActive && 'active')
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-surface-600">
        <div className="text-xs text-surface-100">v2.0 · Demo Mode</div>
      </div>
    </aside>
  )
}
