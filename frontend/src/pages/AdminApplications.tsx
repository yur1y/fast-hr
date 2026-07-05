import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'

export function AdminApplications() {
  const [apps, setApps] = useState<any[]>([])
  const [jobs, setJobs] = useState<any[]>([])
  const [jobFilter, setJobFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [running, setRunning] = useState<string | null>(null)

  const loadJobs = () => {
    api.get('/api/v1/admin/jobs').then((r) => setJobs(r.data)).catch(() => {})
  }

  const loadApps = () => {
    const params = new URLSearchParams()
    if (jobFilter) params.set('job_id', jobFilter)
    if (statusFilter) params.set('status', statusFilter)
    api.get(`/api/v1/admin/candidates?${params.toString()}`)
      .then((r) => setApps(r.data))
      .catch((e) => setError(e.message))
  }

  useEffect(() => {
    loadJobs()
  }, [])

  useEffect(() => {
    loadApps()
  }, [jobFilter, statusFilter])

  const updateStatus = async (id: string, status: string) => {
    try {
      await api.post(`/api/v1/admin/candidates/${id}/status`, { status })
      loadApps()
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    }
  }

  const runScreening = async (id: string) => {
    try {
      setRunning(id)
      await api.post(`/api/v1/admin/candidates/${id}/screen`)
      loadApps()
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    } finally {
      setRunning(null)
    }
  }

  const jobMap = Object.fromEntries(jobs.map((j) => [j.id, j.title]))

  const statusColor: Record<string, string> = {
    new: 'bg-slate-100 text-slate-700',
    screening: 'bg-blue-50 text-blue-700',
    interview: 'bg-purple-50 text-purple-700',
    offer: 'bg-emerald-50 text-emerald-700',
    hired: 'bg-emerald-100 text-emerald-800',
    rejected: 'bg-red-50 text-red-700',
    screening_failed: 'bg-red-50 text-red-700',
  }

  return (
    <div className="space-y-6">
      <section className="card">
        <div className="card-body">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 className="section-title">Applications</h2>
              <p className="mt-1 text-xs text-slate-600">Review candidates and manage hiring stages.</p>
            </div>
            <div className="flex flex-wrap gap-2">
              <select className="rounded-lg border border-slate-200 p-2 text-sm" value={jobFilter} onChange={(e) => setJobFilter(e.target.value)}>
                <option value="">All jobs</option>
                {jobs.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.title}
                  </option>
                ))}
              </select>
              <select className="rounded-lg border border-slate-200 p-2 text-sm" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                <option value="">All statuses</option>
                <option value="new">New</option>
                <option value="screening">Screening</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="hired">Hired</option>
                <option value="rejected">Rejected</option>
                <option value="screening_failed">Screening Failed</option>
              </select>
            </div>
          </div>
          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
          <div className="mt-4 overflow-auto">
            <div className="min-w-full divide-y">
              <div className="grid grid-cols-12 gap-4 py-2 text-xs font-medium text-slate-500">
                <div className="col-span-3">Candidate</div>
                <div className="col-span-3">Job</div>
                <div className="col-span-3">Email</div>
                <div className="col-span-3">Actions</div>
              </div>
              {apps.map((app) => (
                <div key={app.id} className="grid grid-cols-12 gap-4 items-center py-3">
                  <div className="col-span-3">
                    <div className="text-sm font-medium">{app.candidate_name}</div>
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${statusColor[app.status] || 'bg-slate-100 text-slate-700'}`}>
                      {app.status}
                    </span>
                  </div>
                  <div className="col-span-3 text-sm text-slate-600">{jobMap[app.job_id] || app.job_id}</div>
                  <div className="col-span-3 text-sm text-slate-600">{app.candidate_email}</div>
                  <div className="col-span-3 flex flex-wrap gap-2">
                    <Link to={`/admin/applications/${app.id}`} className="text-xs font-medium text-brand-700 hover:underline">
                      View
                    </Link>
                    <button
                      onClick={() => runScreening(app.id)}
                      disabled={running === app.id}
                      className="text-xs font-medium text-brand-700 hover:underline disabled:opacity-50"
                    >
                      {running === app.id ? 'Running...' : 'Run Screening'}
                    </button>
                    <select
                      className="rounded-md border border-slate-200 p-1 text-xs"
                      value={app.status}
                      onChange={(e) => updateStatus(app.id, e.target.value)}
                    >
                      <option value="new">New</option>
                      <option value="screening">Screening</option>
                      <option value="interview">Interview</option>
                      <option value="offer">Offer</option>
                      <option value="hired">Hired</option>
                      <option value="rejected">Rejected</option>
                      <option value="screening_failed">Screening Failed</option>
                    </select>
                  </div>
                </div>
              ))}
              {apps.length === 0 && <p className="py-6 text-sm text-slate-600">No applications yet.</p>}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
