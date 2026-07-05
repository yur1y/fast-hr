import { useState } from 'react'
import { api } from '../lib/api'
import { Play, Plus } from 'lucide-react'

export function Batch() {
  const [jd, setJd] = useState('Looking for senior Python backend developer')
  const [resumes, setResumes] = useState('John Doe\nPython, FastAPI, PostgreSQL, 5 years\n\nJane Smith\nJava, Spring, AWS, 3 years')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [addOpen, setAddOpen] = useState(false)
  const [name, setName] = useState('')
  const [details, setDetails] = useState('')

  const addCandidate = () => {
    const entry = `${name}\n${details}`
    setResumes((prev) => (prev ? prev + '\n\n' + entry : entry))
    setName('')
    setDetails('')
    setAddOpen(false)
  }

  const submit = async () => {
    setLoading(true)
    setResult(null)
    const lines = resumes.split('\n').map((s) => s.trim()).filter(Boolean)
    try {
      const r = await api.post('/api/v1/hr/batch', {
        job_description: jd,
        resumes: lines,
      })
      setResult(r.data)
    } catch (e: any) {
      setResult({ error: e.response?.data?.detail ?? e.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Batch screening</h1>
        <p className="mt-1 text-sm text-brand-800">Compare multiple resumes against a single job description.</p>
      </div>

      <section className="card">
        <div className="card-body space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-slate-700">Candidates</h2>
            <button onClick={() => setAddOpen((v) => !v)} className="btn-secondary gap-2">
              <Plus className="h-4 w-4" /> Add candidate
            </button>
          </div>

          {addOpen && (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div>
                <label htmlFor="candidate-name" className="block text-sm font-medium text-slate-700">Name / headline</label>
                <textarea
                  id="candidate-name"
                  className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
                  rows={2}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="candidate-details" className="block text-sm font-medium text-slate-700">Details</label>
                <textarea
                  id="candidate-details"
                  className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
                  rows={2}
                  value={details}
                  onChange={(e) => setDetails(e.target.value)}
                />
              </div>
              <div className="md:col-span-2">
                <button onClick={addCandidate} className="btn-primary">Add</button>
              </div>
            </div>
          )}

           <div>
             <label htmlFor="batch-jd" className="block text-sm font-medium text-slate-700">Job description</label>
             <textarea
               id="batch-jd"
               className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
               rows={3}
               value={jd}
               onChange={(e) => setJd(e.target.value)}
             />
           </div>

           <div>
             <label htmlFor="batch-resumes" className="block text-sm font-medium text-slate-700">Resumes</label>
             <textarea
               id="batch-resumes"
               className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm font-mono"
               rows={12}
               value={resumes}
               onChange={(e) => setResumes(e.target.value)}
             />
           </div>
          <button onClick={submit} disabled={loading} className="btn-primary gap-2">
            <Play className="h-4 w-4" /> {loading ? 'Running batch...' : 'Run batch'}
          </button>
          {result ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(result, null, 2)}</pre>
          ) : null}
        </div>
      </section>
    </div>
  )
}
