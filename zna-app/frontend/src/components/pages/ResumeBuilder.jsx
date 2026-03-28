import { useState } from 'react'
import { Wand2, Download, FileText, Eye } from 'lucide-react'
import { useStore } from '../../lib/store'
import { api, downloadBlob } from '../../lib/api'
import { Spinner, Alert, ScoreBadge, Tabs, Divider } from '../ui'

const TEMPLATES = ['Standard Corporate', 'Modern Creative', 'Minimal Clean']
const MODES = [
  { id: 'auto',   label: '⚡ Auto-Parse (Paste LinkedIn / Resume Text)' },
  { id: 'manual', label: '✍️ Manual Entry' },
]

export default function ResumeBuilder() {
  const { state, dispatch } = useStore()

  const [mode, setMode]               = useState('auto')
  const [template, setTemplate]       = useState('Standard Corporate')
  const [rawText, setRawText]         = useState('')
  const [name, setName]               = useState('')
  const [email, setEmail]             = useState('')
  const [phone, setPhone]             = useState('')
  const [github, setGithub]           = useState('')
  const [linkedin, setLinkedin]       = useState('')
  const [targetTitle, setTargetTitle] = useState(state.targetJobTitle)
  const [loading, setLoading]         = useState(false)
  const [error, setError]             = useState('')
  const [activeTab, setActiveTab]     = useState('preview')
  const [pdfLoading, setPdfLoading]   = useState(false)

  async function handleGenerate() {
    if (!rawText.trim()) return setError('Please paste your resume / LinkedIn text.')
    if (!targetTitle.trim()) return setError('Please enter a Target Job Title.')
    setError(''); setLoading(true)
    try {
      const payload = {
        raw_text: rawText,
        target_job_title: targetTitle,
        template_style: template,
        ...(name     && { name }),
        ...(email    && { email }),
        ...(phone    && { phone }),
        ...(github   && { github }),
        ...(linkedin && { linkedin }),
      }
      const res = await api.resume.parseAndGenerate(payload)
      dispatch({ type: 'SET_PARSED', payload: res.data.parsed })
      dispatch({ type: 'SET_RESUME', payload: res.data.resume })
      dispatch({ type: 'SET_TARGET_TITLE', payload: targetTitle })
      setActiveTab('preview')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleDownloadPDF() {
    if (!state.resume) return
    setPdfLoading(true)
    try {
      const blob = await api.pdf.resume(state.resume, template)
      downloadBlob(blob, `${(state.resume.name ?? 'resume').replace(/ /g, '_')}_resume.pdf`)
    } catch (e) {
      setError(e.message)
    } finally {
      setPdfLoading(false)
    }
  }

  const resume = state.resume

  return (
    <div className="page">
      <h1 className="page-title">📄 Smart Resume Builder</h1>
      <p className="page-subtitle">Parse your background and generate a polished, ATS-optimised resume.</p>

      {/* ── Settings ── */}
      <div className="card mb-5">
        <h2 className="text-sm font-semibold text-white mb-3">⚙️ Template Settings</h2>
        <div className="grid grid-cols-3 gap-2">
          {TEMPLATES.map(t => (
            <button
              key={t}
              onClick={() => setTemplate(t)}
              className={`py-2 px-3 rounded-lg text-xs font-medium border transition-colors ${
                template === t
                  ? 'bg-accent/10 border-accent/40 text-accent'
                  : 'bg-dark-800 border-dark-500 text-gray-400 hover:border-gray-500'
              }`}
            >{t}</button>
          ))}
        </div>
      </div>

      {/* ── Input ── */}
      <div className="card mb-5">
        <h2 className="text-sm font-semibold text-white mb-4">📋 Data Input</h2>

        <div className="flex gap-4 mb-4">
          {MODES.map(m => (
            <label key={m.id} className="flex items-center gap-2 cursor-pointer text-sm text-gray-400 hover:text-gray-200">
              <input type="radio" checked={mode === m.id} onChange={() => setMode(m.id)} className="accent-accent" />
              {m.label}
            </label>
          ))}
        </div>

        {mode === 'auto' && (
          <div className="log-info mb-4">
            <span>💡 Fast-Import: Paste your entire LinkedIn profile or old resume. The AI extracts and organises it automatically.</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="label">Full Name</label>
            <input className="input" placeholder="e.g. Syed Zaid Karim" value={name} onChange={e => setName(e.target.value)} />
          </div>
          <div>
            <label className="label">Target Job Title *</label>
            <input className="input" placeholder="e.g. Software Engineer" value={targetTitle} onChange={e => setTargetTitle(e.target.value)} />
          </div>
          <div>
            <label className="label">Email</label>
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="label">Phone</label>
            <input className="input" value={phone} onChange={e => setPhone(e.target.value)} />
          </div>
          <div>
            <label className="label">GitHub URL</label>
            <input className="input" placeholder="https://github.com/..." value={github} onChange={e => setGithub(e.target.value)} />
          </div>
          <div>
            <label className="label">LinkedIn URL</label>
            <input className="input" placeholder="https://linkedin.com/in/..." value={linkedin} onChange={e => setLinkedin(e.target.value)} />
          </div>
        </div>

        <div>
          <label className="label">Raw Experience / Education / LinkedIn Data *</label>
          <textarea
            className="textarea"
            rows={mode === 'auto' ? 8 : 10}
            placeholder={mode === 'auto'
              ? 'Paste your LinkedIn profile text or old resume here…'
              : 'Describe your experience, education, skills, projects…'}
            value={rawText}
            onChange={e => setRawText(e.target.value)}
          />
        </div>

        {error && <Alert type="error" message={error} />}

        <button className="btn-primary mt-4" onClick={handleGenerate} disabled={loading}>
          {loading ? <Spinner size={14} /> : <Wand2 size={14} />}
          {loading ? 'Generating…' : '✨ Auto Generate AI Resume'}
        </button>
      </div>

      {/* ── Output ── */}
      {resume && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-white">2. AI Output & Export</h2>
            <div className="flex items-center gap-3">
              <ScoreBadge score={resume.ats_score ?? 0} />
              <button className="btn-primary" onClick={handleDownloadPDF} disabled={pdfLoading}>
                {pdfLoading ? <Spinner size={13} /> : <Download size={13} />}
                Download PDF
              </button>
            </div>
          </div>

          <Tabs
            tabs={[{ id: 'preview', label: '👁 Preview' }, { id: 'json', label: '{ } JSON' }]}
            active={activeTab}
            onChange={setActiveTab}
          />

          {activeTab === 'preview' && (
            <div className="bg-dark-800 rounded-lg p-6 text-sm space-y-4">
              <div>
                <h3 className="text-xl font-bold text-white">{resume.name}</h3>
                <p className="text-xs text-gray-500 mt-1">
                  {[resume.contact?.email, resume.contact?.phone, resume.contact?.github, resume.contact?.linkedin]
                    .filter(Boolean).join('  ·  ')}
                </p>
              </div>
              {resume.summary && (
                <div>
                  <p className="section-title">Summary</p>
                  <p className="text-gray-300 text-xs leading-relaxed">{resume.summary}</p>
                </div>
              )}
              {resume.skills?.technical?.length > 0 && (
                <div>
                  <p className="section-title">Technical Skills</p>
                  <p className="text-gray-400 text-xs">{resume.skills.technical.join(', ')}</p>
                </div>
              )}
              {resume.experience?.map((exp, i) => (
                <div key={i}>
                  {i === 0 && <p className="section-title">Experience</p>}
                  <div className="flex justify-between items-start">
                    <span className="text-white text-xs font-semibold">{exp.title} — {exp.company}</span>
                    <span className="text-gray-600 text-xs">{exp.duration}</span>
                  </div>
                  <ul className="mt-1 space-y-0.5">
                    {exp.bullets?.map((b, j) => <li key={j} className="text-gray-400 text-xs">• {b}</li>)}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'json' && (
            <pre className="bg-dark-800 rounded-lg p-4 text-xs text-green-400 font-mono overflow-auto max-h-96">
              {JSON.stringify(resume, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
