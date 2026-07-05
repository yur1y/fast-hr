import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Scan, Bug, Users, Briefcase, ClipboardList, ArrowRight, ChevronDown } from 'lucide-react'

type Endpoint = {
  method: string
  path: string
  description: string
}

const ENDPOINTS: Endpoint[] = [
  { method: 'GET', path: '/api/v1/health', description: 'Root health check' },
  { method: 'POST', path: '/api/v1/screenings', description: 'Create a new screening' },
  { method: 'GET', path: '/api/v1/screenings', description: 'List screenings (paginated)' },
  { method: 'GET', path: '/api/v1/screenings/{screening_id}', description: 'Get screening by ID (or all)' },
  { method: 'GET', path: '/api/v1/screenings/{screening_id}/trace', description: 'Redirect to observability trace' },
  { method: 'POST', path: '/api/v1/fuzzer/run', description: 'Run fuzzer synchronously' },
  { method: 'POST', path: '/api/v1/fuzzer/run-async', description: 'Queue fuzzer run in Celery' },
  { method: 'GET', path: '/api/v1/fuzzer/runs/{run_id}', description: 'Get fuzzer run result' },
  { method: 'GET', path: '/api/v1/fuzzer/badges', description: 'Get badge metrics for last fuzzer run' },
  { method: 'POST', path: '/api/v1/hr/batch', description: 'Run batch screening for multiple resumes' },
  { method: 'GET', path: '/api/v1/hr/dashboard', description: 'Get HR dashboard analytics' },
  { method: 'POST', path: '/api/v1/hr/compare', description: 'Compare candidate screenings' },
  { method: 'GET', path: '/api/v1/hr/reports/{screening_id}', description: 'Get screening report with trace URL' },
  { method: 'GET', path: '/api/v1/admin/analytics/dashboard', description: 'Get admin analytics dashboard data' },
  { method: 'GET', path: '/api/v1/admin/jobs', description: 'List all jobs' },
  { method: 'POST', path: '/api/v1/admin/jobs', description: 'Create a new job' },
  { method: 'PUT', path: '/api/v1/admin/jobs/{job_id}', description: 'Update a job' },
  { method: 'GET', path: '/api/v1/admin/candidates', description: 'List candidates (filterable)' },
  { method: 'POST', path: '/api/v1/admin/candidates/{candidate_id}/status', description: 'Update application status' },
  { method: 'POST', path: '/api/v1/admin/candidates/{candidate_id}/screen', description: 'Queue screening for candidate' },
  { method: 'GET', path: '/api/v1/admin/candidates/{candidate_id}', description: 'Get candidate detail with screening' },
  { method: 'GET', path: '/api/v1/careers/jobs', description: 'List active public jobs' },
  { method: 'GET', path: '/api/v1/careers/jobs/{job_id}', description: 'Get public job detail' },
  { method: 'POST', path: '/api/v1/careers/apply', description: 'Submit a job application (multipart form)' },
  { method: 'GET', path: '/api/v1/careers/status/{application_id}', description: 'Get application status' },
  { method: 'POST', path: '/api/v1/tasks/canary', description: 'Queue canary drift detection task' },
  { method: 'GET', path: '/api/v1/tasks/{task_id}', description: 'Get Celery background task status' },
]

const METHOD_COLORS: Record<string, string> = {
  GET: 'bg-emerald-50 text-emerald-700',
  POST: 'bg-blue-50 text-blue-700',
  PUT: 'bg-amber-50 text-amber-700',
}

const ACTIONS = [
  {
    title: 'Screen candidates',
    description: 'Evaluate resumes against job descriptions in seconds.',
    to: '/batch',
    icon: Scan,
  },
  {
    title: 'Run fuzzer',
    description: 'Detect deception patterns and resume inconsistencies.',
    to: '/fuzzer',
    icon: Bug,
  },
  {
    title: 'Compare candidates',
    description: 'Side-by-side fit scores, strengths, and risks.',
    to: '/compare',
    icon: Users,
  },
  {
    title: 'Careers portal',
    description: 'Open positions and job applications.',
    to: '/careers',
    icon: Briefcase,
  },
]

export function Dashboard() {
  const [health, setHealth] = useState<{ status: string; version?: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showEndpoints, setShowEndpoints] = useState(false)

  useEffect(() => {
    api
      .get('/health')
      .then((r) => setHealth(r.data))
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-2xl font-semibold text-brand-900">TracePilot</h1>
        <p className="mt-2 max-w-2xl text-sm text-brand-800">
          AI-powered screening and analytics for modern hiring. Screen candidates, detect
          inconsistencies, and make better decisions faster.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <Link to="/batch" className="btn-primary gap-2">
            Start screening <ArrowRight className="h-4 w-4" />
          </Link>
          <Link to="/screenings" className="btn-secondary gap-2">
            View screenings <ClipboardList className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {ACTIONS.map((action) => (
          <Link
            key={action.to}
            to={action.to}
            className="card hover:shadow-md transition-shadow"
          >
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700">
                <action.icon className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-semibold">{action.title}</div>
                <div className="mt-1 text-xs text-slate-600">{action.description}</div>
              </div>
            </div>
          </Link>
        ))}
      </section>

      <section className="card">
        <div className="card-body">
          <div className="flex items-center justify-between">
            <h2 className="section-title">API Health</h2>
            <button
              onClick={() =>
                api
                  .get('/health')
                  .then((r) => {
                    setHealth(r.data)
                    setError(null)
                  })
                  .catch((e) => setError(e.message))
              }
              className="btn-secondary text-xs"
            >
              Refresh
            </button>
          </div>
          <div className="mt-3 flex items-center gap-3">
            {health ? (
              <span className="inline-flex items-center rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                {health.status}
                {health.version ? ` · v${health.version}` : ''}
              </span>
            ) : null}
            {error ? <span className="text-xs text-red-600">{error}</span> : null}
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-body">
          <button
            onClick={() => setShowEndpoints(!showEndpoints)}
            className="flex w-full items-center justify-between section-title"
          >
            <span>Endpoints</span>
            <ChevronDown className={`h-5 w-5 transition-transform ${showEndpoints ? 'rotate-180' : ''}`} />
          </button>
          {showEndpoints && (
            <div className="mt-3 divide-y">
              {ENDPOINTS.map((ep) => (
                <div key={`${ep.method}-${ep.path}`} className="flex items-center gap-3 py-2">
                  <span
                    className={`rounded-md px-2 py-0.5 text-xs font-medium ${METHOD_COLORS[ep.method] || 'bg-slate-100 text-slate-700'}`}
                  >
                    {ep.method}
                  </span>
                  <code className="text-sm">{ep.path}</code>
                  <span className="text-xs text-slate-600">{ep.description}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
