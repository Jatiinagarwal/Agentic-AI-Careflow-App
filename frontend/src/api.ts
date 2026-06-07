import type {
  ActionExecutionResponse,
  AgentRunResponse,
  ApprovalResponse,
  AuditLog,
  GeneratedWorkflowOutput,
  MetricOut,
  Patient,
  PatientHistory,
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
      // Keep default message when the backend response is not JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export const api = {
  getPatients: () => request<Patient[]>('/patients'),
  getPatientHistory: (patientId: number) => request<PatientHistory>(`/patients/${patientId}/history`),
  runAgents: (patientId: number, currentVisit: VisitInputState) =>
    request<AgentRunResponse>('/agents/run', {
      method: 'POST',
      body: JSON.stringify({ patient_id: patientId, current_visit: currentVisit }),
    }),
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
    request<ActionExecutionResponse>('/actions/execute', {
      method: 'POST',
      body: JSON.stringify({ visit_id: visitId }),
    }),
  getMetrics: () => request<MetricOut>('/dashboard/metrics'),
  getAudit: (visitId: number) => request<AuditLog[]>(`/audit/${visitId}`),
};

export type { GeneratedWorkflowOutput };
