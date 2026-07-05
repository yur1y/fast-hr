import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Briefcase, MapPin, DollarSign } from 'lucide-react'

export function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const [job, setJob] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api.get(`/api/v1/careers/jobs/${id}`).then((r) => setJob(r.data)).catch((e) => setError(e.message))
  }, [id])

  if (!id) return <div className="text-sm text-slate-600">No job ID provided.</div>

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-xl font-semibold text-brand-900">{job?.title || 'Loading...'}</h1>
            {job && (
              <div className="mt-2 flex flex-wrap gap-3 text-xs text-brand-800">
                {job.department && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-brand-100 px-2 py-1">
                    <Briefcase className="h-3 w-3" /> {job.department}
                  </span>
                )}
                {job.location && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-brand-100 px-2 py-1">
                    <MapPin className="h-3 w-3" /> {job.location}
                  </span>
                )}
                {job.salary_range && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-brand-100 px-2 py-1">
                    <DollarSign className="h-3 w-3" /> {job.salary_range}
                  </span>
                )}
              </div>
            )}
          </div>
          {job && (
            <div className="flex gap-2">
              <Link to={`/careers/apply/${id}`} className="btn-primary">Apply now</Link>
              <Link to="/careers" className="btn-secondary">Back</Link>
            </div>
          )}
        </div>
      </div>

      {error ? (
        <div className="card"><div className="card-body text-sm text-red-600">{error}</div></div>
      ) : null}

      {job ? (
        <section className="card">
          <div className="card-body space-y-4">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">Description</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
                {job.description}
              </p>
            </div>
            {job.requirements ? (
              <div>
                <h2 className="text-sm font-semibold text-slate-900">Requirements</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
                  {job.requirements}
                </p>
              </div>
            ) : null}
          </div>
        </section>
      ) : null}
    </div>
  )
}
