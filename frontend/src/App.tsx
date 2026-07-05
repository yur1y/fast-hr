import { useState } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import {
  Scan,
  Bug,
  ClipboardList,
  Users,
  Briefcase,
  UserSquare2,
  Menu,
  X,
  Activity,
} from 'lucide-react'
import { Dashboard } from './pages/Dashboard'
import { Screenings } from './pages/Screenings'
import { Fuzzer } from './pages/Fuzzer'
import { Tasks } from './pages/Tasks'
import { Batch } from './pages/Batch'
import { Compare } from './pages/Compare'
import { Report } from './pages/Report'
import { Careers } from './pages/Careers'
import { JobDetail } from './pages/JobDetail'
import { Apply } from './pages/Apply'
import { ApplicationStatus } from './pages/ApplicationStatus'
import { AdminDashboard } from './pages/AdminDashboard'
import { AdminCandidates } from './pages/AdminCandidates'
import { AdminJobs } from './pages/AdminJobs'
import { AdminApplications } from './pages/AdminApplications'
import { AdminApplicationDetail } from './pages/AdminApplicationDetail'
import { HrDashboard } from './pages/HrDashboard'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? 'text-brand-700 font-medium' : 'text-slate-600 hover:text-slate-900'

export function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <NavLink to="/" className="flex items-center gap-2 text-lg font-semibold text-brand-700">
            <Activity className="h-5 w-5" />
            <span>TracePilot</span>
          </NavLink>

          <button
            className="md:hidden p-2 text-slate-600"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <nav className="hidden md:flex gap-6 text-sm">
            <NavLink to="/careers" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><Briefcase className="h-4 w-4" /> Careers</span>
            </NavLink>
            <NavLink to="/batch" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><Scan className="h-4 w-4" /> Screen</span>
            </NavLink>
            <NavLink to="/compare" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> Compare</span>
            </NavLink>
            <NavLink to="/screenings" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><ClipboardList className="h-4 w-4" /> Screenings</span>
            </NavLink>
            <NavLink to="/fuzzer" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><Bug className="h-4 w-4" /> Fuzzer</span>
            </NavLink>
            <NavLink to="/hr" className={navLinkClass}>
              <span className="flex items-center gap-1.5"><ClipboardList className="h-4 w-4" /> HR</span>
            </NavLink>
             <div className="h-4 w-px bg-slate-200" />
             <NavLink to="/admin/applications" className={navLinkClass}>
               <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> Applications</span>
             </NavLink>
             <NavLink to="/admin" className={navLinkClass}>
               <span className="flex items-center gap-1.5"><UserSquare2 className="h-4 w-4" /> Admin</span>
             </NavLink>
          </nav>
        </div>

        {isMobileMenuOpen && (
          <nav className="md:hidden border-t px-4 py-3 flex flex-col gap-3 text-sm bg-white">
            <NavLink to="/careers" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><Briefcase className="h-4 w-4" /> Careers</span>
            </NavLink>
            <NavLink to="/batch" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><Scan className="h-4 w-4" /> Screen</span>
            </NavLink>
            <NavLink to="/compare" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> Compare</span>
            </NavLink>
            <NavLink to="/screenings" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><ClipboardList className="h-4 w-4" /> Screenings</span>
            </NavLink>
            <NavLink to="/fuzzer" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><Bug className="h-4 w-4" /> Fuzzer</span>
            </NavLink>
            <NavLink to="/hr" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
              <span className="flex items-center gap-1.5"><ClipboardList className="h-4 w-4" /> HR</span>
            </NavLink>
             <div className="h-px bg-slate-200" />
             <NavLink to="/admin/applications" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
               <span className="flex items-center gap-1.5"><Users className="h-4 w-4" /> Applications</span>
             </NavLink>
             <NavLink to="/admin" className={navLinkClass} onClick={() => setIsMobileMenuOpen(false)}>
               <span className="flex items-center gap-1.5"><UserSquare2 className="h-4 w-4" /> Admin</span>
             </NavLink>
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/batch" element={<Batch />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/reports/:id" element={<Report />} />
          <Route path="/screenings" element={<Screenings />} />
          <Route path="/fuzzer" element={<Fuzzer />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/careers" element={<Careers />} />
          <Route path="/careers/jobs/:id" element={<JobDetail />} />
          <Route path="/careers/apply/:job_id" element={<Apply />} />
          <Route path="/careers/status/:application_id" element={<ApplicationStatus />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/candidates" element={<AdminCandidates />} />
          <Route path="/admin/jobs" element={<AdminJobs />} />
          <Route path="/admin/applications" element={<AdminApplications />} />
          <Route path="/admin/applications/:id" element={<AdminApplicationDetail />} />
          <Route path="/hr" element={<HrDashboard />} />
        </Routes>
      </main>

      <footer className="border-t bg-white mt-8">
        <div className="mx-auto max-w-6xl px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <span> TracePilot — AI-powered candidate screening</span>
          <span>Built with FastAPI + React</span>
        </div>
      </footer>
    </div>
  )
}
