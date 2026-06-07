from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PatientBase(BaseModel):
    first_name: str = ""
    last_name: str = ""
    name: str = ""
    date_of_birth: str = ""
    age: int = 0
    gender: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    primary_physician: str = "Dr. Sharma"
    preferred_language: str = "English"
    consent_for_mock_email: bool = True
    risk_level: str = "Moderate"
    status: str = "Active"
    conditions: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)


class PatientCreate(PatientBase):
    first_name: str
    last_name: str
    age: int
    gender: str


class PatientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    date_of_birth: str | None = None
    age: int | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    primary_physician: str | None = None
    preferred_language: str | None = None
    consent_for_mock_email: bool | None = None
    risk_level: str | None = None
    status: str | None = None
    conditions: list[str] | None = None
    risk_factors: list[str] | None = None


class PatientOut(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime | None = None


class ConditionCreate(BaseModel):
    name: str
    status: str = "Active"
    diagnosed_at: str = ""
    notes: str = ""


class ConditionOut(ConditionCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    created_at: datetime


class AllergyCreate(BaseModel):
    allergen: str
    reaction: str = ""
    severity: str = "Unknown"
    notes: str = ""


class AllergyOut(AllergyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    created_at: datetime


class MedicationCreate(BaseModel):
    name: str
    dose: str = ""
    frequency: str = ""
    notes: str = ""


class MedicationOut(MedicationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LabCreate(BaseModel):
    name: str
    value: str
    unit: str = ""
    collected_at: str
    status: str = "available"


class LabOut(LabCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PreviousVisitCreate(BaseModel):
    date: str
    visit_type: str = "Follow-up"
    summary: str
    plan: str = ""


class PreviousVisitOut(PreviousVisitCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CareGapCreate(BaseModel):
    gap: str
    priority: str = "Medium"
    evidence: str = ""
    recommended_follow_up_action: str = ""
    status: str = "Open"


class CareGapOut(CareGapCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    visit_id: int | None = None
    created_at: datetime


class TaskCreate(BaseModel):
    task_type: str = "follow_up"
    title: str
    description: str = ""
    owner: str = "Clinic team"
    status: str = "created"


class TaskOut(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int | None = None
    visit_id: int | None = None
    created_at: datetime


class AppointmentCreate(BaseModel):
    appointment_date: str
    reason: str = "Follow-up"
    status: str = "Scheduled"
    notes: str = ""


class AppointmentOut(AppointmentCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    created_at: datetime


class CommunicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    visit_id: int | None = None
    subject: str
    body: str
    instruction_draft: str
    follow_up_summary: str
    status: str
    safety_label: str
    created_at: datetime
    updated_at: datetime


class PatientHistoryOut(BaseModel):
    patient: PatientOut
    medications: list[MedicationOut]
    labs: list[LabOut]
    previous_visits: list[PreviousVisitOut]


class PatientRecordOut(BaseModel):
    patient: PatientOut
    conditions: list[ConditionOut]
    allergies: list[AllergyOut]
    medications: list[MedicationOut]
    labs: list[LabOut]
    previous_visits: list[PreviousVisitOut]
    care_gaps: list[CareGapOut]
    communications: list[CommunicationOut]
    tasks: list[TaskOut]
    appointments: list[AppointmentOut]
    audit_logs: list[dict[str, Any]]


class TimelineEventOut(BaseModel):
    id: str
    date: str
    type: str
    title: str
    description: str
    status: str = ""


class PatientSummaryOut(BaseModel):
    patient_id: int
    active_conditions: int
    open_care_gaps: int
    open_tasks: int
    queued_emails: int
    mock_sent_emails: int
    latest_visit_status: str
    risk_level: str


class VisitInput(BaseModel):
    chief_complaint: str = Field(default="Fatigue and increased thirst")
    symptoms: str = Field(default="Fatigue, increased thirst, home glucose readings high, unsure medication adherence")
    vitals: str = Field(default="BP 154/94, HR 82, BMI 29")
    doctor_notes: str = Field(default="Patient missed last HbA1c test and reports irregular medication routine during travel.")
    assessment_notes: str = Field(default="Doctor wants diabetes and blood pressure follow-up; no autonomous diagnosis requested.")
    suggested_plan: str = Field(default="Discuss medication adherence, order HbA1c and kidney function labs, schedule BP follow-up, reinforce lifestyle counseling.")


class VisitStartRequest(VisitInput):
    patient_id: int


class VisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chief_complaint: str
    symptoms: str
    vitals: str
    doctor_notes: str
    assessment_notes: str
    suggested_plan: str
    status: str
    created_at: datetime


class AgentRunRequest(BaseModel):
    patient_id: int
    visit_id: int | None = None
    current_visit: VisitInput = Field(default_factory=VisitInput)


class GeneratedWorkflowOutput(BaseModel):
    visit_id: int
    patient_context_summary: str
    relevant_history: list[dict[str, Any]]
    risk_factors: list[str]
    recent_labs: list[dict[str, Any]]
    medication_list: list[dict[str, Any]]
    soap_note: dict[str, Any]
    care_gaps: list[dict[str, Any]]
    medication_safety: list[dict[str, Any]]
    patient_email_draft: str
    medication_instruction_draft: str
    follow_up_summary: str
    proposed_tasks: list[dict[str, Any]]
    agent_steps: list[dict[str, Any]]
    doctor_approval: dict[str, Any]
    approved: bool
    executed: bool


class AgentRunResponse(BaseModel):
    message: str
    output: GeneratedWorkflowOutput


class ApprovalRequest(BaseModel):
    visit_id: int
    doctor_name: str = "Dr. Sharma"
    approve_soap_note: bool = True
    approve_patient_email: bool = True
    approve_follow_up_tasks: bool = True
    approve_medication_instructions: bool = True


class ApprovalResponse(BaseModel):
    visit_id: int
    approved: bool
    approval_status: dict[str, Any]
    message: str


class ActionExecutionRequest(BaseModel):
    visit_id: int


class ActionExecutionResponse(BaseModel):
    visit_id: int
    executed: bool
    action_log: list[dict[str, Any]]
    task_statuses: list[dict[str, Any]]
    safety_status: str
    message: str


class MetricOut(BaseModel):
    documentation_time_saved_minutes: int
    care_gaps_detected: int
    follow_up_tasks_created: int
    drafts_awaiting_approval: int
    simulated_patient_communication_rate: int
    reduced_missed_follow_up_risk: str
    doctor_productivity_impact: str
    completed_workflows: int
    total_active_patients: int = 0
    patients_with_overdue_care_gaps: int = 0
    emails_queued: int = 0
    mock_emails_sent: int = 0
    follow_up_tasks_open: int = 0
    actions_completed_after_approval: int = 0


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int | None = None
    visit_id: int | None
    actor: str
    event_type: str
    details: dict[str, Any]
    created_at: datetime
