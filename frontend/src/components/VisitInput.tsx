import type { VisitInputState } from '../types';

type Props = {
  value: VisitInputState;
  onChange: (value: VisitInputState) => void;
  onRun: () => void;
  isRunning: boolean;
  disabled: boolean;
};

const fields: Array<{ key: keyof VisitInputState; label: string; rows: number }> = [
  { key: 'chief_complaint', label: 'Chief complaint', rows: 2 },
  { key: 'symptoms', label: 'Symptoms / current visit details', rows: 3 },
  { key: 'vitals', label: 'Vitals', rows: 2 },
  { key: 'doctor_notes', label: 'Doctor notes', rows: 3 },
  { key: 'assessment_notes', label: 'Doctor assessment notes', rows: 3 },
  { key: 'suggested_plan', label: 'Suggested plan', rows: 3 },
];

export default function VisitInput({ value, onChange, onRun, isRunning, disabled }: Props) {
  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Current visit input</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Doctor-entered visit context</h2>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
          Doctor source of truth
        </span>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {fields.map((field) => (
          <label key={field.key} className={field.key === 'suggested_plan' ? 'md:col-span-2' : ''}>
            <span className="text-sm font-semibold text-slate-700">{field.label}</span>
            <textarea
              rows={field.rows}
              value={value[field.key]}
              onChange={(event) => onChange({ ...value, [field.key]: event.target.value })}
              className="mt-2 w-full resize-none rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          </label>
        ))}
      </div>

      <button
        type="button"
        onClick={onRun}
        disabled={disabled || isRunning}
        className="mt-6 w-full rounded-2xl bg-blue-600 px-6 py-4 text-base font-bold text-white shadow-glow transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isRunning ? 'Running CareFlow Agents...' : 'Run CareFlow Agents'}
      </button>
    </section>
  );
}
