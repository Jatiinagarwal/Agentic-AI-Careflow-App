import type { EmailSettings } from '../types';

type Props = {
  settings: EmailSettings | null;
};

export default function EmailSettingsCard({ settings }: Props) {
  if (!settings) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
        Loading email settings...
      </div>
    );
  }

  return (
    <div className={`rounded-2xl border p-4 ${settings.email_enabled && settings.smtp_configured ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'}`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-bold text-slate-950">Email sending mode</p>
          <p className="mt-1 text-sm text-slate-700">{settings.warning}</p>
        </div>
        <span className="rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-700 shadow-sm">
          {settings.email_enabled && settings.smtp_configured ? 'Real SMTP enabled' : 'Mock send mode'}
        </span>
      </div>
      <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
        <span className="rounded-full bg-white px-3 py-1">Host: {settings.smtp_host || 'Not configured'}</span>
        <span className="rounded-full bg-white px-3 py-1">From: {settings.smtp_from_email || 'Not configured'}</span>
        <span className="rounded-full bg-white px-3 py-1">TLS: {settings.smtp_use_tls ? 'On' : 'Off'}</span>
      </div>
    </div>
  );
}
