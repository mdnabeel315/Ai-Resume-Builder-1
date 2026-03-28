import { useState } from 'react'
import { Globe, Zap, ExternalLink } from 'lucide-react'
import { useStore } from '../../lib/store'
import { api } from '../../lib/api'
import { Spinner, Alert, Pills, EmptyState } from '../ui'

export default function JobPortal() {
  const { state, dispatch } = useStore()
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState('')
  const [strategy, setStrategy]   = useState(null)
  const [jd, setJd]               = useState(state.jobDescription)
  const [scanLoading, setScanLoading] = useState(false)
  const [quickResult, setQuickResult] = useState(null)

  const title  = state.targetJobTitle
  const skills = state.resume?.skills?.technical ?? []

  async function handleStrategy() {
    if (!title) return setError('Set a Target Job Title in the Resume Builder first.')
    setError(''); setLoading(true)
    try {
      const res = await api.jobs.strategy(title, skills)
      setStrategy(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleQuickScan() {
    if (!state.resume) return setError('Build your resume first.')
    if (!jd.trim())    return setError('Paste a job description.')
    setError(''); setScanLoading(true)
    try {
      dispatch({ type: 'SET_JOB_DESCRIPTION', payload: jd })
      const res = await api.ats.scan(state.resume, jd)
      setQuickResult(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setScanLoading(false)
    }
  }

  if (!title) {
    return (
      <div className="page">
        <h1 className="page-title">🌐 Job Portal</h1>
        <EmptyState
          icon={Globe}
          title="Job Portal Locked"
          body="Fill out the 'Target Job Title' in the Resume Builder to unlock AI-powered job search strategy."
        />
      </div>
    )
  }

  return (
    <div className="page">
      <h1 className="page-title">🌐 Job Portal</h1>
      <p className="page-subtitle">AI-powered job search strategy tailored to your resume and target role.</p>

      {/* Resume card */}
      {state.resume && (
        <div className="card mb-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-white">{state.resume.name}</p>
            <p className="text-xs text-gray-500 mt-0.5">Target: <span className="text-accent">{title}</span></p>
          </div>
          <div className="badge-green">Resume Loaded ✅</div>
        </div>
      )}

      {error && <Alert type="error" message={error} />}

      <button className="btn-primary mb-8" onClick={handleStrategy} disabled={loading}>
        {loading ? <Spinner size={14} /> : <Zap size={14} />}
        {loading ? 'Building strategy…' : '🤖 Generate Search Strategy'}
      </button>

      {/* Strategy output */}
      {strategy && (
        <>
          {/* LinkedIn CTA */}
          {strategy.linkedin_search_url && (
            <div className="card mb-5 flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-white mb-0.5">🔗 LinkedIn Job Search</p>
                <p className="text-xs text-gray-500 font-mono truncate max-w-md">{strategy.linkedin_search_url}</p>
              </div>
              <a
                href={strategy.linkedin_search_url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary shrink-0"
              >
                <ExternalLink size={13} />
                Open LinkedIn
              </a>
            </div>
          )}

          <div className="grid lg:grid-cols-2 gap-5 mb-5">
            <div className="card">
              <p className="section-title">📋 Alternative Job Titles</p>
              <Pills items={strategy.alternative_job_titles ?? []} variant="accent" />
            </div>
            <div className="card">
              <p className="section-title">🔎 Recommended Search Terms</p>
              <Pills items={strategy.recommended_search_terms ?? []} />
            </div>
          </div>

          {/* Salary */}
          {strategy.salary_range && (
            <div className="card mb-5">
              <p className="section-title">💰 Estimated Salary Range</p>
              <div className="grid grid-cols-3 gap-4 text-center">
                {[['India', strategy.salary_range.india_lpa], ['USA', strategy.salary_range.us_usd], ['UK', strategy.salary_range.uk_gbp]].map(([region, val]) => (
                  <div key={region} className="bg-dark-800 rounded-lg py-3">
                    <div className="text-lg font-bold text-accent font-mono">{val || 'N/A'}</div>
                    <div className="text-xs text-gray-500">{region}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Companies */}
          {strategy.top_companies_to_target?.length > 0 && (
            <div className="card mb-5">
              <p className="section-title">🏢 Top Companies to Target</p>
              <div className="grid lg:grid-cols-2 gap-3">
                {strategy.top_companies_to_target.map((co, i) => (
                  <div key={i} className="bg-dark-800 rounded-lg p-3 border border-dark-500">
                    <p className="text-sm font-medium text-white">{co.name}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{co.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tips + Certs */}
          <div className="grid lg:grid-cols-2 gap-5 mb-8">
            {strategy.search_tips?.length > 0 && (
              <div className="card">
                <p className="section-title">💡 Search Tips</p>
                <ul className="space-y-1">
                  {strategy.search_tips.map((t, i) => <li key={i} className="text-xs text-gray-400">• {t}</li>)}
                </ul>
              </div>
            )}
            {strategy.certifications_to_boost_profile?.length > 0 && (
              <div className="card">
                <p className="section-title">🏅 Certs to Boost Your Profile</p>
                <Pills items={strategy.certifications_to_boost_profile} variant="accent" />
              </div>
            )}
          </div>
        </>
      )}

      {/* Quick ATS scan */}
      <div className="card border-t border-dark-500 pt-5">
        <h2 className="text-sm font-semibold text-white mb-1">⚡ Quick ATS Check</h2>
        <p className="text-xs text-gray-500 mb-4">Paste any job posting to instantly score your resume against it.</p>
        <textarea
          className="textarea mb-3"
          rows={5}
          placeholder="Paste a full job description here…"
          value={jd}
          onChange={e => setJd(e.target.value)}
        />
        <button className="btn-secondary mb-4" onClick={handleQuickScan} disabled={scanLoading}>
          {scanLoading ? <Spinner size={13} /> : <Zap size={13} />}
          {scanLoading ? 'Scanning…' : 'Quick Scan'}
        </button>

        {quickResult && (
          <div className="grid lg:grid-cols-2 gap-4">
            <div className="bg-dark-800 rounded-lg p-4 text-center border border-dark-500">
              <div className="text-3xl font-bold font-mono text-accent">{quickResult.overall_score}%</div>
              <div className="text-xs text-gray-400 mt-1">{quickResult.verdict}</div>
            </div>
            <div>
              <p className="text-xs font-medium text-red-400 mb-2">Missing Keywords</p>
              <Pills items={(quickResult.missing_keywords ?? []).slice(0, 10)} variant="red" />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
