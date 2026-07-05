import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import { ArrowLeft, ExternalLink } from 'lucide-react'

export function AdminApplicationDetail() {
  const { id } = useParams<{ id: string }>()
  const [app, setApp] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    api.get(`/api/v1/admin/candidates/${id}`)
      .then((r) => setApp(r.data))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="card"><div className="card-body text-center text-sm text-slate-500">Loading application...</div></div>
    )
  }

  if (error || !app) {
    return (
      <div className="card"><div className="card-body text-center text-sm text-red-600">{error || 'Application not found'}</div></div>
    )
  }

  const screening = app.screening
  const ensureProtocol = (url?: string) => {
    if (!url) return null
    return /^https?:\/\//i.test(url) ? url : `https://${url}`
  }
  const linkedinUrl = ensureProtocol(app.linkedin_url)
  const traceUrl = screening?.trace_url || null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/admin/applications" className="inline-flex items-center gap-1 text-sm text-slate-600 hover:text-brand-700">
          <ArrowLeft className="h-4 w-4" /> Applications
        </Link>
      </div>

      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-brand-900">{app.candidate_name}</h1>
            <p className="mt-1 text-sm text-brand-800">{app.job_title || 'Unknown job'}</p>
          </div>
          <span className="inline-flex w-fit items-center rounded-full border border-brand-200 bg-white px-3 py-1 text-xs font-medium text-brand-700 capitalize">
            {app.status}
          </span>
        </div>
      </div>

      <section className="card">
        <div className="card-body space-y-5">
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div className="rounded-xl border border-slate-100 p-4">
              <h3 className="text-sm font-semibold text-slate-900">Candidate</h3>
              <dl className="mt-3 space-y-3 text-sm">
                <div className="flex items-start justify-between gap-3">
                  <dt className="text-xs text-slate-500">Email</dt>
                  <dd>
                    {app.candidate_email ? (
                      <a href={`mailto:${app.candidate_email}`} className="text-brand-700 hover:underline">{app.candidate_email}</a>
                    ) : '—'}
                  </dd>
                </div>
                <div className="flex items-start justify-between gap-3">
                  <dt className="text-xs text-slate-500">LinkedIn</dt>
                  <dd>
                    {linkedinUrl ? (
                      <a href={linkedinUrl} target="_blank" rel="noreferrer" className="text-brand-700 hover:underline">
                        View profile <ExternalLink className="inline h-3 w-3" />
                      </a>
                    ) : '—'}
                  </dd>
                </div>
                <div className="flex items-start justify-between gap-3">
                  <dt className="text-xs text-slate-500">Applied</dt>
                  <dd className="text-right text-xs text-slate-600">{app.created_at ? new Date(app.created_at).toLocaleString() : '—'}</dd>
                </div>
              </dl>
            </div>

            <div className="rounded-xl border border-slate-100 p-4">
              <h3 className="text-sm font-semibold text-slate-900">Cover Letter</h3>
              <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                {app.cover_letter || 'No cover letter provided.'}
              </p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-100 p-4">
            <h3 className="text-sm font-semibold text-slate-900">Resume</h3>
            <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-slate-50 p-3 text-xs font-mono text-slate-700">
              {app.resume_text}
            </pre>
          </div>
        </div>
      </section>

      {screening && (
        <section className="card">
          <div className="card-body space-y-5">
            <h3 className="text-lg font-semibold">Screening Result</h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-slate-100 p-4">
                <h4 className="text-sm font-semibold text-slate-900">Scores</h4>
                <dl className="mt-3 space-y-3 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-xs text-slate-500">Fit score</dt>
                    <dd className="font-mono text-xs">{(screening.fit_score * 100).toFixed(0)}%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-xs text-slate-500">Confidence</dt>
                    <dd className="font-mono text-xs">{(screening.confidence * 100).toFixed(0)}%</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-xs text-slate-500">Processing time</dt>
                    <dd className="font-mono text-xs">{screening.processing_time_ms ? `${screening.processing_time_ms} ms` : '—'}</dd>
                  </div>
                </dl>
                {traceUrl && (
                  <a href={traceUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-xs text-brand-700 hover:underline">
                    View trace in Langfuse <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>

              <div className="rounded-xl border border-slate-100 p-4">
                <h4 className="text-sm font-semibold text-slate-900">Summary</h4>
                <p className="mt-3 text-sm leading-relaxed text-slate-700">{screening.candidate_summary}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="rounded-xl border border-slate-100 p-4">
                <h4 className="text-sm font-semibold text-slate-900">Strengths</h4>
                <ul className="mt-3 list-inside list-disc space-y-1 text-sm text-slate-700">
                  {(screening.strengths || []).map((s: string) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>

              <div className="rounded-xl border border-slate-100 p-4">
                <h4 className="text-sm font-semibold text-slate-900">Risks</h4>
                <ul className="mt-3 list-inside list-disc space-y-1 text-sm text-slate-700">
                  {(screening.risks || []).map((s: string) => (
                    <li key={s}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="rounded-xl border border-slate-100 p-4">
              <h4 className="text-sm font-semibold text-slate-900">Follow-up Questions</h4>
              <ul className="mt-3 list-inside list-disc space-y-1 text-sm text-slate-700">
                {(screening.follow_up_questions || []).map((q: string) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
