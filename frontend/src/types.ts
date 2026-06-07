export type Patient = {
  id: number;
  name: string;
  age: number;
  gender: string;
  conditions: string[];
  risk_factors: string[];
};

export type Medication = {
  id: number;
  name: string;
  dose: string;
  frequency: string;
  notes: string;
};

export type Lab = {
  id: number;
  name: string;
  value: string;
  unit: string;
  collected_at: string;
  status: string;
};

export type PreviousVisit = {
  id: number;
  date: string;
  visit_type: string;
  summary: string;
  plan: string;
};

export type PatientHistory = {
  patient: Patient;
  medications: Medication[];
  labs: Lab[];
  previous_visits: PreviousVisit[];
};

export type VisitInputState = {
  chief_complaint: string;
  symptoms: string;
  vitals: string;
  doctor_notes: string;
  assessment_notes: string;
  suggested_plan: string;
};

export type AgentStep = {
  name: string;
  status: 'queued' | 'running' | 'completed' | 'blocked' | string;
  detail: string;
  timestamp?: string;
};

export type CareGap = {
  gap: string;
  priority: string;
  evidence: string;
  recommended_follow_up_action: string;
};

export type MedicationSafetyFlag = {
  severity: string;
  flag: string;
  mock_rule: string;
  doctor_review_note: string;
};

export type ProposedTask = {
  task_type: string;
  title: string;
  description: string;
  owner: string;
};

export type GeneratedWorkflowOutput = {
  visit_id: number;
  patient_context_summary: string;
  relevant_history: PreviousVisit[];
  risk_factors: string[];
  recent_labs: Lab[];
  medication_list: Medication[];
  soap_note: {
    subjective: string;
    objective: string;
    assessment_draft: string;
    plan_draft: string;
    doctor_review_required_flag: boolean;
    full_note: string;
  };
  care_gaps: CareGap[];
  medication_safety: MedicationSafetyFlag[];
  patient_email_draft: string;
  medication_instruction_draft: string;
  follow_up_summary: string;
  proposed_tasks: ProposedTask[];
  agent_steps: AgentStep[];
  doctor_approval: Record<string, unknown>;
  approved: boolean;
  executed: boolean;
};

export type AgentRunResponse = {
  message: string;
  output: GeneratedWorkflowOutput;
};

export type ApprovalResponse = {
  visit_id: number;
  approved: boolean;
  approval_status: Record<string, unknown>;
  message: string;
};

export type ActionExecutionResponse = {
  visit_id: number;
  executed: boolean;
  action_log: Array<{ action: string; status: string; detail: string }>;
  task_statuses: Array<{ id: number; task_type: string; title: string; owner: string; status: string }>;
  safety_status: string;
  message: string;
};

export type MetricOut = {
  documentation_time_saved_minutes: number;
  care_gaps_detected: number;
  follow_up_tasks_created: number;
  drafts_awaiting_approval: number;
  simulated_patient_communication_rate: number;
  reduced_missed_follow_up_risk: string;
  doctor_productivity_impact: string;
  completed_workflows: number;
};

export type AuditLog = {
  id: number;
  visit_id: number | null;
  actor: string;
  event_type: string;
  details: Record<string, unknown>;
  created_at: string;
};
