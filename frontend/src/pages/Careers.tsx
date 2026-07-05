import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

export function Careers() {
  const [jobs, setJobs] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get('/api/v1/careers/jobs').then((r) => setJobs(r.data)).catch((e) => setError(e.message))
  }, [])

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Careers</h1>
        <p className="mt-1 text-sm text-brand-800">
          Explore open positions and join the team building modern hiring infrastructure.
        </p>
      </section>

      <section className="card">
        <div className="card-body">
          <h2 className="section-title">Open positions</h2>
          {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
          <div className="mt-4 divide-y">
            {jobs.map((job) => (
              <div key={job.id} className="flex flex-col gap-3 py-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <Link to={`/careers/jobs/${job.id}`} className="text-sm font-medium text-brand-700 hover:underline">
                    {job.title}
                  </Link>
                  <div className="mt-1 text-xs text-slate-600">
                    {[job.department, job.location, job.salary_range].filter(Boolean).join(' · ')}
                  </div>
                </div>
                <Link to={`/careers/apply/${job.id}`} className="btn-primary text-xs justify-self-start md:justify-self-end">
                  Apply
                </Link>
              </div>
            ))}
            {jobs.length === 0 && !error ? (
              <p className="py-6 text-sm text-slate-600">No open positions right now.</p>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  )
}
