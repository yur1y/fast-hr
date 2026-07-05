import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'

export function ApplicationStatus() {
  const { application_id } = useParams<{ application_id: string }>()
  const [status, setStatus] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!application_id) return
    api.get(`/api/v1/careers/status/${application_id}`).then((r) => setStatus(r.data)).catch((e) => setError(e.message))
  }, [application_id])

  if (!application_id) return <div className="text-sm text-slate-600">No application ID provided.</div>

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Application status</h1>
        <p className="mt-1 text-sm text-brand-800">Track your application progress.</p>
      </div>

      {error ? (
        <div className="card"><div className="card-body text-sm text-red-600">{error}</div></div>
      ) : null}

      {status ? (
        <section className="card">
          <div className="card-body space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <div className="text-xs text-slate-500">Application ID</div>
                <div className="mt-1 text-sm font-medium">{status.application_id || status.id}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Candidate</div>
                <div className="mt-1 text-sm font-medium">{status.candidate_name}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Status</div>
                <div className="mt-1">
                  <span className="inline-flex items-center rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700 capitalize">
                    {status.status}
                  </span>
                </div>
              </div>
            </div>

            {(status.fit_score != null || status.confidence != null) && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {status.fit_score != null && (
                  <div>
                    <div className="flex justify-between text-xs text-slate-600">
                      <span>Fit Score</span>
                      <span>{Math.round((status.fit_score || 0) * 100)}%</span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full bg-brand-500" style={{ width: `${Math.round((status.fit_score || 0) * 100)}%` }} />
                    </div>
                  </div>
                )}
                {status.confidence != null && (
                  <div>
                    <div className="flex justify-between text-xs text-slate-600">
                      <span>Confidence</span>
                      <span>{Math.round((status.confidence || 0) * 100)}%</span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-slate-100">
                      <div className="h-2 rounded-full bg-brand-500" style={{ width: `${Math.round((status.confidence || 0) * 100)}%` }} />
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  )
}
