import type { ApprovalResponse, GeneratedWorkflowOutput } from '../types';

type Props = {
  output: GeneratedWorkflowOutput | null;
  approval: ApprovalResponse | null;
  onApprove: () => void;
  isApproving: boolean;
};

export default function ApprovalPanel({ output, approval, onApprove, isApproving }: Props) {
  const approved = approval?.approved || output?.approved;

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Doctor approval</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Human-in-the-loop safety gate</h2>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-bold ${approved ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-700'}`}>
          {approved ? 'Approved' : 'Approval required'}
        </span>
      </div>

      <div className="mt-5 grid gap-3 md:grid-cols-2">
        {['SOAP note', 'Patient email', 'Follow-up tasks', 'Medication instruction draft'].map((item) => (
          <div key={item} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p className="font-semibold text-slate-900">{item}</p>
            <p className="mt-1 text-sm text-slate-600">Doctor must review and approve before action execution.</p>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={onApprove}
        disabled={!output || isApproving || Boolean(approved)}
        className="mt-6 w-full rounded-2xl bg-green-600 px-6 py-4 text-base font-bold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {approved ? 'Doctor Approval Recorded' : isApproving ? 'Recording Approval...' : 'Approve All Drafts as Doctor'}
      </button>

      {approval && <p className="mt-3 rounded-2xl bg-green-50 p-4 text-sm font-semibold text-green-800">{approval.message}</p>}
    </section>
  );
}
