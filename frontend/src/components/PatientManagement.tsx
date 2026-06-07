import { useState } from 'react';
import type { Patient, PatientCreate } from '../types';

type Props = {
  open: boolean;
  onClose: () => void;
  onCreate: (patient: PatientCreate) => Promise<void>;
};

const initialForm: PatientCreate = {
  first_name: '',
  last_name: '',
  age: 50,
  gender: 'Female',
  phone: '',
  email: '',
  address: '',
  primary_physician: 'Dr. Sharma',
  preferred_language: 'English',
  risk_level: 'Moderate',
  status: 'Active',
  consent_for_mock_email: true,
  conditions: [],
  risk_factors: [],
};

export default function PatientManagement({ open, onClose, onCreate }: Props) {
  const [form, setForm] = useState<PatientCreate>(initialForm);
  const [conditionText, setConditionText] = useState('');
  const [saving, setSaving] = useState(false);

  if (!open) return null;

  async function submit() {
    setSaving(true);
    try {
      await onCreate({
        ...form,
        conditions: conditionText.split(',').map((item) => item.trim()).filter(Boolean),
        risk_factors: ['New mock patient record - doctor review required'],
      });
      setForm(initialForm);
      setConditionText('');
      onClose();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4">
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-3xl bg-white p-6 shadow-2xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="section-title">Add mock patient</p>
            <h2 className="mt-2 text-2xl font-bold text-slate-950">Create patient profile</h2>
            <p className="mt-2 text-sm text-slate-600">No real patient data. Use synthetic/demo details only.</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-full bg-slate-100 px-3 py-1 text-sm font-bold text-slate-600">Close</button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {[
            ['first_name', 'First name'],
            ['last_name', 'Last name'],
            ['gender', 'Gender'],
            ['phone', 'Phone'],
            ['email', 'Email'],
            ['primary_physician', 'Primary physician'],
            ['preferred_language', 'Preferred language'],
            ['risk_level', 'Risk level'],
            ['status', 'Status'],
          ].map(([key, label]) => (
            <label key={key} className="text-sm font-semibold text-slate-700">
              {label}
              <input
                value={String(form[key as keyof PatientCreate] ?? '')}
                onChange={(event) => setForm({ ...form, [key]: event.target.value })}
                className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
              />
            </label>
          ))}
          <label className="text-sm font-semibold text-slate-700">
            Age
            <input
              type="number"
              value={form.age}
              onChange={(event) => setForm({ ...form, age: Number(event.target.value) })}
              className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
            />
          </label>
          <label className="md:col-span-2 text-sm font-semibold text-slate-700">
            Address
            <input
              value={form.address ?? ''}
              onChange={(event) => setForm({ ...form, address: event.target.value })}
              className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
            />
          </label>
          <label className="md:col-span-2 text-sm font-semibold text-slate-700">
            Conditions, comma separated
            <input
              value={conditionText}
              onChange={(event) => setConditionText(event.target.value)}
              placeholder="Diabetes, hypertension, asthma"
              className="mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-blue-500"
            />
          </label>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-2xl bg-slate-100 px-5 py-3 text-sm font-bold text-slate-700">Cancel</button>
          <button type="button" onClick={submit} disabled={saving} className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white disabled:opacity-60">
            {saving ? 'Saving...' : 'Create patient'}
          </button>
        </div>
      </div>
    </div>
  );
}
