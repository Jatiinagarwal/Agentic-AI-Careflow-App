import { useState } from 'react';
import type { ReactNode } from 'react';
import CommunicationsPanel from './CommunicationsPanel';
import TasksPanel from './TasksPanel';
import type { PatientRecord, TimelineEvent } from '../types';

type Props = {
  record: PatientRecord | null;
  timeline: TimelineEvent[];
  onMockSend?: (communicationId: number) => Promise<void> | void;
};

type TabId = 'overview' | 'timeline' | 'conditions' | 'medications' | 'allergies' | 'labs' | 'visits' | 'communications' | 'tasks' | 'audit';

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'conditions', label: 'Conditions' },
  { id: 'medications', label: 'Medications' },
  { id: 'allergies', label: 'Allergies' },
  { id: 'labs', label: 'Labs' },
  { id: 'visits', label: 'Visits' },
  { id: 'communications', label: 'Communications' },
  { id: 'tasks', label: 'Tasks' },
  { id: 'audit', label: 'Audit Trail' },
];

function EmptyState({ children }: { children: ReactNode }) {
  return <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-600">{children}</div>;
}

function Badge({ children }: { children: ReactNode }) {
  return <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{children}</span>;
}

function Card({ children }: { children: ReactNode }) {
  return <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">{children}</div>;
}

export default function PatientRecordTabs({ record, timeline, onMockSend }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  if (!record) {
    return (
      <section className="card p-6">
        <p className="section-title">Patient record</p>
        <h2 className="mt-2 text-2xl font-bold text-slate-950">Select a patient to view record</h2>
        <p className="mt-3 text-sm text-slate-600">The longitudinal record will appear here after patient selection.</p>
      </section>
    );
  }

  const patientName = record.patient.name || `${record.patient.first_name ?? ''} ${record.patient.last_name ?? ''}`.trim() || 'Selected patient';

  return (
    <section className="card p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="section-title">Patient record</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">{patientName}</h2>
          <p className="mt-1 text-sm text-slate-600">
            Longitudinal record, communications, tasks, and audit trail for this mock patient.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge>{record.patient.status || 'Active'}</Badge>
          <Badge>{record.patient.risk_level || 'Standard'} risk</Badge>
        </div>
      </div>

      <div className="mt-5 flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`shrink-0 rounded-full px-4 py-2 text-sm font-semibold transition ${
              activeTab === tab.id ? 'bg-slate-950 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mt-5">
        {activeTab === 'overview' && (
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <p className="section-title">Demographics</p>
              <div className="mt-3 space-y-2 text-sm text-slate-700">
                <p>Age: {record.patient.age ?? 'N/A'}</p>
                <p>Gender: {record.patient.gender || 'N/A'}</p>
                <p>Phone: {record.patient.phone || 'N/A'}</p>
                <p>Email: {record.patient.email || 'N/A'}</p>
                <p>Preferred language: {record.patient.preferred_language || 'N/A'}</p>
              </div>
            </Card>

            <Card>
              <p className="section-title">Clinical snapshot</p>
              <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                <Badge>{record.conditions.length} conditions</Badge>
                <Badge>{record.medications.length} medications</Badge>
                <Badge>{record.labs.length} labs</Badge>
                <Badge>{record.tasks.length} tasks</Badge>
                <Badge>{record.communications.length} communications</Badge>
                <Badge>{record.audit_logs.length} audit events</Badge>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="space-y-3">
            {timeline.length === 0 ? (
              <EmptyState>No timeline events yet.</EmptyState>
            ) : (
              timeline.map((event) => (
                <Card key={`${event.event_type}-${event.title}-${event.created_at}`}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{event.event_type}</p>
                      <h3 className="mt-1 font-bold text-slate-950">{event.title}</h3>
                      <p className="mt-1 text-sm text-slate-600">{event.description}</p>
                    </div>
                    <Badge>{event.created_at ? new Date(event.created_at).toLocaleDateString() : 'No date'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'conditions' && (
          <div className="space-y-3">
            {record.conditions.length === 0 ? (
              <EmptyState>No conditions recorded.</EmptyState>
            ) : (
              record.conditions.map((condition) => (
                <Card key={condition.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{condition.name}</h3>
                      <p className="mt-1 text-sm text-slate-600">{condition.notes || 'No notes'}</p>
                    </div>
                    <Badge>{condition.status || 'Active'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'medications' && (
          <div className="space-y-3">
            {record.medications.length === 0 ? (
              <EmptyState>No medications recorded.</EmptyState>
            ) : (
              record.medications.map((medication) => (
                <Card key={medication.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{medication.name}</h3>
                      <p className="mt-1 text-sm text-slate-600">
                        {medication.dose || 'Dose not recorded'} • {medication.frequency || 'Frequency not recorded'}
                      </p>
                    </div>
                    <Badge>{medication.status || 'Active'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'allergies' && (
          <div className="space-y-3">
            {record.allergies.length === 0 ? (
              <EmptyState>No allergies recorded.</EmptyState>
            ) : (
              record.allergies.map((allergy) => (
                <Card key={allergy.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{allergy.allergen}</h3>
                      <p className="mt-1 text-sm text-slate-600">{allergy.reaction || 'Reaction not recorded'}</p>
                    </div>
                    <Badge>{allergy.severity || 'Unknown severity'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'labs' && (
          <div className="space-y-3">
            {record.labs.length === 0 ? (
              <EmptyState>No labs recorded.</EmptyState>
            ) : (
              record.labs.map((lab) => (
                <Card key={lab.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{lab.test_name}</h3>
                      <p className="mt-1 text-sm text-slate-600">
                        {lab.value} {lab.unit || ''} {lab.reference_range ? `• Ref: ${lab.reference_range}` : ''}
                      </p>
                    </div>
                    <Badge>{lab.result_date || 'No date'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'visits' && (
          <div className="space-y-3">
            {record.visits.length === 0 ? (
              <EmptyState>No visits recorded.</EmptyState>
            ) : (
              record.visits.map((visit) => (
                <Card key={visit.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{visit.chief_complaint || 'Visit note'}</h3>
                      <p className="mt-1 text-sm text-slate-600">{visit.doctor_notes || visit.assessment_notes || 'No visit notes'}</p>
                    </div>
                    <Badge>{visit.status || 'Draft'}</Badge>
                  </div>
                </Card>
              ))
            )}
          </div>
        )}

        {activeTab === 'communications' && <CommunicationsPanel communications={record.communications} onMockSend={onMockSend} />}

        {activeTab === 'tasks' && <TasksPanel tasks={record.tasks} />}

        {activeTab === 'audit' && (
          <div className="space-y-3">
            {record.audit_logs.length === 0 ? (
              <EmptyState>No audit events yet.</EmptyState>
            ) : (
              record.audit_logs.map((event) => (
                <Card key={event.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="font-bold text-slate-950">{event.event_type}</h3>
                      <p className="mt-1 text-sm text-slate-600">Actor: {event.actor}</p>
                    </div>
                    <Badge>{new Date(event.created_at).toLocaleString()}</Badge>
                  </div>
                  <pre className="mt-3 whitespace-pre-wrap rounded-2xl bg-slate-950 p-4 text-xs text-slate-100">
                    {JSON.stringify(event.details, null, 2)}
                  </pre>
                </Card>
              ))
            )}
          </div>
        )}
      </div>
    </section>
  );
}