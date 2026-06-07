import type { PatientHistory } from '../types';

type Props = {
  history: PatientHistory | null;
};

export default function PatientTimeline({ history }: Props) {
  if (!history) {
    return (
      <section className="card p-6">
        <p className="text-sm text-slate-600">Select a patient to load longitudinal history.</p>
      </section>
    );
  }

  return (
    <section className="card p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="section-title">Patient timeline</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Fragmented history review</h2>
        </div>
        <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-700">
          Prior follow-up missed
        </span>
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="font-bold text-slate-900">Conditions</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {history.patient.conditions.map((condition) => (
              <span key={condition} className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700 shadow-sm">
                {condition}
              </span>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h3 className="font-bold text-slate-900">Risk factors</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            {history.patient.risk_factors.map((risk) => (
              <li key={risk} className="flex gap-2">
                <span className="mt-1 h-2 w-2 rounded-full bg-blue-500" />
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="mt-6 grid gap-4 xl:grid-cols-3">
        <div>
          <h3 className="font-bold text-slate-900">Recent labs</h3>
          <div className="mt-3 space-y-2">
            {history.labs.slice(0, 6).map((lab) => (
              <div key={lab.id} className="rounded-2xl border border-slate-200 bg-white p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-slate-900">{lab.name}</p>
                  <p className="text-sm font-bold text-slate-950">
                    {lab.value} {lab.unit}
                  </p>
                </div>
                <p className="mt-1 text-xs text-slate-500">
                  {lab.collected_at} • {lab.status}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-900">Medications</h3>
          <div className="mt-3 space-y-2">
            {history.medications.map((medication) => (
              <div key={medication.id} className="rounded-2xl border border-slate-200 bg-white p-3">
                <p className="font-semibold text-slate-900">{medication.name}</p>
                <p className="text-sm text-slate-600">
                  {medication.dose} • {medication.frequency}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h3 className="font-bold text-slate-900">Previous visits</h3>
          <div className="mt-3 space-y-2">
            {history.previous_visits.map((visit) => (
              <div key={visit.id} className="rounded-2xl border border-slate-200 bg-white p-3">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">{visit.date}</p>
                <p className="mt-1 font-semibold text-slate-900">{visit.visit_type}</p>
                <p className="mt-1 text-sm text-slate-600">{visit.summary}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
