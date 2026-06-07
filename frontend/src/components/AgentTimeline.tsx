import type { AgentStep } from '../types';

type Props = {
  steps: AgentStep[];
};

const statusClass: Record<string, string> = {
  queued: 'bg-slate-100 text-slate-600 border-slate-200',
  running: 'bg-blue-50 text-blue-700 border-blue-200 animate-pulse',
  completed: 'bg-green-50 text-green-700 border-green-200',
  blocked: 'bg-amber-50 text-amber-700 border-amber-200',
};

export default function AgentTimeline({ steps }: Props) {
  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Agent workflow</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Visible orchestration timeline</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          Start to audit trail
        </span>
      </div>

      <div className="mt-6 space-y-3">
        {steps.map((step, index) => (
          <div key={`${step.name}-${index}`} className="flex gap-4 rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex flex-col items-center">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-950 text-sm font-bold text-white">
                {index + 1}
              </div>
              {index < steps.length - 1 && <div className="mt-2 h-full min-h-8 w-px bg-slate-200" />}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-bold text-slate-950">{step.name}</p>
                <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass[step.status] ?? statusClass.queued}`}>
                  {step.status}
                </span>
              </div>
              <p className="mt-1 text-sm text-slate-600">{step.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
