/**
 * ZNA API Client
 * All communication with the FastAPI backend lives here.
 * Vite proxies /api → http://localhost:8000 in dev.
 * In production, set VITE_API_URL in your env.
 */

const BASE = import.meta.env.VITE_API_URL ?? ''

async function request(method, path, body = null, isBlob = false) {
  const opts = {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    ...(body ? { body: JSON.stringify(body) } : {}),
  }
  const res = await fetch(`${BASE}${path}`, opts)

  if (isBlob) {
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Request failed' }))
      throw new Error(err.detail ?? err.error ?? 'Request failed')
    }
    return res.blob()
  }

  const json = await res.json()
  if (!res.ok) {
    throw new Error(json.detail ?? json.error ?? 'Request failed')
  }
  return json
}

const get  = (path)         => request('GET',  path)
const post = (path, body)   => request('POST', path, body)
const blob = (path, body)   => request('POST', path, body, true)

// ── Resume ────────────────────────────────────────────────────────────────────
export const api = {
  resume: {
    parse:            (rawText)              => post('/api/resume/parse', { raw_text: rawText }),
    generate:         (parsedData, title, style) =>
                      post('/api/resume/generate', { parsed_data: parsedData, target_job_title: title, template_style: style }),
    parseAndGenerate: (payload)              => post('/api/resume/parse-and-generate', payload),
  },

  // ── ATS ─────────────────────────────────────────────────────────────────────
  ats: {
    scan:     (resumeData, jobDescription) =>
              post('/api/ats/scan', { resume_data: resumeData, job_description: jobDescription }),
    keywords: (jobDescription)            =>
              post('/api/ats/keywords', { job_description: jobDescription }),
  },

  // ── Cover Letter ─────────────────────────────────────────────────────────────
  coverLetter: {
    generate: (resumeData, jobDescription, tone) =>
              post('/api/cover-letter/generate', { resume_data: resumeData, job_description: jobDescription, tone }),
  },

  // ── PDF ──────────────────────────────────────────────────────────────────────
  pdf: {
    resume:      (resumeData, templateStyle) =>
                 blob('/api/pdf/resume', { resume_data: resumeData, template_style: templateStyle }),
    coverLetter: (coverLetter)              =>
                 blob('/api/pdf/cover-letter', { cover_letter: coverLetter }),
  },

  // ── Jobs ─────────────────────────────────────────────────────────────────────
  jobs: {
    strategy: (targetJobTitle, skills) =>
              post('/api/jobs/strategy', { target_job_title: targetJobTitle, skills }),
  },

  // ── Health ───────────────────────────────────────────────────────────────────
  health: () => get('/health'),
}

/** Download a PDF blob and trigger browser save dialog. */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
