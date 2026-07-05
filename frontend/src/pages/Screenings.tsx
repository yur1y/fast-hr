import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Play, Search } from 'lucide-react'

export function Screenings() {
  const [resume, setResume] = useState('Python developer with 5 years experience in FastAPI and PostgreSQL')
  const [jd, setJd] = useState('Looking for senior Python backend developer')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [id, setId] = useState('')
  const [lookup, setLookup] = useState<any>(null)
  const [lookupLoading, setLookupLoading] = useState(false)

  const fetchAll = async () => {
    setLookupLoading(true)
    setLookup(null)
    try {
      const r = await api.get('/api/v1/screenings/all')
      setLookup(r.data)
    } catch (e: any) {
      setLookup({ error: e.response?.data?.detail ?? e.message })
    } finally {
      setLookupLoading(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  const create = async () => {
    setLoading(true)
    setResult(null)
    try {
      const r = await api.post('/api/v1/screenings', { resume_text: resume, job_description: jd })
      setResult(r.data)
      setId(r.data.id)
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail ?? e.message })
    } finally {
      setLoading(false)
    }
  }

  const lookupById = async () => {
    setLookupLoading(true)
    setLookup(null)
    try {
      const endpoint = id ? `/api/v1/screenings/${id}` : `/api/v1/screenings/all`
      const r = await api.get(endpoint)
      setLookup(r.data)
    } catch (e: any) {
      setLookup({ error: e.response?.data?.detail ?? e.message })
    } finally {
      setLookupLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Screenings</h1>
        <p className="mt-1 text-sm text-brand-800">AI-powered candidate evaluation.</p>
      </div>

      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="section-title">Create screening</h2>
          <div>
            <label htmlFor="resume" className="block text-sm font-medium text-slate-700">Resume text</label>
            <textarea
              id="resume"
              className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
              rows={5}
              value={resume}
              onChange={(e) => setResume(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="jd" className="block text-sm font-medium text-slate-700">Job description</label>
            <textarea
              id="jd"
              className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
              rows={4}
              value={jd}
              onChange={(e) => setJd(e.target.value)}
            />
          </div>
          <button onClick={create} disabled={loading} className="btn-primary gap-2">
            <Play className="h-4 w-4" /> {loading ? 'Screening...' : 'Run screening'}
          </button>
          {result ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(result, null, 2)}</pre>
          ) : null}
        </div>
      </section>

      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="section-title">Lookup</h2>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex-1 min-w-[180px]">
              <label htmlFor="screening-id" className="block text-sm font-medium text-slate-700">Screening ID</label>
              <input
                id="screening-id"
                className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
                value={id}
                onChange={(e) => setId(e.target.value)}
              />
            </div>
            <button onClick={lookupById} disabled={lookupLoading} className="btn-secondary gap-2">
              <Search className="h-4 w-4" /> {lookupLoading ? 'Loading...' : 'Lookup'}
            </button>
            <button onClick={fetchAll} disabled={lookupLoading} className="btn-secondary">
              Show all
            </button>
            {id ? (
              <a
                className="btn-secondary"
                href={`/api/v1/screenings/${id}/trace`}
                target="_blank"
                rel="noreferrer"
              >
                Open trace
              </a>
            ) : null}
          </div>
          {lookup ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(lookup, null, 2)}</pre>
          ) : null}
        </div>
      </section>
    </div>
  )
}
