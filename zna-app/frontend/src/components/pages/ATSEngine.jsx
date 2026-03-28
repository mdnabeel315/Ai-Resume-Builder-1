import { useState } from 'react'
import { Search, Zap } from 'lucide-react'
import { useStore } from '../../lib/store'
import { api } from '../../lib/api'
import { Spinner, Alert, ScoreBar, Pills, EmptyState, Divider } from '../ui'

export default function ATSEngine() {
  const { state, dispatch } = useStore()
  const [jd, setJd]           = useState(state.jobDescription)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')

  const result = state.atsResult

  async function handleScan() {
    if (!state.resume) return setError('No resume loaded. Build your resume first.')
    if (!jd.trim())    return setError('Please paste a Job Description.')
    setError(''); setLoading(true)
    try {
      dispatch({ type: 'SET_JOB_DESCRIPTION', payload: jd })
      const res = await api.ats.scan(state.resume, jd)
      dispatch({ type: 'SET_ATS_RESULT', payload: res.data })
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">🔍 ATS Match Engine</h1>
      <p className="page-subtitle">Compare your resume against a real Job Description to find missing keywords before you apply.</p>

      <div className="grid lg:grid-cols-2 gap-5 mb-5">
        {/* Resume status */}
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-3">Your Active Resume</h2>
          {state.resume ? (
            <div>
              <div className="log-success mb-3">
                <span>✅ Loaded: <strong>{state.resume.name}</strong></span>
              </div>
              <p className="text-xs text-gray-500">
                Technical: {(state.resume.skills?.technical ?? []).slice(0, 6).join(', ')}
              </p>
            </div>
          ) : (
            <div className="log-warn">
              <span>⚠️ No resume loaded. Go to the Resume Builder first.</span>
            </div>
          )}
        </div>

        {/* JD input */}
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-3">Target Job Description</h2>
          <textarea
            className="textarea"
            rows={5}
            placeholder="Paste the full job requirements, skills, and responsibilities…"
            value={jd}
            onChange={e => setJd(e.target.value)}
          />
        </div>
      </div>

      {error && <Alert type="error" message={error} />}

      <button className="btn-primary mb-8" onClick={handleScan} disabled={loading}>
        {loading ? <Spinner size={14} /> : <Zap size={14} />}
        {loading ? 'Scanning…' : '🚀 Run Deep ATS Scan'}
      </button>

      {/* Results */}
      {result && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[
              { label: 'Overall Score',         value: result.overall_score },
              { label: 'Keyword Match',          value: result.breakdown?.keyword_match },
              { label: 'Skills Alignment',       value: result.breakdown?.skills_alignment },
              { label: 'Experience Relevance',   value: result.breakdown?.experience_relevance },
            ].map(({ label, value }) => (
              <div key={label} className="card text-center">
                <div className="text-2xl font-bold font-mono text-accent">{value ?? 0}%</div>
                <div className="text-xs text-gray-400 mt-0.5">{label}</div>
              </div>
            ))}
          </div>

          <div className="card mb-5">
            <div className="space-y-3">
              <ScoreBar label="Keyword Match"        score={result.breakdown?.keyword_match ?? 0} />
              <ScoreBar label="Skills Alignment"     score={result.breakdown?.skills_alignment ?? 0} />
              <ScoreBar label="Experience Relevance" score={result.breakdown?.experience_relevance ?? 0} />
              <ScoreBar label="Title Match"          score={result.breakdown?.title_match ?? 0} />
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-5 mb-5">
            <div className="card">
              <h3 className="text-sm font-semibold text-green-400 mb-3">✅ Matched Keywords</h3>
              <Pills items={result.matched_keywords ?? []} variant="green" />
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-red-400 mb-3">❌ Missing Keywords</h3>
              <Pills items={result.missing_keywords ?? []} variant="red" />
            </div>
          </div>

          {result.improvements?.length > 0 && (
            <div className="card mb-5">
              <h3 className="text-sm font-semibold text-white mb-4">💡 Improvement Suggestions</h3>
              <div className="space-y-3">
                {result.improvements.map((imp, i) => (
                  <div key={i} className="bg-dark-800 rounded-lg p-4 border border-dark-500">
                    <p className="text-xs font-semibold text-accent mb-1">📌 {imp.section}</p>
                    <p className="text-xs text-gray-400"><span className="text-gray-300">Issue:</span> {imp.issue}</p>
                    <p className="text-xs text-gray-400 mt-1"><span className="text-gray-300">Fix:</span> {imp.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.strengths?.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold text-white mb-3">💪 Strengths</h3>
              <ul className="space-y-1">
                {result.strengths.map((s, i) => (
                  <li key={i} className="text-xs text-gray-400">• {s}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {!result && !loading && (
        <EmptyState
          icon={Search}
          title="No scan run yet"
          body="Load your resume and paste a job description, then click Run Deep ATS Scan."
        />
      )}
    </div>
  )
}
