# ZNA AI Studio — Full-Stack Career Workspace

AI-powered resume builder, ATS scanner, cover letter generator, and job portal.

**Stack:** FastAPI · Gemini 2.0 Flash · ReportLab · React 18 · Vite · Tailwind CSS

---

## 🗂 Project Structure

```
zna-app/
├── .github/workflows/ci.yml   # GitHub Actions CI
├── .gitignore
├── Procfile                   # Railway / Render deploy
│
├── backend/
│   ├── main.py                # FastAPI app, middleware, routes
│   ├── config.py              # Centralised settings (pydantic-settings)
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   ├── llm_service.py     # Gemini + retry + TTL cache
│   │   ├── resume_service.py  # Parse + generate resume
│   │   ├── ats_service.py     # 4-dimension ATS scoring
│   │   ├── cover_letter_service.py
│   │   └── pdf_service.py     # ReportLab PDF (3 themes)
│   ├── routes/
│   │   ├── resume.py
│   │   ├── ats.py
│   │   ├── cover_letter.py
│   │   ├── pdf.py
│   │   └── jobs.py
│   └── utils/
│       └── models.py          # Pydantic request/response models
│
└── frontend/
    ├── index.html
    ├── vite.config.js         # Proxies /api → localhost:8000 in dev
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── package.json
    └── src/
        ├── main.jsx
        ├── App.jsx            # Router + StoreProvider
        ├── lib/
        │   ├── store.jsx      # Global state (React Context + useReducer)
        │   └── api.js         # All API calls in one place
        ├── styles/
        │   └── globals.css    # Tailwind + custom component classes
        └── components/
            ├── ui/index.jsx   # Shared UI components
            ├── layout/
            │   └── Sidebar.jsx
            └── pages/
                ├── Dashboard.jsx
                ├── ResumeBuilder.jsx
                ├── ATSEngine.jsx
                ├── CoverLetter.jsx
                └── JobPortal.jsx
```

---

## 🚀 Local Development

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
uvicorn main:app --reload --port 8000
# API docs → http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

Vite proxies all `/api/*` calls to `http://localhost:8000` — no CORS issues in dev.

---

## ☁️ Deployment

### Backend → Railway / Render

1. Push repo to GitHub
2. Create a new Railway / Render **Web Service**, point to the repo
3. Set **Root Directory** to `backend`
4. Set **Start Command** to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `GEMINI_API_KEY=your_key_here`

### Frontend → Vercel / Netlify

1. Connect GitHub repo to Vercel
2. Set **Root Directory** to `frontend`
3. Set **Build Command** to: `npm run build`
4. Set **Output Directory** to: `dist`
5. Add environment variable: `VITE_API_URL=https://your-backend.railway.app`

---

## 🔑 Environment Variables

### Backend (`backend/.env`)
```env
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=production
FRONTEND_URL=https://your-frontend.vercel.app
```

### Frontend (`frontend/.env.local`)
```env
VITE_API_URL=https://your-backend.railway.app
```
*(Leave empty for local dev — Vite proxy handles it)*

---

## 📡 API Reference

| Method | Endpoint                      | Description                        |
|--------|-------------------------------|------------------------------------|
| GET    | /health                       | Health check                       |
| POST   | /api/resume/parse             | Parse raw text → structured JSON   |
| POST   | /api/resume/generate          | Generate polished resume           |
| POST   | /api/resume/parse-and-generate| Full pipeline (one call)           |
| POST   | /api/ats/scan                 | Deep ATS scan with breakdown       |
| POST   | /api/ats/keywords             | Extract keywords from JD           |
| POST   | /api/cover-letter/generate    | Generate tailored cover letter     |
| POST   | /api/pdf/resume               | Resume → PDF download              |
| POST   | /api/pdf/cover-letter         | Cover letter → PDF download        |
| POST   | /api/jobs/strategy            | AI LinkedIn search strategy        |

Interactive docs: `http://localhost:8000/docs`

---

## 🐙 GitHub Secrets Required

Add these in **GitHub → Settings → Secrets → Actions**:

| Secret          | Value                  |
|-----------------|------------------------|
| `GEMINI_API_KEY`| Your Gemini API key    |
