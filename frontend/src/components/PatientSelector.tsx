import type { Patient } from '../types';

type Props = {
  patients: Patient[];
  selectedPatientId: number | null;
  onSelect: (patient: Patient) => void;
};

export default function PatientSelector({ patients, selectedPatientId, onSelect }: Props) {
  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Patient selection</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Mock clinic queue</h2>
        </div>
        <span className="rounded-full bg-green-50 px-3 py-1 text-xs font-semibold text-green-700">Mock data</span>
      </div>
      <div className="mt-5 space-y-3">
        {patients.map((patient) => {
          const selected = patient.id === selectedPatientId;
          return (
            <button
              type="button"
              key={patient.id}
              onClick={() => onSelect(patient)}
              className={`w-full rounded-2xl border p-4 text-left transition ${
                selected ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-slate-200 bg-white hover:border-blue-200 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-lg font-bold text-slate-950">{patient.name}</p>
                  <p className="text-sm text-slate-600">
                    {patient.age} years • {patient.gender}
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                  Visit ready
                </span>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                {patient.conditions.slice(0, 3).map((condition) => (
                  <span key={condition} className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm">
                    {condition}
                  </span>
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}
