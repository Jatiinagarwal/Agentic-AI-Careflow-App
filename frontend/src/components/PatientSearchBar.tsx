import type { Patient } from '../types';

type Props = {
  query: string;
  onQueryChange: (query: string) => void;
  onAddPatient: () => void;
  patients: Patient[];
};

export default function PatientSearchBar({ query, onQueryChange, onAddPatient, patients }: Props) {
  return (
    <section className="card p-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="section-title">Patient management</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Search clinic records</h2>
          <p className="mt-2 text-sm text-slate-600">Search by name, phone, condition, risk level, or status. Mock patient data only.</p>
        </div>
        <button type="button" onClick={onAddPatient} className="rounded-2xl bg-slate-950 px-5 py-3 text-sm font-bold text-white shadow-sm hover:bg-slate-800">
          Add mock patient
        </button>
      </div>
      <input
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        placeholder="Search Rajesh, asthma, high risk, overdue labs..."
        className="mt-5 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
      />
      <p className="mt-3 text-xs font-semibold text-slate-500">Showing {patients.length} mock patient record{patients.length === 1 ? '' : 's'}.</p>
    </section>
  );
}
