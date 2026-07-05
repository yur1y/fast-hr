import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { Clock } from 'lucide-react'

export function Tasks() {
  const [taskId, setTaskId] = useState('')
  const [taskStatus, setTaskStatus] = useState<any>(null)
  const [canaryResult, setCanaryResult] = useState<any>(null)

  const queueCanary = async () => {
    const r = await api.post('/api/v1/tasks/canary')
    setTaskId(r.data.task_id)
    setCanaryResult(r.data)
  }

  const pollTask = async () => {
    if (!taskId) return
    const r = await api.get(`/api/v1/tasks/${taskId}`)
    setTaskStatus(r.data)
  }

  useEffect(() => {
    if (!taskId) return
    const interval = setInterval(pollTask, 2000)
    return () => clearInterval(interval)
  }, [taskId])

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-brand-100 bg-brand-50 p-6">
        <h1 className="text-xl font-semibold text-brand-900">Tasks</h1>
        <p className="mt-1 text-sm text-brand-800">Background jobs and canary drift detection.</p>
      </div>

      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="section-title">Canary drift detection</h2>
          <p className="text-sm text-slate-600">Queue a background canary run and watch task status.</p>
          <button onClick={queueCanary} className="btn-primary gap-2"><Clock className="h-4 w-4" /> Queue canary run</button>
          {canaryResult ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(canaryResult, null, 2)}</pre>
          ) : null}
        </div>
      </section>

      <section className="card">
        <div className="card-body space-y-4">
          <h2 className="section-title">Task status</h2>
          <div className="flex flex-wrap items-end gap-3">
            <div className="flex-1 min-w-[180px]">
              <label htmlFor="task-id" className="block text-sm font-medium text-slate-700">Task ID</label>
              <input
                id="task-id"
                className="mt-1 w-full rounded-lg border border-slate-200 p-2.5 text-sm"
                value={taskId}
                onChange={(e) => setTaskId(e.target.value)}
              />
            </div>
            <button onClick={pollTask} className="btn-secondary">Check status</button>
          </div>
          {taskStatus ? (
            <pre className="mt-4 overflow-auto rounded-xl bg-slate-50 p-4 text-xs">{JSON.stringify(taskStatus, null, 2)}</pre>
          ) : null}
          {taskId ? (
            <p className="text-xs text-slate-500">Auto-refreshes every 2s while a task ID is set.</p>
          ) : null}
        </div>
      </section>
    </div>
  )
}
