import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Activity, TrendingUp, BarChart3 } from 'lucide-react'

export function HrDashboard() {
  const [metrics, setMetrics] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .get('/api/v1/hr/dashboard')
      .then((r) => setMetrics(r.data))
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">HR Dashboard</h1>
        <p className="mt-1 text-sm text-brand-800">Screening outcomes and candidate quality analytics.</p>
      </div>

      {error ? (
        <div className="card"><div className="card-body text-sm text-red-600">{error}</div></div>
      ) : null}

      {metrics ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><Activity className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Total screenings</div>
                <div className="text-xl font-semibold">{metrics.total_screenings ?? '-'}</div>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><TrendingUp className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Avg fit score</div>
                <div className="text-xl font-semibold">{metrics.avg_fit_score ?? '-'}</div>
              </div>
            </div>
          </div>
          <div className="card">
            <div className="card-body flex items-start gap-3">
              <div className="rounded-lg bg-brand-50 p-2 text-brand-700"><BarChart3 className="h-5 w-5" /></div>
              <div>
                <div className="text-xs text-slate-500">Avg confidence</div>
                <div className="text-xl font-semibold">{metrics.avg_confidence ?? '-'}</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {metrics?.top_candidates?.length ? (
        <section className="card">
          <div className="card-body">
            <h3 className="section-title">Top candidates</h3>
            <div className="mt-4 divide-y">
              {metrics.top_candidates.map((c: any) => (
                <div key={c.id} className="flex items-center justify-between py-3">
                  <div>
                    <div className="text-sm font-medium text-brand-700">{c.id}</div>
                    <div className="text-xs text-slate-600">{c.candidate_summary}</div>
                  </div>
                  <div className="text-sm font-semibold">{c.fit_score}</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {metrics?.risk_distribution && Object.keys(metrics.risk_distribution).length > 0 && (
        <section className="card">
          <div className="card-body">
            <h3 className="section-title">Risk distribution</h3>
            <div className="mt-4 flex flex-wrap gap-2">
              {Object.entries(metrics.risk_distribution).map(([risk, count]: any) => (
                <span key={risk} className="rounded-lg border border-slate-200 px-3 py-1.5 text-xs">
                  <span className="font-medium">{risk}</span> <span className="text-slate-600">: {count}</span>
                </span>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
