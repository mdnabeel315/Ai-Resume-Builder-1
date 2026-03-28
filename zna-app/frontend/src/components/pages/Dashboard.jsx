import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { FileText, Mail, Search, Globe, CheckCircle2, Info, Clock } from 'lucide-react'
import { useStore } from '../../lib/store'
import { api } from '../../lib/api'
import { StatCard } from '../ui'

const PLACEHOLDER_HISTORY = [65, 70, 68, 75, 82, 85, 92]

const QUICK_CARDS = [
  { to: '/resume',       icon: FileText, label: 'Smart Resume Builder',    desc: 'Parse LinkedIn/resume text → polished ATS resume.' },
  { to: '/cover-letter', icon: Mail,     label: 'Cover Letter Generator',  desc: 'Auto-generate a tailored letter from your resume + JD.' },
  { to: '/ats',          icon: Search,   label: 'ATS Match Engine',        desc: 'Deep scan: keyword breakdown vs any job description.' },
  { to: '/jobs',         icon: Globe,    label: 'Job Portal',              desc: 'AI LinkedIn strategy, company targets, salary ranges.' },
]

export default function Dashboard() {
  const { state } = useStore()
  const navigate = useNavigate()
  const [apiStatus, setApiStatus] = useState('checking')

  const history = state.atsHistory.length
    ? state.atsHistory.map((s, i) => ({ session: i + 1, score: s }))
    : PLACEHOLDER_HISTORY.map((s, i) => ({ session: i + 1, score: s }))

  useEffect(() => {
    api.health()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('error'))
  }, [])

  return (
    <div className="page">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-1">Welcome to your Career Workspace 🔗</h1>
        <p className="text-gray-500 text-sm">Your central hub for AI-powered career growth and optimisation.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Dynamic Templates" value="3" sub="Styles" />
        <StatCard label="Input Modes"        value="Dual" sub="Auto / Manual" />
        <StatCard label="Cover Letters"      value="Auto" sub="Gen" />
        <StatCard label="ATS Scanner"        value="NLP" sub="Semantic" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* ATS Trend Chart */}
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
            📈 ATS Optimisation Trends
          </h2>
          <p className="text-xs text-gray-600 mb-4">Average ATS Match Scores over the last sessions.</p>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={history}>
              <XAxis dataKey="session" tick={{ fontSize: 10, fill: '#6b7280' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{ background: '#1a1d27', border: '1px solid #2d3147', borderRadius: 8, fontSize: 12 }}
                labelStyle={{ color: '#9ca3af' }}
                itemStyle={{ color: '#00d4ff' }}
              />
              <Line type="monotone" dataKey="score" stroke="#00d4ff" strokeWidth={2} dot={{ r: 3, fill: '#00d4ff' }} />
            </LineChart>
          </ResponsiveContainer>
          {!state.atsHistory.length && (
            <p className="text-[10px] text-gray-700 text-center mt-1">Sample data — generate your first resume to start tracking</p>
          )}
        </div>

        {/* Live System Logs */}
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            ⚡ Live System Logs
          </h2>
          <div className="space-y-2">
            <div className={apiStatus === 'ok' ? 'log-success' : apiStatus === 'error' ? 'log-error' : 'log-warn'}>
              <CheckCircle2 size={12} className="mt-0.5 shrink-0" />
              <span>
                {apiStatus === 'ok'       && '[System] LLM Engine connected to Gemini 2.0 Flash.'}
                {apiStatus === 'error'    && '[System] Cannot reach backend API. Is it running?'}
                {apiStatus === 'checking' && '[System] Checking backend connection…'}
              </span>
            </div>
            <div className="log-info">
              <Info size={12} className="mt-0.5 shrink-0" />
              <span>[Module] PDF Generation engine ready.</span>
            </div>
            <div className="log-warn">
              <Clock size={12} className="mt-0.5 shrink-0" />
              <span>
                {state.resume
                  ? `[Memory] Resume loaded for ${state.resume.name ?? 'user'}.`
                  : '[Memory] Waiting for user to generate a resume…'}
              </span>
            </div>
            {state.atsResult && (
              <div className="log-success">
                <CheckCircle2 size={12} className="mt-0.5 shrink-0" />
                <span>[ATS] Last scan score: {state.atsResult.overall_score}%</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick start cards */}
      <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4">🚀 Quick Start</h2>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {QUICK_CARDS.map(({ to, icon: Icon, label, desc }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="card-hover text-left group"
          >
            <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center mb-3 group-hover:bg-accent/20 transition-colors">
              <Icon size={16} className="text-accent" />
            </div>
            <div className="text-sm font-semibold text-white mb-1">{label}</div>
            <div className="text-xs text-gray-500 leading-relaxed">{desc}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
