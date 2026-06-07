import { useEffect, useState } from 'react';
import type { CommunicationDraft, EmailSettings, Patient } from '../types';
import EmailStatusBadge from './EmailStatusBadge';

type Props = {
  communication: CommunicationDraft | null;
  patient: Patient | null;
  settings: EmailSettings | null;
  open: boolean;
  isBusy: boolean;
  onClose: () => void;
  onSave: (communicationId: number, payload: { subject: string; body: string; recipient_email: string }) => Promise<void>;
  onApprove: (communicationId: number) => Promise<void>;
  onSend: (communicationId: number) => Promise<void>;
  onCancel: (communicationId: number) => Promise<void>;
};

const sentStatuses = ['Sent', 'Mock Sent'];

export default function EmailPreviewModal({ communication, patient, settings, open, isBusy, onClose, onSave, onApprove, onSend, onCancel }: Props) {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [recipientEmail, setRecipientEmail] = useState('');

  useEffect(() => {
    if (communication) {
      setSubject(communication.subject || '');
      setBody(communication.body || '');
      setRecipientEmail(communication.recipient_email || patient?.email || '');
    }
  }, [communication, patient]);

  if (!open || !communication) return null;

  const hasConsent = Boolean(patient?.consent_for_mock_email);
  const canSend =
    communication.approval_status === 'Approved' &&
    !sentStatuses.includes(communication.status) &&
    hasConsent &&
    recipientEmail.trim().length > 0 &&
    subject.trim().length > 0 &&
    body.trim().length > 0;

  async function handleSave() {
    await onSave(communication!.id, { subject, body, recipient_email: recipientEmail });
  }

  async function handleApprove() {
    await handleSave();
    await onApprove(communication!.id);
  }

  async function handleSend() {
    if (!canSend) return;
    const confirmed = window.confirm(`You are about to send this doctor-approved email to ${recipientEmail}. Confirm that the content has been reviewed and is appropriate to send.`);
    if (confirmed) await onSend(communication!.id);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4">
      <div className="max-h-[92vh] w-full max-w-4xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="section-title">Doctor-approved patient communication</p>
            <h2 className="mt-2 text-2xl font-bold text-slate-950">Review and send email</h2>
            <p className="mt-2 text-sm text-slate-600">Email sending may contain sensitive information. Use only with consent and appropriate safeguards.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <EmailStatusBadge status={communication.status} />
            <EmailStatusBadge status={communication.approval_status} />
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm font-semibold text-amber-900">
          {settings?.email_enabled && settings.smtp_configured
            ? 'Real SMTP sending is enabled. Confirm recipient, consent, and message content before sending.'
            : 'Real email is disabled or SMTP is incomplete. Sending will be recorded as Mock Sent.'}
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <label className="text-sm font-semibold text-slate-700">
            Recipient email
            <input value={recipientEmail} onChange={(event) => setRecipientEmail(event.target.value)} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500" />
          </label>
          <div className="rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
            <p><strong>Patient:</strong> {patient?.name || 'Selected patient'}</p>
            <p className="mt-1"><strong>Consent:</strong> {hasConsent ? 'Enabled' : 'Not enabled'}</p>
            <p className="mt-1"><strong>Provider:</strong> {communication.provider || settings?.mode || 'Not used yet'}</p>
          </div>
        </div>

        <label className="mt-4 block text-sm font-semibold text-slate-700">
          Subject
          <input value={subject} onChange={(event) => setSubject(event.target.value)} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500" />
        </label>

        <label className="mt-4 block text-sm font-semibold text-slate-700">
          Body
          <textarea value={body} onChange={(event) => setBody(event.target.value)} rows={12} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm leading-6 outline-none focus:border-blue-500" />
        </label>

        {communication.error_message && <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-800">{communication.error_message}</div>}

        <div className="mt-6 flex flex-wrap justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-full bg-slate-100 px-5 py-2 text-sm font-bold text-slate-700">Close</button>
          <button type="button" disabled={isBusy || sentStatuses.includes(communication.status)} onClick={() => onCancel(communication.id)} className="rounded-full bg-red-50 px-5 py-2 text-sm font-bold text-red-700 disabled:opacity-50">Cancel</button>
          <button type="button" disabled={isBusy || sentStatuses.includes(communication.status)} onClick={handleSave} className="rounded-full bg-slate-950 px-5 py-2 text-sm font-bold text-white disabled:opacity-50">Save Draft</button>
          <button type="button" disabled={isBusy || !subject.trim() || !body.trim() || sentStatuses.includes(communication.status)} onClick={handleApprove} className="rounded-full bg-purple-600 px-5 py-2 text-sm font-bold text-white disabled:opacity-50">Approve</button>
          <button type="button" disabled={isBusy || !canSend} onClick={handleSend} className="rounded-full bg-blue-600 px-5 py-2 text-sm font-bold text-white disabled:bg-slate-200 disabled:text-slate-500">Send Email</button>
        </div>
      </div>
    </div>
  );
}
