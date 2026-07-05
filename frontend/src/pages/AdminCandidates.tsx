import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Link } from 'react-router-dom'

export function AdminCandidates() {
  const [candidates, setCandidates] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get('/api/v1/admin/candidates').then((r) => setCandidates(r.data)).catch((e) => setError(e.message))
  }, [])

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
          <h2 className="section-title">Candidates</h2>
          <p className="mt-1 text-xs text-slate-600">All candidates across jobs.</p>
          {error ? <p className="mt-2 text-sm text-red-600">{error}</p> : null}
          <div className="mt-4 divide-y">
            {candidates.map((c) => (
              <Link to={`/admin/applications/${c.id}`} key={c.id} className="flex items-center justify-between py-3 hover:bg-slate-50 -mx-5 px-5 rounded-lg transition-colors">
                <div>
                  <div className="text-sm font-medium text-brand-700">{c.candidate_name}</div>
                  <div className="text-xs text-slate-600">{c.candidate_email}</div>
                </div>
                <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColor[c.status] || 'bg-slate-100 text-slate-700'}`}>
                  {c.status}
                </span>
              </Link>
            ))}
            {candidates.length === 0 && !error ? (
              <p className="py-6 text-sm text-slate-600">No candidates yet.</p>
            ) : null}
          </div>
        </div>
      </section>
    </div>
  )
}
