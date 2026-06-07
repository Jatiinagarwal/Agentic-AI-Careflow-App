from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: str
    conditions: list[str]
    risk_factors: list[str]


class MedicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    dose: str
    frequency: str
    notes: str


class LabOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    value: str
    unit: str
    collected_at: str
    status: str


class PreviousVisitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: str
    visit_type: str
    summary: str
    plan: str


class PatientHistoryOut(BaseModel):
    patient: PatientOut
    medications: list[MedicationOut]
    labs: list[LabOut]
    previous_visits: list[PreviousVisitOut]


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


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int | None
    actor: str
    event_type: str
    details: dict[str, Any]
    created_at: datetime
