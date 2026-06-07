import type { CommunicationDraft } from '../types';

type Props = {
  communications: CommunicationDraft[];
  onMockSend: (communicationId: number) => Promise<void>;
};

export default function CommunicationsPanel({ communications, onMockSend }: Props) {
  return (
    <div className="space-y-3">
      <p className="rounded-2xl bg-blue-50 p-4 text-sm font-semibold text-blue-800">Simulated email only. No real patient email is sent.</p>
      {communications.length === 0 && <p className="text-sm text-slate-600">No communication drafts yet. Run CareFlow Agents to create one.</p>}
      {communications.map((message) => (
        <div key={message.id} className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-bold text-slate-950">{message.subject}</p>
              <p className="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">{message.status}</p>
            </div>
            <button
              type="button"
              onClick={() => onMockSend(message.id)}
              disabled={!['Queued', 'Approved'].includes(message.status)}
              className="rounded-full bg-slate-950 px-3 py-1 text-xs font-bold text-white disabled:bg-slate-200 disabled:text-slate-500"
            >
              Mock send
            </button>
          </div>
          <p className="mt-3 whitespace-pre-wrap text-sm text-slate-700">{message.body}</p>
          <p className="mt-3 rounded-2xl bg-amber-50 p-3 text-xs font-semibold text-amber-800">{message.safety_label}</p>
        </div>
      ))}
    </div>
  );
}
