import { useEffect, useMemo, useState } from 'react';
import { api } from './api';
import ActionPanel from './components/ActionPanel';
import AddMedicalRecordModal from './components/AddMedicalRecordModal';
import AgentTimeline from './components/AgentTimeline';
import ApprovalPanel from './components/ApprovalPanel';
import Dashboard from './components/Dashboard';
import OutputTabs from './components/OutputTabs';
import PatientManagement from './components/PatientManagement';
import PatientRecordTabs from './components/PatientRecordTabs';
import PatientSearchBar from './components/PatientSearchBar';
import PatientSelector from './components/PatientSelector';
import PatientTimeline from './components/PatientTimeline';
import VisitInput from './components/VisitInput';
import type {
  ActionExecutionResponse,
  AgentStep,
  ApprovalResponse,
  AuditLog,
  GeneratedWorkflowOutput,
  EmailSettings,
  MetricOut,
  Patient,
  PatientCreate,
  PatientHistory,
  PatientRecord,
  TimelineEvent,
  VisitInputState,
} from './types';

const defaultVisitInput: VisitInputState = {
  chief_complaint: 'Fatigue and increased thirst',
  symptoms: 'Fatigue, increased thirst, home glucose readings high, unsure medication adherence',
  vitals: 'BP 154/94, HR 82, BMI 29',
  doctor_notes: 'Patient missed last HbA1c test and reports irregular medication routine during travel.',
  assessment_notes: 'Doctor wants diabetes and blood pressure follow-up; no autonomous diagnosis requested.',
  suggested_plan: 'Discuss medication adherence, order HbA1c and kidney function labs, schedule BP follow-up, reinforce lifestyle counseling.',
};

const workflowStepNames = [
  'Patient Context Agent',
  'Clinical Note Agent',
  'Care Gap Agent',
  'Medication Safety Agent',
  'Patient Communication Agent',
  'Doctor Approval Step',
  'Task Orchestration Agent',
  'Compliance & Audit Agent',
  'Dashboard Update',
];

const delay = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

function initialSteps(): AgentStep[] {
  return workflowStepNames.map((name) => ({ name, status: 'queued', detail: 'Waiting to run.' }));
}

export default function App() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [history, setHistory] = useState<PatientHistory | null>(null);
  const [record, setRecord] = useState<PatientRecord | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [visitInput, setVisitInput] = useState<VisitInputState>(defaultVisitInput);
  const [metrics, setMetrics] = useState<MetricOut | null>(null);
  const [emailSettings, setEmailSettings] = useState<EmailSettings | null>(null);
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>(initialSteps());
  const [output, setOutput] = useState<GeneratedWorkflowOutput | null>(null);
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [execution, setExecution] = useState<ActionExecutionResponse | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isEmailBusy, setIsEmailBusy] = useState(false);
  const [query, setQuery] = useState('');
  const [addPatientOpen, setAddPatientOpen] = useState(false);
  const [addRecordOpen, setAddRecordOpen] = useState(false);

  const selectedPatientId = selectedPatient?.id ?? null;

  async function refreshPatients(nextQuery = query) {
    const patientList = nextQuery.trim() ? await api.searchPatients(nextQuery.trim()) : await api.getPatients();
    setPatients(patientList);
    return patientList;
  }

  async function refreshSelectedPatient(patientId: number) {
    const [patientHistory, patientRecord, patientTimeline] = await Promise.all([
      api.getPatientHistory(patientId),
      api.getPatientRecord(patientId),
      api.getPatientTimeline(patientId),
    ]);
    setHistory(patientHistory);
    setRecord(patientRecord);
    setTimeline(patientTimeline);
  }

  async function refreshMetrics() {
    const metricData = await api.getMetrics();
    setMetrics(metricData);
  }

  async function refreshEmailSettings() {
    const settings = await api.getEmailSettings();
    setEmailSettings(settings);
  }

  useEffect(() => {
    async function boot() {
      try {
        const [patientList] = await Promise.all([refreshPatients(''), refreshMetrics(), refreshEmailSettings()]);
        if (patientList.length > 0) {
          setSelectedPatient(patientList[0]);
          await refreshSelectedPatient(patientList[0].id);
        }
      } catch (bootError) {
        setError(bootError instanceof Error ? bootError.message : 'Unable to load app data. Is the backend running?');
      }
    }
    void boot();
  }, []);

  async function handleSearchChange(nextQuery: string) {
    setQuery(nextQuery);
    setError(null);
    try {
      await refreshPatients(nextQuery);
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : 'Patient search failed.');
    }
  }

  async function handleSelectPatient(patient: Patient) {
    setSelectedPatient(patient);
    setOutput(null);
    setApproval(null);
    setExecution(null);
    setAuditLogs([]);
    setAgentSteps(initialSteps());
    setError(null);
    try {
      await refreshSelectedPatient(patient.id);
    } catch (selectError) {
      setError(selectError instanceof Error ? selectError.message : 'Unable to load patient history.');
    }
  }

  async function handleCreatePatient(patient: PatientCreate) {
    const created = await api.createPatient(patient);
    const patientList = await refreshPatients('');
    setQuery('');
    setSelectedPatient(created);
    await refreshSelectedPatient(created.id);
    if (!patientList.some((item) => item.id === created.id)) {
      setPatients([created, ...patientList]);
    }
    await refreshMetrics();
  }

  async function handleAddMedicalRecord(type: string, payload: Record<string, string>) {
    if (!selectedPatient) return;
    if (type === 'condition') await api.addCondition(selectedPatient.id, payload as { name: string; status?: string; diagnosed_at?: string; notes?: string });
    if (type === 'allergy') await api.addAllergy(selectedPatient.id, payload as { allergen: string; reaction?: string; severity?: string; notes?: string });
    if (type === 'medication') await api.addMedication(selectedPatient.id, payload as { name: string; dose?: string; frequency?: string; notes?: string });
    if (type === 'lab') await api.addLab(selectedPatient.id, payload as { name: string; value: string; unit?: string; collected_at: string; status?: string });
    if (type === 'visit') await api.addPreviousVisit(selectedPatient.id, payload as { date: string; visit_type?: string; summary: string; plan?: string });
    if (type === 'task') await api.addTask(selectedPatient.id, payload as { title: string; task_type?: string; description?: string; owner?: string; status?: string });
    if (type === 'care_gap') await api.addCareGap(selectedPatient.id, payload as { gap: string; priority?: string; evidence?: string; recommended_follow_up_action?: string; status?: string });
    if (type === 'appointment') await api.addAppointment(selectedPatient.id, payload as { appointment_date: string; reason?: string; status?: string; notes?: string });
    await Promise.all([refreshSelectedPatient(selectedPatient.id), refreshMetrics(), refreshPatients(query)]);
  }

  async function refreshAfterEmailAction() {
    if (selectedPatient) await refreshSelectedPatient(selectedPatient.id);
    await Promise.all([refreshMetrics(), refreshEmailSettings()]);
  }

  async function handleSaveCommunication(communicationId: number, payload: { subject: string; body: string; recipient_email: string }) {
    setIsEmailBusy(true);
    setError(null);
    try {
      await api.updateCommunication(communicationId, payload);
      await refreshAfterEmailAction();
    } catch (emailError) {
      setError(emailError instanceof Error ? emailError.message : 'Unable to save email draft.');
    } finally {
      setIsEmailBusy(false);
    }
  }

  async function handleApproveCommunication(communicationId: number) {
    setIsEmailBusy(true);
    setError(null);
    try {
      await api.approveCommunication(communicationId);
      await refreshAfterEmailAction();
    } catch (emailError) {
      setError(emailError instanceof Error ? emailError.message : 'Unable to approve email draft.');
    } finally {
      setIsEmailBusy(false);
    }
  }

  async function handleSendCommunication(communicationId: number) {
    setIsEmailBusy(true);
    setError(null);
    try {
      const result = await api.sendCommunication(communicationId);
      if (result.status === 'Failed') setError(result.error_message || 'Email sending failed.');
      await refreshAfterEmailAction();
    } catch (emailError) {
      setError(emailError instanceof Error ? emailError.message : 'Unable to send email.');
    } finally {
      setIsEmailBusy(false);
    }
  }

  async function handleCancelCommunication(communicationId: number) {
    setIsEmailBusy(true);
    setError(null);
    try {
      await api.cancelCommunication(communicationId);
      await refreshAfterEmailAction();
    } catch (emailError) {
      setError(emailError instanceof Error ? emailError.message : 'Unable to cancel email draft.');
    } finally {
      setIsEmailBusy(false);
    }
  }

  async function animateAgentRun(workflowPromise: Promise<GeneratedWorkflowOutput>) {
    for (let index = 0; index < workflowStepNames.length; index += 1) {
      setAgentSteps((current) =>
        current.map((step, stepIndex) => {
          if (stepIndex < index) return { ...step, status: 'completed', detail: 'Completed.' };
          if (stepIndex === index) return { ...step, status: 'running', detail: 'Agent is processing this workflow step.' };
          return step;
        }),
      );
      await delay(index === 5 ? 200 : 350);
      if (index === 4) break;
    }

    const result = await workflowPromise;
    const backendSteps = result.agent_steps;
    const withApprovalStep: AgentStep[] = [
      ...backendSteps.slice(0, 5),
      { name: 'Doctor Approval Step', status: 'blocked', detail: 'Doctor must approve SOAP note, email, tasks, and medication instructions.' },
      ...backendSteps.slice(5),
      { name: 'Dashboard Update', status: 'queued', detail: 'Dashboard updates after approval and simulated action execution.' },
    ];
    setAgentSteps(withApprovalStep);
    return result;
  }

  async function handleRunAgents() {
    if (!selectedPatient) return;
    setError(null);
    setIsRunning(true);
    setOutput(null);
    setApproval(null);
    setExecution(null);
    setAuditLogs([]);
    setAgentSteps(initialSteps());

    try {
      const workflowPromise = api.runAgents(selectedPatient.id, visitInput).then((response) => response.output);
      const result = await animateAgentRun(workflowPromise);
      setOutput(result);
      const logs = await api.getAudit(result.visit_id);
      setAuditLogs(logs);
      await Promise.all([refreshMetrics(), refreshSelectedPatient(selectedPatient.id)]);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : 'Agent workflow failed.');
      setAgentSteps(initialSteps());
    } finally {
      setIsRunning(false);
    }
  }

  async function handleApprove() {
    if (!output) return;
    setIsApproving(true);
    setError(null);
    try {
      const approvalResult = await api.approve(output.visit_id);
      setApproval(approvalResult);
      setOutput({ ...output, approved: approvalResult.approved, doctor_approval: approvalResult.approval_status });
      setAgentSteps((current) =>
        current.map((step) =>
          step.name === 'Doctor Approval Step'
            ? { ...step, status: 'completed', detail: 'Doctor approved all generated drafts.' }
            : step.name === 'Task Orchestration Agent'
              ? { ...step, status: 'queued', detail: 'Ready to execute simulated actions.' }
              : step,
        ),
      );
      const logs = await api.getAudit(output.visit_id);
      setAuditLogs(logs);
      await Promise.all([refreshMetrics(), selectedPatient ? refreshSelectedPatient(selectedPatient.id) : Promise.resolve()]);
    } catch (approvalError) {
      setError(approvalError instanceof Error ? approvalError.message : 'Approval failed.');
    } finally {
      setIsApproving(false);
    }
  }

  async function handleExecute() {
    if (!output) return;
    setIsExecuting(true);
    setError(null);
    try {
      setAgentSteps((current) =>
        current.map((step) => (step.name === 'Task Orchestration Agent' ? { ...step, status: 'running', detail: 'Executing simulated actions.' } : step)),
      );
      const executionResult = await api.executeActions(output.visit_id);
      setExecution(executionResult);
      setOutput({ ...output, executed: true });
      setAgentSteps((current) =>
        current.map((step) => {
          if (step.name === 'Task Orchestration Agent') return { ...step, status: 'completed', detail: 'Mock EHR save, email queue, nurse task, lab reminder, and appointment follow-up completed.' };
          if (step.name === 'Compliance & Audit Agent') return { ...step, status: 'completed', detail: 'Post-execution audit trail recorded.' };
          if (step.name === 'Dashboard Update') return { ...step, status: 'completed', detail: 'Executive impact metrics refreshed.' };
          return step;
        }),
      );
      const [logs] = await Promise.all([api.getAudit(output.visit_id), refreshMetrics(), selectedPatient ? refreshSelectedPatient(selectedPatient.id) : Promise.resolve()]);
      setAuditLogs(logs);
    } catch (executeError) {
      setError(executeError instanceof Error ? executeError.message : 'Action execution failed.');
    } finally {
      setIsExecuting(false);
    }
  }

  const impactSummary = useMemo(() => {
    if (!metrics) return 'Run a workflow to calculate clinic impact.';
    return `${metrics.reduced_missed_follow_up_risk} • ${metrics.doctor_productivity_impact}`;
  }, [metrics]);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#dbeafe,_transparent_35%),linear-gradient(135deg,_#f8fafc,_#e0f2fe)] px-4 py-6 md:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <Dashboard metrics={metrics} />

        <section className="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-900">
          <strong>Demo safety guardrail:</strong> CareFlow MD uses mock records only. It does not diagnose, prescribe, or integrate with a real EHR. Agents draft emails; doctors send emails. Real SMTP is disabled unless explicitly enabled in backend environment variables.
        </section>

        {error && <section className="rounded-3xl border border-red-200 bg-red-50 p-5 text-sm font-semibold text-red-800">{error}</section>}

        <PatientSearchBar query={query} onQueryChange={handleSearchChange} onAddPatient={() => setAddPatientOpen(true)} patients={patients} />

        <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
          <div className="space-y-6">
            <PatientSelector patients={patients} selectedPatientId={selectedPatientId} onSelect={handleSelectPatient} />
            <VisitInput value={visitInput} onChange={setVisitInput} onRun={handleRunAgents} isRunning={isRunning} disabled={!selectedPatient} />
            <AgentTimeline steps={agentSteps} />
          </div>

          <div className="space-y-6">
            <PatientRecordTabs
              record={record}
              timeline={timeline}
              onAddRecord={() => setAddRecordOpen(true)}
              emailSettings={emailSettings}
              isEmailBusy={isEmailBusy}
              onSaveCommunication={handleSaveCommunication}
              onApproveCommunication={handleApproveCommunication}
              onSendCommunication={handleSendCommunication}
              onCancelCommunication={handleCancelCommunication}
            />
            <PatientTimeline history={history} />
            <OutputTabs output={output} auditLogs={auditLogs} />
            <div className="grid gap-6 lg:grid-cols-2">
              <ApprovalPanel output={output} approval={approval} onApprove={handleApprove} isApproving={isApproving} />
              <ActionPanel output={output} approval={approval} execution={execution} onExecute={handleExecute} isExecuting={isExecuting} />
            </div>
            <section className="card p-6">
              <p className="section-title">Executive impact dashboard</p>
              <h2 className="mt-2 text-2xl font-bold text-slate-950">Clinic transformation summary</h2>
              <p className="mt-3 text-slate-700">{impactSummary}</p>
              <div className="mt-5 grid gap-3 md:grid-cols-3">
                <div className="rounded-2xl bg-blue-50 p-4"><p className="text-sm font-semibold text-blue-700">Reduced missed follow-up risk</p><p className="mt-2 text-xl font-bold text-slate-950">{metrics?.reduced_missed_follow_up_risk ?? 'Pending'}</p></div>
                <div className="rounded-2xl bg-green-50 p-4"><p className="text-sm font-semibold text-green-700">Completed workflows</p><p className="mt-2 text-xl font-bold text-slate-950">{metrics?.completed_workflows ?? 0}</p></div>
                <div className="rounded-2xl bg-purple-50 p-4"><p className="text-sm font-semibold text-purple-700">Agentic differentiation</p><p className="mt-2 text-xl font-bold text-slate-950">Patient record to workflow</p></div>
              </div>
            </section>
          </div>
        </div>
      </div>
      <PatientManagement open={addPatientOpen} onClose={() => setAddPatientOpen(false)} onCreate={handleCreatePatient} />
      <AddMedicalRecordModal open={addRecordOpen} onClose={() => setAddRecordOpen(false)} onAdd={handleAddMedicalRecord} />
    </main>
  );
}
