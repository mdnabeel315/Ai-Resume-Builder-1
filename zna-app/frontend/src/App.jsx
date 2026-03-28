import { Routes, Route } from 'react-router-dom'
import { StoreProvider } from './lib/store'
import Sidebar from './components/layout/Sidebar'
import Dashboard from './components/pages/Dashboard'
import ResumeBuilder from './components/pages/ResumeBuilder'
import CoverLetter from './components/pages/CoverLetter'
import ATSEngine from './components/pages/ATSEngine'
import JobPortal from './components/pages/JobPortal'

export default function App() {
  return (
    <StoreProvider>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/"             element={<Dashboard />} />
            <Route path="/resume"       element={<ResumeBuilder />} />
            <Route path="/cover-letter" element={<CoverLetter />} />
            <Route path="/ats"          element={<ATSEngine />} />
            <Route path="/jobs"         element={<JobPortal />} />
          </Routes>
        </main>
      </div>
    </StoreProvider>
  )
}
