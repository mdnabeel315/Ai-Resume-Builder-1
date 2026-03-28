import { clsx } from 'clsx'
import { Loader2, AlertCircle, CheckCircle2, Info } from 'lucide-react'

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 16, className = '' }) {
  return <Loader2 size={size} className={clsx('animate-spin text-accent', className)} />
}

// ── Loading overlay ───────────────────────────────────────────────────────────
export function LoadingOverlay({ message = 'AI is thinking…' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-gray-400">
      <Spinner size={28} />
      <p className="text-sm font-mono">{message}</p>
    </div>
  )
}

// ── Alerts ────────────────────────────────────────────────────────────────────
export function Alert({ type = 'error', message }) {
  const styles = {
    error:   { cls: 'log-error',   Icon: AlertCircle },
    success: { cls: 'log-success', Icon: CheckCircle2 },
    info:    { cls: 'log-info',    Icon: Info },
    warn:    { cls: 'log-warn',    Icon: AlertCircle },
  }
  const { cls, Icon } = styles[type] ?? styles.error
  return (
    <div className={clsx(cls, 'mb-4')}>
      <Icon size={14} className="mt-0.5 shrink-0" />
      <span>{message}</span>
    </div>
  )
}

// ── Score badge ───────────────────────────────────────────────────────────────
export function ScoreBadge({ score }) {
  const cls =
    score >= 85 ? 'badge-green' :
    score >= 70 ? 'badge-yellow' :
    score >= 50 ? 'badge-purple' : 'badge-red'
  const label =
    score >= 85 ? 'Strong Match' :
    score >= 70 ? 'Good Match' :
    score >= 50 ? 'Partial Match' : 'Weak Match'
  return <span className={cls}>{score}% — {label}</span>
}

// ── Score bar ─────────────────────────────────────────────────────────────────
export function ScoreBar({ score, label }) {
  const color =
    score >= 85 ? 'bg-green-500' :
    score >= 70 ? 'bg-yellow-500' :
    score >= 50 ? 'bg-purple-500' : 'bg-red-500'
  return (
    <div>
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{label}</span><span className="font-mono">{score}%</span>
      </div>
      <div className="h-1.5 bg-dark-500 rounded-full overflow-hidden">
        <div className={clsx('h-full rounded-full transition-all duration-700', color)} style={{ width: `${score}%` }} />
      </div>
    </div>
  )
}

// ── Keyword pills ─────────────────────────────────────────────────────────────
export function Pills({ items = [], variant = 'default' }) {
  if (!items.length) return <span className="text-xs text-gray-600">None</span>
  const cls = { default: 'pill', green: 'pill-green', red: 'pill-red', accent: 'pill-accent' }
  return (
    <div className="flex flex-wrap gap-1">
      {items.map((kw, i) => <span key={i} className={cls[variant] ?? 'pill'}>{kw}</span>)}
    </div>
  )
}

// ── Section header ────────────────────────────────────────────────────────────
export function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-0.5">
        {Icon && <Icon size={16} className="text-accent" />}
        <h2 className="text-base font-semibold text-white">{title}</h2>
      </div>
      {subtitle && <p className="text-xs text-gray-500 ml-6">{subtitle}</p>}
    </div>
  )
}

// ── Stat card ─────────────────────────────────────────────────────────────────
export function StatCard({ label, value, sub, accent = false }) {
  return (
    <div className={clsx('card text-center', accent && 'border-accent/30 bg-accent/5')}>
      <div className={clsx('text-2xl font-bold font-mono', accent ? 'text-accent' : 'text-white')}>{value}</div>
      <div className="text-xs font-medium text-gray-300 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
    </div>
  )
}

// ── Tab bar ───────────────────────────────────────────────────────────────────
export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 bg-dark-800 p-1 rounded-lg mb-5 w-fit">
      {tabs.map(t => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={clsx(
            'px-4 py-1.5 rounded-md text-sm font-medium transition-colors duration-150',
            active === t.id ? 'bg-dark-600 text-white' : 'text-gray-500 hover:text-gray-300'
          )}
        >{t.label}</button>
      ))}
    </div>
  )
}

// ── Divider ───────────────────────────────────────────────────────────────────
export function Divider() {
  return <hr className="border-dark-500 my-6" />
}

// ── Empty state ───────────────────────────────────────────────────────────────
export function EmptyState({ icon: Icon, title, body, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
      {Icon && <div className="p-4 bg-dark-700 rounded-full"><Icon size={28} className="text-gray-600" /></div>}
      <p className="text-sm font-medium text-gray-400">{title}</p>
      {body && <p className="text-xs text-gray-600 max-w-xs">{body}</p>}
      {action}
    </div>
  )
}
