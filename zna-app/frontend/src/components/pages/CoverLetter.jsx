import { useState } from 'react'
import { Wand2, Download, Copy, Check } from 'lucide-react'
import { useStore } from '../../lib/store'
import { api, downloadBlob } from '../../lib/api'
import { Spinner, Alert, EmptyState } from '../ui'
import { Mail } from 'lucide-react'

const TONES = ['Professional', 'Enthusiastic', 'Concise']
const TONE_DESC = {
  Professional:  'Formal, confident, achievement-driven.',
  Enthusiastic:  'Warm, energetic, shows personality.',
  Concise:       '3 tight paragraphs — no filler.',
}

export default function CoverLetter() {
  const { state, dispatch } = useStore()
  const [jd, setJd]               = useState(state.jobDescription)
  const [tone, setTone]           = useState('Professional')
  const [loading, setLoading]     = useState(false)
  const [pdfLoading, setPdfLoading] = useState(false)
  const [error, setError]         = useState('')
  const [copied, setCopied]       = useState(false)
  const [editedText, setEditedText] = useState('')

  const cl = state.coverLetter
  const displayText = editedText || cl?.text || ''

  async function handleGenerate() {
    if (!state.resume) return setError('No resume loaded. Build your resume first.')
    if (!jd.trim())    return setError('Please paste a Job Description.')
    setError(''); setLoading(true)
    try {
      dispatch({ type: 'SET_JOB_DESCRIPTION', payload: jd })
      const res = await api.coverLetter.generate(state.resume, jd, tone)
      dispatch({ type: 'SET_COVER_LETTER', payload: res.data })
      setEditedText('')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleDownloadPDF() {
    if (!cl) return
    setPdfLoading(true)
    try {
      const payload = { ...cl, text: displayText }
      const b = await api.pdf.coverLetter(payload)
      downloadBlob(b, 'cover_letter.pdf')
    } catch (e) {
      setError(e.message)
    } finally {
      setPdfLoading(false)
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(displayText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function downloadTxt() {
    const blob = new Blob([displayText], { type: 'text/plain' })
    downloadBlob(blob, 'cover_letter.txt')
  }

  return (
    <div className="page">
      <h1 className="page-title">✉️ Auto-Cover Letter</h1>
      <p className="page-subtitle">Generate a highly personalised cover letter based on your resume and the job description.</p>

      {!state.resume && (
        <div className="log-warn mb-5">
          <span>⚠️ No resume found. Please build your resume in the <strong>Smart Resume Builder</strong> first so the AI knows your background.</span>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-5 mb-5">
        <div className="lg:col-span-2 card">
          <label className="label">Target Job Description</label>
          <textarea
            className="textarea"
            rows={7}
            placeholder="Paste the job description here for a fully tailored letter…"
            value={jd}
            onChange={e => setJd(e.target.value)}
          />
        </div>
        <div className="card">
          <label className="label">Letter Tone</label>
          <div className="space-y-2">
            {TONES.map(t => (
              <label key={t} className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                tone === t ? 'border-accent/40 bg-accent/5' : 'border-dark-500 hover:border-dark-400'
              }`}>
                <input type="radio" checked={tone === t} onChange={() => setTone(t)} className="mt-0.5 accent-accent" />
                <div>
                  <div className="text-sm font-medium text-gray-200">{t}</div>
                  <div className="text-xs text-gray-500">{TONE_DESC[t]}</div>
                </div>
              </label>
            ))}
          </div>
        </div>
      </div>

      {error && <Alert type="error" message={error} />}

      <button className="btn-primary mb-8" onClick={handleGenerate} disabled={loading || !state.resume}>
        {loading ? <Spinner size={14} /> : <Wand2 size={14} />}
        {loading ? 'Crafting…' : '✨ Generate Cover Letter'}
      </button>

      {/* Output */}
      {cl && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">📝 Your Cover Letter</h2>
              <p className="text-xs text-gray-500 mt-0.5">{cl.word_count} words · {cl.tone} · {cl.date}</p>
            </div>
            <div className="flex items-center gap-2">
              <button className="btn-ghost" onClick={handleCopy}>
                {copied ? <Check size={13} className="text-green-400" /> : <Copy size={13} />}
                {copied ? 'Copied!' : 'Copy'}
              </button>
              <button className="btn-secondary" onClick={downloadTxt}>
                <Download size={13} /> .txt
              </button>
              <button className="btn-primary" onClick={handleDownloadPDF} disabled={pdfLoading}>
                {pdfLoading ? <Spinner size={13} /> : <Download size={13} />}
                PDF
              </button>
            </div>
          </div>
          <textarea
            className="textarea font-mono text-xs leading-relaxed"
            rows={18}
            value={displayText}
            onChange={e => setEditedText(e.target.value)}
          />
          <p className="text-xs text-gray-600 mt-2">You can edit the letter above before downloading.</p>
        </div>
      )}

      {!cl && !loading && (
        <EmptyState
          icon={Mail}
          title="No cover letter yet"
          body="Load your resume and paste a job description, then click Generate."
        />
      )}
    </div>
  )
}
