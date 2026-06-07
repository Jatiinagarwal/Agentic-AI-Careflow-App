import { useState } from 'react';

type RecordType = 'condition' | 'allergy' | 'medication' | 'lab' | 'visit' | 'task' | 'care_gap' | 'appointment';

type Props = {
  open: boolean;
  onClose: () => void;
  onAdd: (type: RecordType, payload: Record<string, string>) => Promise<void>;
};

const recordTypes: Array<{ id: RecordType; label: string }> = [
  { id: 'condition', label: 'Condition' },
  { id: 'allergy', label: 'Allergy' },
  { id: 'medication', label: 'Medication' },
  { id: 'lab', label: 'Lab result' },
  { id: 'visit', label: 'Previous visit' },
  { id: 'task', label: 'Follow-up task' },
  { id: 'care_gap', label: 'Care gap' },
  { id: 'appointment', label: 'Appointment' },
];

export default function AddMedicalRecordModal({ open, onClose, onAdd }: Props) {
  const [type, setType] = useState<RecordType>('condition');
  const [primary, setPrimary] = useState('');
  const [secondary, setSecondary] = useState('');
  const [details, setDetails] = useState('');
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [saving, setSaving] = useState(false);

  if (!open) return null;

  async function submit() {
    setSaving(true);
    try {
      const payloadByType: Record<RecordType, Record<string, string>> = {
        condition: { name: primary, status: secondary || 'Active', diagnosed_at: date, notes: details },
        allergy: { allergen: primary, reaction: secondary, severity: details || 'Unknown' },
        medication: { name: primary, dose: secondary, frequency: 'as directed', notes: details },
        lab: { name: primary, value: secondary, unit: '', collected_at: date, status: details || 'available' },
        visit: { date, visit_type: primary || 'Manual visit note', summary: secondary || details, plan: details },
        task: { title: primary, task_type: 'manual_follow_up', description: secondary || details, owner: details || 'Clinic team', status: 'open' },
        care_gap: { gap: primary, priority: secondary || 'Medium', evidence: details, recommended_follow_up_action: details, status: 'Open' },
        appointment: { appointment_date: date, reason: primary || 'Follow-up', status: secondary || 'Scheduled', notes: details },
      };
      await onAdd(type, payloadByType[type]);
      setPrimary('');
      setSecondary('');
      setDetails('');
      onClose();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
      <div className="w-full max-w-2xl rounded-3xl bg-white p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="section-title">Medical record</p>
            <h2 className="mt-2 text-2xl font-bold text-slate-950">Add mock record entry</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded-full bg-slate-100 px-3 py-1 text-sm font-bold text-slate-600">Close</button>
        </div>
        <div className="mt-5 grid gap-4">
          <label className="text-sm font-semibold text-slate-700">
            Record type
            <select value={type} onChange={(event) => setType(event.target.value as RecordType)} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm">
              {recordTypes.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
            </select>
          </label>
          <label className="text-sm font-semibold text-slate-700">
            Main value
            <input value={primary} onChange={(event) => setPrimary(event.target.value)} placeholder="Name, title, reason, or lab name" className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm" />
          </label>
          <label className="text-sm font-semibold text-slate-700">
            Secondary value
            <input value={secondary} onChange={(event) => setSecondary(event.target.value)} placeholder="Status, dose, value, priority, or short summary" className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm" />
          </label>
          <label className="text-sm font-semibold text-slate-700">
            Date
            <input type="date" value={date} onChange={(event) => setDate(event.target.value)} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm" />
          </label>
          <label className="text-sm font-semibold text-slate-700">
            Details
            <textarea value={details} onChange={(event) => setDetails(event.target.value)} rows={3} className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm" />
          </label>
        </div>
        <div className="mt-6 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-2xl bg-slate-100 px-5 py-3 text-sm font-bold text-slate-700">Cancel</button>
          <button type="button" onClick={submit} disabled={saving || !primary} className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-60">{saving ? 'Adding...' : 'Add record'}</button>
        </div>
      </div>
    </div>
  );
}
