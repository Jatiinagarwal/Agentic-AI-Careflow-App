import { useState } from 'react';
import type { ReactNode } from 'react';
import type { AuditLog, GeneratedWorkflowOutput } from '../types';

type Props = {
  output: GeneratedWorkflowOutput | null;
  auditLogs: AuditLog[];
};

type TabId = 'soap' | 'summary' | 'gaps' | 'safety' | 'email' | 'tasks' | 'audit';

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'soap', label: 'SOAP Note' },
  { id: 'summary', label: 'History Summary' },
  { id: 'gaps', label: 'Care Gaps' },
  { id: 'safety', label: 'Medication Safety' },
  { id: 'email', label: 'Patient Email' },
  { id: 'tasks', label: 'Follow-up Tasks' },
  { id: 'audit', label: 'Audit Trail' },
];

function Pre({ children }: { children: string }) {
  return <pre className="whitespace-pre-wrap rounded-2xl bg-slate-950 p-5 text-sm leading-6 text-slate-100">{children}</pre>;
}

function Badge({ children }: { children: ReactNode }) {
  return <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">{children}</span>;
}

export default function OutputTabs({ output, auditLogs }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('soap');

  if (!output) {
    return (
      <section className="card p-6">
        <p className="section-title">Generated outputs</p>
        <h2 className="mt-2 text-2xl font-bold text-slate-950">Drafts appear here after agents run</h2>
        <p className="mt-3 text-sm text-slate-600">
          The system will show SOAP note, care gaps, safety flags, patient communication, proposed tasks, and audit events.
        </p>
      </section>
    );
  }

  return (
    <section className="card p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="section-title">Generated outputs</p>
          <h2 className="mt-2 text-2xl font-bold text-slate-950">Doctor-review draft workspace</h2>
        </div>
        <Badge>Visit #{output.visit_id}</Badge>
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
        {activeTab === 'soap' && <Pre>{output.soap_note.full_note}</Pre>}

        {activeTab === 'summary' && (
          <div className="space-y-4">
            <Pre>{output.patient_context_summary}</Pre>
            <div className="grid gap-3 md:grid-cols-2">
              {output.risk_factors.map((risk) => (
                <div key={risk} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                  {risk}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'gaps' && (
          <div className="space-y-3">
            {output.care_gaps.map((gap) => (
              <div key={gap.gap} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-bold text-slate-950">{gap.gap}</h3>
                  <span className="rounded-full bg-red-50 px-3 py-1 text-xs font-bold text-red-700">{gap.priority}</span>
                </div>
                <p className="mt-2 text-sm text-slate-600">{gap.evidence}</p>
                <p className="mt-2 text-sm font-semibold text-blue-700">Action: {gap.recommended_follow_up_action}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'safety' && (
          <div className="space-y-3">
            <p className="rounded-2xl bg-amber-50 p-4 text-sm font-semibold text-amber-800">
              Decision support only. Mock rules. Doctor review required.
            </p>
            {output.medication_safety.map((flag) => (
              <div key={flag.flag} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-bold text-slate-950">{flag.flag}</h3>
                  <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700">{flag.severity}</span>
                </div>
                <p className="mt-2 text-sm text-slate-600">{flag.mock_rule}</p>
                <p className="mt-2 text-sm font-semibold text-slate-800">{flag.doctor_review_note}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'email' && (
          <div className="space-y-4">
            <Pre>{output.patient_email_draft}</Pre>
            <Pre>{output.medication_instruction_draft}</Pre>
            <p className="rounded-2xl bg-blue-50 p-4 text-sm font-semibold text-blue-800">{output.follow_up_summary}</p>
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="space-y-3">
            {output.proposed_tasks.map((task) => (
              <div key={`${task.task_type}-${task.title}`} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-bold text-slate-950">{task.title}</h3>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{task.owner}</span>
                </div>
                <p className="mt-2 text-sm text-slate-600">{task.description}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'audit' && (
          <div className="space-y-3">
            {auditLogs.length === 0 && <p className="text-sm text-slate-600">Audit events will load after workflow execution.</p>}
            {auditLogs.map((event) => (
              <div key={event.id} className="rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h3 className="font-bold text-slate-950">{event.event_type}</h3>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{event.actor}</span>
                </div>
                <p className="mt-1 text-xs text-slate-500">{new Date(event.created_at).toLocaleString()}</p>
                <Pre>{JSON.stringify(event.details, null, 2)}</Pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

