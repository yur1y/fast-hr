import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Send } from 'lucide-react'

export function Apply() {
  const { job_id } = useParams<{ job_id: string }>()
  const [form, setForm] = useState({ name: '', email: '', cover_letter: '', linkedin_url: '' })
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!file) {
      setError('Please upload a resume.')
      return
    }
    const data = new FormData()
    data.append('job_id', job_id || '')
    data.append('name', form.name)
    data.append('email', form.email)
    data.append('resume', file)
    if (form.cover_letter) data.append('cover_letter', form.cover_letter)
    if (form.linkedin_url) data.append('linkedin_url', form.linkedin_url)
    try {
      const r = await api.post('/api/v1/careers/apply', data, { headers: { 'Content-Type': 'multipart/form-data' } })
      setResult(r.data)
    } catch (e: any) {
      setError(e.response?.data?.detail ?? e.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Apply</h1>
        <p className="mt-1 text-sm text-brand-800">Submit your resume and cover letter for review.</p>
      </div>

      <section className="card">
        <div className="card-body">
          <form onSubmit={submit} className="space-y-5">
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-700">Full name</label>
                <input id="name" className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              </div>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700">Email</label>
                <input id="email" type="email" className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              </div>
            </div>
            <div>
              <label htmlFor="linkedin_url" className="block text-sm font-medium text-slate-700">LinkedIn</label>
              <input id="linkedin_url" className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" value={form.linkedin_url} onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })} />
            </div>
            <div>
              <label htmlFor="resume" className="block text-sm font-medium text-slate-700">Resume (PDF/DOCX)</label>
              <input id="resume" type="file" accept=".pdf,.docx,.txt" className="mt-1 block w-full text-sm" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </div>
            <div>
              <label htmlFor="cover" className="block text-sm font-medium text-slate-700">Cover letter</label>
              <textarea id="cover" className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm" rows={5} value={form.cover_letter} onChange={(e) => setForm({ ...form, cover_letter: e.target.value })} />
            </div>
            <div className="flex flex-wrap gap-3">
              <button type="submit" className="btn-primary gap-2"><Send className="h-4 w-4" /> Submit application</button>
              <Link to={`/careers/jobs/${job_id}`} className="btn-secondary">Cancel</Link>
            </div>
          </form>
          {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
          {result ? (
            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-xs">
              <p className="font-medium text-emerald-800">Application submitted</p>
              <p className="mt-1 text-emerald-700">ID: {result.application_id || result.id}</p>
              <p className="text-emerald-700">Status: {result.status}</p>
            </div>
          ) : null}
        </div>
      </section>
    </div>
  )
}
