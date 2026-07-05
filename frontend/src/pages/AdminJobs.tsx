import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { Plus, XCircle } from 'lucide-react'

export function AdminJobs() {
  const [jobs, setJobs] = useState<any[]>([])
  const [form, setForm] = useState({
    title: '',
    department: '',
    description: '',
    requirements: '',
    location: '',
    salary_range: '',
    status: 'active',
  })
  const [error, setError] = useState<string | null>(null)

  const loadJobs = () => {
    api.get('/api/v1/admin/jobs').then((r) => setJobs(r.data)).catch((e) => setError(e.message))
  }

  useEffect(() => {
    loadJobs()
  }, [])

  const createJob = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    try {
      await api.post('/api/v1/admin/jobs', form)
      setForm({
        title: '',
        department: '',
        description: '',
        requirements: '',
        location: '',
        salary_range: '',
        status: 'active',
      })
      loadJobs()
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    }
  }

  const closeJob = async (id: string) => {
    try {
      await api.put(`/api/v1/admin/jobs/${id}`, { status: 'closed' })
      loadJobs()
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    }
  }

  return (
    <div className="space-y-6">
      <section className="card">
        <div className="card-body">
          <h2 className="section-title flex items-center gap-2"><Plus className="h-5 w-5 text-brand-600" /> Create Job</h2>
          <form onSubmit={createJob} className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Title</label>
              <input className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Department</label>
              <input className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700">Location</label>
              <input className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Description</label>
              <textarea className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700">Requirements (one per line)</label>
              <textarea className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.requirements} onChange={(e) => setForm({ ...form, requirements: e.target.value })} />
            </div>
            <div className="md:col-span-2 flex flex-wrap items-center gap-3">
              <div>
                <label className="block text-sm font-medium text-slate-700">Salary range</label>
                <input className="mt-1 rounded-lg border border-slate-200 p-2.5 text-sm" value={form.salary_range} onChange={(e) => setForm({ ...form, salary_range: e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Status</label>
                <select className="mt-1 rounded-lg border border-slate-200 p-2.5 text-sm" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
                  <option value="active">Active</option>
                  <option value="closed">Closed</option>
                  <option value="draft">Draft</option>
                </select>
              </div>
              <button type="submit" className="btn-primary mt-4"><Plus className="h-4 w-4" /> Create</button>
            </div>
          </form>
          {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
        </div>
      </section>

      <section className="card">
        <div className="card-body">
          <h2 className="section-title">Jobs</h2>
          <div className="mt-4 divide-y">
            {jobs.map((job) => (
              <div key={job.id} className="flex flex-col gap-2 py-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="text-sm font-medium text-slate-900">{job.title}</div>
                  <div className="mt-1 text-xs text-slate-600">
                    {[job.department, job.location, job.status, job.salary_range].filter(Boolean).join(' · ')}
                  </div>
                </div>
                {job.status === 'active' && (
                  <button onClick={() => closeJob(job.id)} className="btn-secondary text-xs text-red-600 hover:text-red-700 gap-1 self-start md:self-center">
                    <XCircle className="h-4 w-4" /> Close
                  </button>
                )}
              </div>
            ))}
            {jobs.length === 0 && <p className="py-6 text-sm text-slate-600">No jobs yet.</p>}
          </div>
        </div>
      </section>
    </div>
  )
}
