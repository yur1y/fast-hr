import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'
import { Users, Briefcase, TrendingUp, Plus } from 'lucide-react'

export function AdminDashboard() {
  const [data, setData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get('/api/v1/admin/analytics/dashboard').then((r) => setData(r.data)).catch((e) => setError(e.message))
  }, [])

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-brand-800">Overview of jobs, candidates, and screening performance.</p>
      </div>

      {error ? (
        <div className="card"><div className="card-body text-sm text-red-600">{error}</div></div>
      ) : null}

      {data ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><Briefcase className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Jobs</div>
                <div className="text-xl font-semibold">{data.active_jobs || 0} active / {data.total_jobs || 0} total</div>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><Users className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Candidates</div>
                <div className="text-xl font-semibold">{data.total_candidates || 0}</div>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><TrendingUp className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Avg fit score</div>
                <div className="text-xl font-semibold">{data.average_fit_score ?? '-'}</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      <section className="card">
        <div className="card-body flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 className="section-title">Job openings</h2>
            <p className="mt-1 text-xs text-slate-600">Create and manage job postings.</p>
          </div>
          <Link to="/admin/jobs" className="btn-primary"><Plus className="h-4 w-4" /> Add new job</Link>
        </div>
      </section>
    </div>
  )
}
