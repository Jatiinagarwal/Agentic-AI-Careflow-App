import type {
  ActionExecutionResponse,
  AgentRunResponse,
  Allergy,
  Appointment,
  ApprovalResponse,
  AuditLog,
  CareGapRecord,
  CommunicationDraft,
  ConditionRecord,
  GeneratedWorkflowOutput,
  Lab,
  Medication,
  MetricOut,
  Patient,
  PatientCreate,
  PatientHistory,
  PatientRecord,
  PatientSummary,
  PreviousVisit,
  Task,
  TimelineEvent,
  VisitInputState,
} from './types';

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const API_BASE_URL = (rawApiBaseUrl && rawApiBaseUrl.length > 0 ? rawApiBaseUrl : 'http://localhost:8000').replace(/\/+$/, '');

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const errorBody = await response.json();
      message = errorBody.detail ?? message;
    } catch {
      // Keep default message when backend response is not JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getPatients: () => request<Patient[]>('/patients'),
  searchPatients: (query: string) => request<Patient[]>(`/patients/search?query=${encodeURIComponent(query)}`),
  createPatient: (payload: PatientCreate) =>
    request<Patient>('/patients', { method: 'POST', body: JSON.stringify(payload) }),
  updatePatient: (patientId: number, payload: Partial<Patient>) =>
    request<Patient>(`/patients/${patientId}`, { method: 'PUT', body: JSON.stringify(payload) }),
  getPatientHistory: (patientId: number) => request<PatientHistory>(`/patients/${patientId}/history`),
  getPatientRecord: (patientId: number) => request<PatientRecord>(`/patients/${patientId}/record`),
  getPatientTimeline: (patientId: number) => request<TimelineEvent[]>(`/patients/${patientId}/timeline`),
  getPatientAudit: (patientId: number) => request<AuditLog[]>(`/patients/${patientId}/audit`),
  getPatientCommunications: (patientId: number) => request<CommunicationDraft[]>(`/patients/${patientId}/communications`),
  addCondition: (patientId: number, payload: { name: string; status?: string; diagnosed_at?: string; notes?: string }) =>
    request<ConditionRecord>(`/patients/${patientId}/conditions`, { method: 'POST', body: JSON.stringify(payload) }),
  addAllergy: (patientId: number, payload: { allergen: string; reaction?: string; severity?: string; notes?: string }) =>
    request<Allergy>(`/patients/${patientId}/allergies`, { method: 'POST', body: JSON.stringify(payload) }),
  addMedication: (patientId: number, payload: { name: string; dose?: string; frequency?: string; notes?: string }) =>
    request<Medication>(`/patients/${patientId}/medications`, { method: 'POST', body: JSON.stringify(payload) }),
  addLab: (patientId: number, payload: { name: string; value: string; unit?: string; collected_at: string; status?: string }) =>
    request<Lab>(`/patients/${patientId}/labs`, { method: 'POST', body: JSON.stringify(payload) }),
  addPreviousVisit: (patientId: number, payload: { date: string; visit_type?: string; summary: string; plan?: string }) =>
    request<PreviousVisit>(`/patients/${patientId}/visits`, { method: 'POST', body: JSON.stringify(payload) }),
  addCareGap: (patientId: number, payload: { gap: string; priority?: string; evidence?: string; recommended_follow_up_action?: string; status?: string }) =>
    request<CareGapRecord>(`/patients/${patientId}/care-gaps`, { method: 'POST', body: JSON.stringify(payload) }),
  addTask: (patientId: number, payload: { task_type?: string; title: string; description?: string; owner?: string; status?: string }) =>
    request<Task>(`/patients/${patientId}/tasks`, { method: 'POST', body: JSON.stringify(payload) }),
  addAppointment: (patientId: number, payload: { appointment_date: string; reason?: string; status?: string; notes?: string }) =>
    request<Appointment>(`/patients/${patientId}/appointments`, { method: 'POST', body: JSON.stringify(payload) }),
  mockSendCommunication: (communicationId: number) =>
    request<CommunicationDraft>(`/communications/${communicationId}/mock-send`, { method: 'POST' }),
  runAgents: (patientId: number, currentVisit: VisitInputState) =>
    request<AgentRunResponse>('/agents/run', { method: 'POST', body: JSON.stringify({ patient_id: patientId, current_visit: currentVisit }) }),
  approve: (visitId: number) =>
    request<ApprovalResponse>('/approval/approve', {
      method: 'POST',
      body: JSON.stringify({
        visit_id: visitId,
        doctor_name: 'Dr. Sharma',
        approve_soap_note: true,
        approve_patient_email: true,
        approve_follow_up_tasks: true,
        approve_medication_instructions: true,
      }),
    }),
  executeActions: (visitId: number) =>
    request<ActionExecutionResponse>('/actions/execute', { method: 'POST', body: JSON.stringify({ visit_id: visitId }) }),
  getMetrics: () => request<MetricOut>('/dashboard/metrics'),
  getPatientSummary: (patientId: number) => request<PatientSummary>(`/dashboard/patient-summary/${patientId}`),
  getAudit: (visitId: number) => request<AuditLog[]>(`/audit/${visitId}`),
};

export type { GeneratedWorkflowOutput };
