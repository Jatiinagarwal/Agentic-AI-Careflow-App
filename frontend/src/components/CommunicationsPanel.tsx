import { useState } from 'react';
import type { CommunicationDraft, EmailSettings, Patient } from '../types';
import EmailPreviewModal from './EmailPreviewModal';
import EmailSettingsCard from './EmailSettingsCard';
import EmailStatusBadge from './EmailStatusBadge';

type Props = {
  communications: CommunicationDraft[];
  patient: Patient | null;
  emailSettings: EmailSettings | null;
  onSave: (communicationId: number, payload: { subject: string; body: string; recipient_email: string }) => Promise<void>;
  onApprove: (communicationId: number) => Promise<void>;
  onSend: (communicationId: number) => Promise<void>;
  onCancel: (communicationId: number) => Promise<void>;
  isBusy?: boolean;
};

export default function CommunicationsPanel({ communications, patient, emailSettings, onSave, onApprove, onSend, onCancel, isBusy = false }: Props) {
  const [selected, setSelected] = useState<CommunicationDraft | null>(null);

  return (
    <div className="space-y-4">
      <EmailSettingsCard settings={emailSettings} />
      <p className="rounded-2xl bg-blue-50 p-4 text-sm font-semibold text-blue-800">
        Doctor-approved patient communication. Email sending may contain sensitive information. Use only with consent and appropriate safeguards.
      </p>

      {communications.length === 0 && <p className="text-sm text-slate-600">No communication drafts yet. Run CareFlow Agents to create one.</p>}

      {communications.map((message) => (
        <article key={message.id} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-bold text-slate-950">{message.subject}</p>
              <p className="mt-1 text-xs text-slate-500">To: {message.recipient_email || patient?.email || 'No recipient email'} • Created {new Date(message.created_at).toLocaleString()}</p>
              {message.sent_at && <p className="mt-1 text-xs text-slate-500">Sent: {new Date(message.sent_at).toLocaleString()}</p>}
            </div>
            <div className="flex flex-wrap gap-2">
              <EmailStatusBadge status={message.status} />
              <EmailStatusBadge status={message.approval_status} />
            </div>
          </div>

          <p className="mt-3 line-clamp-4 whitespace-pre-wrap text-sm text-slate-700">{message.body}</p>
          {message.error_message && <p className="mt-3 rounded-2xl bg-red-50 p-3 text-xs font-semibold text-red-800">{message.error_message}</p>}

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs font-semibold text-amber-700">Draft - Doctor review required. Agents draft emails; doctors send emails.</p>
            <button type="button" onClick={() => setSelected(message)} className="rounded-full bg-slate-950 px-4 py-2 text-sm font-bold text-white">
              Preview / Edit / Send
            </button>
          </div>
        </article>
      ))}

      <EmailPreviewModal
        open={Boolean(selected)}
        communication={selected}
        patient={patient}
        settings={emailSettings}
        isBusy={isBusy}
        onClose={() => setSelected(null)}
        onSave={async (communicationId, payload) => {
          await onSave(communicationId, payload);
          setSelected(null);
        }}
        onApprove={async (communicationId) => {
          await onApprove(communicationId);
          setSelected(null);
        }}
        onSend={async (communicationId) => {
          await onSend(communicationId);
          setSelected(null);
        }}
        onCancel={async (communicationId) => {
          await onCancel(communicationId);
          setSelected(null);
        }}
      />
    </div>
  );
}
