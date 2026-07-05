import { useState } from 'react'
import { api } from '../lib/api'
import { Play, List, RefreshCw } from 'lucide-react'

type LieType = 'date_overlap' | 'skill_inflation' | 'phantom_company' | 'backdated_title' | 'degree_mismatch' | 'location_lie' | 'salary_inflation' | 'reference_fake'

const LIE_TYPES: LieType[] = [
  'date_overlap',
  'skill_inflation',
  'phantom_company',
  'backdated_title',
  'degree_mismatch',
  'location_lie',
  'salary_inflation',
  'reference_fake',
]

export function Fuzzer() {
  const [count, setCount] = useState(10)
  const [selected, setSelected] = useState<LieType[]>(['date_overlap', 'skill_inflation'])
  const [runResult, setRunResult] = useState<any>(null)
  const [asyncResult, setAsyncResult] = useState<any>(null)
  const [badges, setBadges] = useState<any>(null)
  const [lookupId, setLookupId] = useState('')
  const [lookupResult, setLookupResult] = useState<any>(null)

  const toggle = (lt: LieType) => {
    setSelected((prev) => (prev.includes(lt) ? prev.filter((x) => x !== lt) : [...prev, lt]))
  }

  const runSync = async () => {
    setRunResult(null)
    const r = await api.post('/api/v1/fuzzer/run', { lie_types: selected, count })
    setRunResult(r.data)
  }

  const runAsync = async () => {
    setAsyncResult(null)
    const r = await api.post('/api/v1/fuzzer/run-async', { lie_types: selected, count })
    setAsyncResult(r.data)
  }

  const loadBadges = async () => {
    const r = await api.get('/api/v1/fuzzer/badges')
    setBadges(r.data)
  }

  const lookupRun = async () => {
    if (!lookupId) return
    const r = await api.get(`/api/v1/fuzzer/runs/${lookupId}`)
    setLookupResult(r.data)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Fuzzer</h1>
        <p className="mt-1 text-sm text-brand-800">Detect inconsistencies and deception patterns in candidate profiles.</p>
      </div>

      <section className="card">
        <div className="card-body space-y-5">
          <h2 className="section-title">Run fuzzer</h2>
          <div className="flex flex-wrap gap-2">
            {LIE_TYPES.map((lt) => (
              <button
                key={lt}
                onClick={() => toggle(lt)}
                className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${selected.includes(lt) ? 'bg-brand-600 text-white border-brand-600' : 'bg-white hover:bg-slate-50'}`}
              >
                {lt}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <label htmlFor="fuzzer-count" className="text-sm font-medium text-slate-700">Count</label>
            <input
              id="fuzzer-count"
              type="number"
              className="w-24 rounded-lg border border-slate-200 p-2 text-sm"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              min={1}
              max={50}
            />
            <button onClick={runSync} className="btn-primary gap-2"><Play className="h-4 w-4" /> Run sync</button>
            <button onClick={runAsync} className="btn-secondary gap-2"><List className="h-4 w-4" /> Queue async</button>
          </div>
          {runResult ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(runResult, null, 2)}</pre>
          ) : null}
          {asyncResult ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(asyncResult, null, 2)}</pre>
          ) : null}
        </div>
      </section>

      <section className="card">
        <div className="card-body space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="section-title">Badges</h2>
            <button onClick={loadBadges} className="btn-secondary gap-2"><RefreshCw className="h-4 w-4" /> Refresh</button>
          </div>
          {badges ? (
            <div className="flex flex-wrap gap-2">
              {badges.badges?.length ? (
                badges.badges.map((b: any) => (
                  <img key={b.lie_type} src={b.badge_url} alt={b.lie_type} className="h-6" />
                ))
              ) : (
                <p className="text-sm text-slate-600">No badges yet.</p>
              )}
            </div>
          ) : null}
        </div>
      </section>

      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="section-title">Lookup run</h2>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex-1 min-w-[180px]">
              <label htmlFor="run-id" className="block text-sm font-medium text-slate-700">Run ID</label>
              <input
                id="run-id"
                className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
                value={lookupId}
                onChange={(e) => setLookupId(e.target.value)}
              />
            </div>
            <button onClick={lookupRun} className="btn-secondary">Get run</button>
          </div>
          {lookupResult ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(lookupResult, null, 2)}</pre>
          ) : null}
        </div>
      </section>
    </div>
  )
}
