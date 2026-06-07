import type { Patient } from '../types';

type Props = {
  patients: Patient[];
  selectedPatientId: number | null;
  onSelect: (patient: Patient) => void;
};

function statusClass(status?: string | null) {
  const lowered = (status || 'Active').toLowerCase();
  if (lowered.includes('overdue')) return 'bg-red-50 text-red-700';
  if (lowered.includes('follow')) return 'bg-amber-50 text-amber-700';
  if (lowered.includes('draft')) return 'bg-purple-50 text-purple-700';
  return 'bg-green-50 text-green-700';
}

function safeConditions(patient: Patient): string[] {
  if (Array.isArray(patient.conditions)) {
    return patient.conditions;
  }
  return [];
}

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
        {patients.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-600">
            No patients found. Add a mock patient or check that the backend is running.
          </div>
        ) : (
          patients.map((patient) => {
            const selected = patient.id === selectedPatientId;
            const patientStatus = patient.status || 'Active';
            const patientRiskLevel = patient.risk_level || 'Standard';
            const patientGender = patient.gender || 'Unknown';
            const patientAge = patient.age ?? 'N/A';
            const patientName = patient.name || `${patient.first_name ?? ''} ${patient.last_name ?? ''}`.trim() || 'Unnamed patient';
            const conditions = safeConditions(patient);

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
                    <p className="text-lg font-bold text-slate-950">{patientName}</p>
                    <p className="text-sm text-slate-600">
                      {patientAge} years • {patientGender} • {patientRiskLevel} risk
                    </p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass(patientStatus)}`}>
                    {patientStatus}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap gap-2">
                  {conditions.length === 0 ? (
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-500 shadow-sm">
                      No conditions recorded
                    </span>
                  ) : (
                    conditions.slice(0, 3).map((condition) => (
                      <span key={condition} className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 shadow-sm">
                        {condition}
                      </span>
                    ))
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>
    </section>
  );
}