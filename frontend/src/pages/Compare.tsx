import { useState } from 'react'
import { api } from '../lib/api'
import { Users } from 'lucide-react'

export function Compare() {
  const [ids, setIds] = useState('')
  const [candidates, setCandidates] = useState<any[] | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submit = async () => {
    setLoading(true)
    setError(null)
    setCandidates(null)
    const list = ids.split(',').map((s) => s.trim()).filter(Boolean)
    if (list.length < 2) {
      setError('Enter at least 2 screening IDs separated by commas.')
      setLoading(false)
      return
    }
    try {
      const r = await api.post('/api/v1/hr/compare', { screening_ids: list })
      setCandidates(r.data.candidates)
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Compare candidates</h1>
        <p className="mt-1 text-sm text-brand-800">Side-by-side fit scores, strengths, and risks.</p>
      </div>

      <section className="card">
        <div className="card-body space-y-5">
          <div>
            <label htmlFor="compare-ids" className="block text-sm font-medium text-slate-700">Screening IDs (comma separated)</label>
            <input
              id="compare-ids"
              className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
              value={ids}
              onChange={(e) => setIds(e.target.value)}
              placeholder="e.g. abc123, def456"
            />
          </div>
          <button onClick={submit} disabled={loading} className="btn-primary gap-2"><Users className="h-4 w-4" /> {loading ? 'Comparing...' : 'Compare'}</button>
          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          {candidates ? (
            <div className="mt-4 overflow-auto rounded-xl border border-slate-200">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50">
                  <tr className="border-b">
                    <th className="px-4 py-3 text-xs font-medium text-slate-600">ID</th>
                    <th className="px-4 py-3 text-xs font-medium text-slate-600">Fit</th>
                    <th className="px-4 py-3 text-xs font-medium text-slate-600">Confidence</th>
                    <th className="px-4 py-3 text-xs font-medium text-slate-600">Strengths</th>
                    <th className="px-4 py-3 text-xs font-medium text-slate-600">Risks</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {candidates.map((c, idx) => (
                    <tr key={c.id} className={idx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}>
                      <td className="px-4 py-3 text-xs text-slate-600">{c.id}</td>
                      <td className="px-4 py-3">{c.fit_score}</td>
                      <td className="px-4 py-3">{c.confidence}</td>
                      <td className="px-4 py-3 text-xs text-slate-600">{(c.strengths || []).join(', ')}</td>
                      <td className="px-4 py-3 text-xs text-slate-600">{(c.risks || []).join(', ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  )
}
