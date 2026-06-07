import type { ActionExecutionResponse, ApprovalResponse, GeneratedWorkflowOutput } from '../types';

type Props = {
  output: GeneratedWorkflowOutput | null;
  approval: ApprovalResponse | null;
  execution: ActionExecutionResponse | null;
  onExecute: () => void;
  isExecuting: boolean;
};

export default function ActionPanel({ output, approval, execution, onExecute, isExecuting }: Props) {
  const canExecute = Boolean(output && approval?.approved && !execution?.executed);

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Action execution</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Simulated care coordination</h2>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${execution?.executed ? 'bg-green-50 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
          {execution?.executed ? 'Completed' : 'Blocked until approval'}
        </span>
      </div>

      <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
        Actions are simulated only: mock EHR note save, email queue, nurse task, lab reminder, and appointment follow-up.
      </div>

      <button
        type="button"
        onClick={onExecute}
        disabled={!canExecute || isExecuting}
        className="mt-6 w-full rounded-2xl bg-slate-950 px-6 py-4 text-base font-bold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {execution?.executed ? 'Simulated Actions Completed' : isExecuting ? 'Executing Simulated Actions...' : 'Execute Approved Actions'}
      </button>

      {execution && (
        <div className="mt-6 space-y-3">
          {execution.action_log.map((action) => (
            <div key={action.action} className="rounded-2xl border border-green-100 bg-green-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="font-bold text-green-950">{action.action.replaceAll('_', ' ')}</p>
                <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-green-700">{action.status}</span>
              </div>
              <p className="mt-1 text-sm text-green-800">{action.detail}</p>
            </div>
          ))}
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <p className="font-bold text-slate-950">Created task statuses</p>
            <div className="mt-3 space-y-2">
              {execution.task_statuses.map((task) => (
                <div key={task.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-slate-50 p-3 text-sm">
                  <span className="font-semibold text-slate-800">{task.title}</span>
                  <span className="text-slate-600">{task.owner} • {task.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
