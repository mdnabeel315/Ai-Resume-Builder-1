import { NavLink, useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import {
  LayoutDashboard, FileText, Mail, Search, Globe,
  Zap, Trash2,
} from 'lucide-react'
import { useStore } from '../../lib/store'

const NAV = [
  { to: '/',             icon: LayoutDashboard, label: 'Overview Dashboard' },
  { to: '/resume',       icon: FileText,        label: 'Smart Resume Builder' },
  { to: '/cover-letter', icon: Mail,            label: 'Cover Letter Generator' },
  { to: '/ats',          icon: Search,          label: 'ATS Match Engine' },
  { to: '/jobs',         icon: Globe,           label: 'Job Portal' },
]

export default function Sidebar() {
  const { state, dispatch } = useStore()
  const navigate = useNavigate()

  function clearAll() {
    if (confirm('Clear all data and start fresh?')) {
      dispatch({ type: 'CLEAR_ALL' })
      navigate('/')
    }
  }

  return (
    <aside className="w-56 shrink-0 bg-dark-800 border-r border-dark-500 flex flex-col h-screen sticky top-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-dark-500">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-accent flex items-center justify-center">
            <Zap size={14} className="text-dark-900" />
          </div>
          <div>
            <div className="text-sm font-bold text-white tracking-wide">ZNA AI Studio</div>
            <div className="text-[10px] text-gray-600 font-mono">Career Workspace</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="section-title px-2 mb-3">Navigate Workspace</p>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => clsx(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors duration-150',
              isActive
                ? 'bg-accent/10 text-accent border border-accent/20'
                : 'text-gray-500 hover:text-gray-200 hover:bg-dark-700'
            )}
          >
            {({ isActive }) => (
              <>
                <span className={clsx(
                  'w-1.5 h-1.5 rounded-full shrink-0',
                  isActive ? 'bg-accent' : 'bg-dark-500'
                )} />
                <Icon size={14} className="shrink-0" />
                <span className="truncate">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Job Portal hint / status */}
      <div className="px-3 pb-3">
        <div className="card text-xs">
          <p className="section-title mb-2">Job Portal</p>
          {state.targetJobTitle ? (
            <div className="badge-green text-xs px-2 py-1 rounded">
              🎯 {state.targetJobTitle}
            </div>
          ) : (
            <p className="text-gray-600 leading-relaxed">
              💡 Fill out the <span className="text-accent">'Target Job Title'</span> in the Resume Builder to unlock the LinkedIn Job Portal.
            </p>
          )}
        </div>

        {/* Clear session */}
        <button onClick={clearAll} className="btn-ghost w-full mt-2 justify-center text-gray-600 hover:text-red-400">
          <Trash2 size={12} />
          Clear Session
        </button>
      </div>
    </aside>
  )
}
