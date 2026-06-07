import { useState } from 'react';
import type { ReactNode } from 'react';
import type { PatientRecord, TimelineEvent } from '../types';
import CommunicationsPanel from './CommunicationsPanel';
import TasksPanel from './TasksPanel';

type TabId = 'overview' | 'timeline' | 'conditions' | 'allergies' | 'medications' | 'labs' | 'visits' | 'communications' | 'tasks' | 'audit';

type Props = {
  record: PatientRecord | null;
  timeline: TimelineEvent[];
  onAddRecord: () => void;
  onMockSend: (communicationId: number) => Promise<void>;
};

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'conditions', label: 'Conditions' },
  { id: 'allergies', label: 'Allergies' },
  { id: 'medications', label: 'Medications' },
  { id: 'labs', label: 'Labs' },
  { id: 'visits', label: 'Visits' },
  { id: 'communications', label: 'Communications' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'audit', label: 'Audit Trail' },
];

function Badge({ children }: { children: ReactNode }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{children}</span>;
}

export default function PatientRecordTabs({ record, timeline, onAddRecord, onMockSend }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  if (!record) {
    return (
      <section className="card p-6">
        <p className="text-sm text-slate-600">Select a patient to load patient record tabs.</p>
      </section>
    );
  }

  return (
    <section className="card p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="section-title">Patient record</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">{record.patient.name}</h2>
          <p className="mt-2 text-sm text-slate-600">{record.patient.age} years • {record.patient.gender} • {record.patient.primary_physician}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge>{record.patient.status}</Badge>
            <Badge>{record.patient.risk_level} risk</Badge>
            <Badge>{record.patient.preferred_language}</Badge>
          </div>
        </div>
        <button type="button" onClick={onAddRecord} className="rounded-2xl bg-blue-600 px-5 py-3 text-sm font-bold text-white shadow-sm hover:bg-blue-700">
          Add record entry
        </button>
      </div>

      <div className="mt-5 flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button key={tab.id} type="button" onClick={() => setActiveTab(tab.id)} className={`shrink-0 rounded-full px-4 py-2 text-sm font-semibold ${activeTab === tab.id ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}>
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-5">
        {activeTab === 'overview' && (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-blue-50 p-4"><p className="text-sm font-semibold text-blue-700">Conditions</p><p className="mt-2 text-3xl font-black text-slate-950">{record.conditions.length}</p></div>
            <div className="rounded-2xl bg-amber-50 p-4"><p className="text-sm font-semibold text-amber-700">Open care gaps</p><p className="mt-2 text-3xl font-black text-slate-950">{record.care_gaps.filter((gap) => gap.status !== 'Closed').length}</p></div>
            <div className="rounded-2xl bg-green-50 p-4"><p className="text-sm font-semibold text-green-700">Open tasks</p><p className="mt-2 text-3xl font-black text-slate-950">{record.tasks.filter((task) => task.status !== 'completed').length}</p></div>
            <div className="rounded-2xl border border-slate-200 bg-white p-4 md:col-span-3">
              <h3 className="font-bold text-slate-950">Profile</h3>
              <p className="mt-2 text-sm text-slate-600">Phone: {record.patient.phone || 'Mock phone not set'} • Email: {record.patient.email || 'Mock email not set'}</p>
              <p className="mt-1 text-sm text-slate-600">Emergency contact: {record.patient.emergency_contact_name || 'Not set'} {record.patient.emergency_contact_phone}</p>
            </div>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-3">
            {timeline.map((event) => (
              <div key={event.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2"><p className="font-bold text-slate-950">{event.title}</p><Badge>{event.type}</Badge></div>
                <p className="mt-1 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">{event.date} • {event.status}</p>
                <p className="mt-2 text-sm text-slate-600">{event.description}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'conditions' && <div className="flex flex-wrap gap-2">{record.conditions.map((condition) => <Badge key={condition.id}>{condition.name} • {condition.status}</Badge>)}</div>}
        {activeTab === 'allergies' && <div className="space-y-2">{record.allergies.map((allergy) => <div key={allergy.id} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="font-bold text-slate-950">{allergy.allergen}</p><p className="text-sm text-slate-600">{allergy.reaction} • {allergy.severity}</p><p className="mt-1 text-sm text-slate-500">{allergy.notes}</p></div>)}</div>}
        {activeTab === 'medications' && <div className="space-y-2">{record.medications.map((med) => <div key={med.id} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="font-bold text-slate-950">{med.name}</p><p className="text-sm text-slate-600">{med.dose} • {med.frequency}</p><p className="mt-1 text-sm text-slate-500">{med.notes}</p></div>)}</div>}
        {activeTab === 'labs' && <div className="space-y-2">{record.labs.map((lab) => <div key={lab.id} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="font-bold text-slate-950">{lab.name}: {lab.value} {lab.unit}</p><p className="text-sm text-slate-600">{lab.collected_at} • {lab.status}</p></div>)}</div>}
        {activeTab === 'visits' && <div className="space-y-2">{record.previous_visits.map((visit) => <div key={visit.id} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">{visit.date}</p><p className="font-bold text-slate-950">{visit.visit_type}</p><p className="text-sm text-slate-600">{visit.summary}</p></div>)}</div>}
        {activeTab === 'communications' && <CommunicationsPanel communications={record.communications} onMockSend={onMockSend} />}
        {activeTab === 'tasks' && <TasksPanel tasks={record.tasks} />}
        {activeTab === 'audit' && <div className="space-y-2">{record.audit_logs.map((log) => <div key={log.id} className="rounded-2xl border border-slate-200 bg-white p-4"><p className="font-bold text-slate-950">{log.event_type}</p><p className="text-xs text-slate-500">{log.actor} • {new Date(log.created_at).toLocaleString()}</p><pre className="mt-2 whitespace-pre-wrap rounded-xl bg-slate-950 p-3 text-xs text-slate-100">{JSON.stringify(log.details, null, 2)}</pre></div>)}</div>}
      </div>
    </section>
  );
}
