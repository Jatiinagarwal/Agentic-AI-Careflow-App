type Props = {
  status: string;
};

function statusClass(status: string) {
  const normalized = status.toLowerCase();
  if (normalized === 'sent') return 'bg-emerald-50 text-emerald-700';
  if (normalized === 'mock sent') return 'bg-cyan-50 text-cyan-700';
  if (normalized === 'failed') return 'bg-red-50 text-red-700';
  if (normalized === 'approved') return 'bg-purple-50 text-purple-700';
  if (normalized === 'queued') return 'bg-blue-50 text-blue-700';
  if (normalized === 'cancelled') return 'bg-slate-100 text-slate-600';
  return 'bg-amber-50 text-amber-700';
}

export default function EmailStatusBadge({ status }: Props) {
  return <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusClass(status || 'Draft')}`}>{status || 'Draft'}</span>;
}
