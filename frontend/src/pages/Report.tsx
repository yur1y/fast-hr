import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { ExternalLink } from 'lucide-react'

export function Report() {
  const { id } = useParams<{ id: string }>()
  const [reportUrl, setReportUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    setReportUrl(`/api/v1/hr/reports/${id}`)
    api.get(`/api/v1/hr/reports/${id}`).catch((e) => setError(e.message))
  }, [id])

  if (!id) {
    return <div className="text-sm text-slate-600">No screening ID provided.</div>
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Report</h1>
        <p className="mt-1 text-sm text-brand-800">View screening report for candidate evaluation.</p>
      </div>

      <section className="card">
        <div className="card-body">
          <h2 className="section-title">Screening report</h2>
          <p className="mt-1 text-sm text-slate-600">
            Screening ID: <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">{id}</code>
          </p>
          <div className="mt-4">
            <a
              className="btn-secondary gap-2"
              href={reportUrl || '#'}
              target="_blank"
              rel="noreferrer"
            >
              <ExternalLink className="h-4 w-4" /> Open HTML report
            </a>
          </div>
          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        </div>
      </section>
    </div>
  )
}
