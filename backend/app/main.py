from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agent_orchestrator import AgentOrchestrator
from app.agents.compliance_audit_agent import ComplianceAuditAgent
from app.agents.task_orchestration_agent import TaskOrchestrationAgent
from app.config import get_settings
from app.database import SessionLocal, get_db, init_db
from app.models import CommunicationDraft, GeneratedOutput, Task, Visit
from app.schemas import (
    ActionExecutionRequest,
    ActionExecutionResponse,
    AgentRunRequest,
    AgentRunResponse,
    AllergyCreate,
    AllergyOut,
    AppointmentCreate,
    AppointmentOut,
    ApprovalRequest,
    ApprovalResponse,
    AuditLogOut,
    CareGapCreate,
    CareGapOut,
    CommunicationOut,
    TestEmailRequest,
    EmailSettingsResponse,
    EmailSendResponse,
    EmailDraftUpdate,
    EmailApprovalRequest,
    ConditionCreate,
    ConditionOut,
    GeneratedWorkflowOutput,
    LabCreate,
    LabOut,
    MedicationCreate,
    MedicationOut,
    MetricOut,
    PatientCreate,
    PatientHistoryOut,
    PatientOut,
    PatientRecordOut,
    PatientSummaryOut,
    PatientUpdate,
    PreviousVisitCreate,
    PreviousVisitOut,
    TaskCreate,
    TaskOut,
    TimelineEventOut,
    VisitOut,
    VisitStartRequest,
)
from app.seed_data import seed_database
from app.services import audit_service, communication_service, dashboard_service, email_service, medical_record_service, patient_service, visit_service

settings = get_settings()
app = FastAPI(title="CareFlow MD API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = AgentOrchestrator()
task_agent = TaskOrchestrationAgent()
compliance_agent = ComplianceAuditAgent()


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "message": "CareFlow MD API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@app.get("/patients/search", response_model=list[PatientOut])
def search_patients(query: str = "", db: Session = Depends(get_db)):
    return patient_service.search_patients(db, query)


@app.get("/patients", response_model=list[PatientOut])
def get_patients(db: Session = Depends(get_db)):
    return patient_service.list_patients(db)


@app.post("/patients", response_model=PatientOut)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    patient = patient_service.create_patient(db, payload)
    audit_service.log_event(db, None, "clinic_staff", "patient_created", {"patient_id": patient.id}, patient_id=patient.id)
    return patient


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    updated = patient_service.update_patient(db, patient, payload)
    audit_service.log_event(db, None, "clinic_staff", "patient_updated", {"patient_id": patient_id}, patient_id=patient_id)
    return updated


@app.get("/patients/{patient_id}/history", response_model=PatientHistoryOut)
def get_patient_history(patient_id: int, db: Session = Depends(get_db)):
    try:
        return patient_service.get_patient_history(db, patient_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/patients/{patient_id}/record", response_model=PatientRecordOut)
def get_patient_record(patient_id: int, db: Session = Depends(get_db)):
    try:
        return patient_service.get_patient_record(db, patient_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/patients/{patient_id}/timeline", response_model=list[TimelineEventOut])
def get_patient_timeline(patient_id: int, db: Session = Depends(get_db)):
    try:
        return patient_service.get_patient_timeline(db, patient_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/conditions", response_model=ConditionOut)
def add_condition(patient_id: int, payload: ConditionCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_condition(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "condition_added", {"name": record.name}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/allergies", response_model=AllergyOut)
def add_allergy(patient_id: int, payload: AllergyCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_allergy(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "allergy_added", {"allergen": record.allergen}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/medications", response_model=MedicationOut)
def add_medication(patient_id: int, payload: MedicationCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_medication(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "medication_added", {"name": record.name}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/labs", response_model=LabOut)
def add_lab(patient_id: int, payload: LabCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_lab(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "lab_added", {"name": record.name, "value": record.value}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/visits", response_model=PreviousVisitOut)
def add_previous_visit(patient_id: int, payload: PreviousVisitCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_previous_visit(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "previous_visit_added", {"visit_type": record.visit_type}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/care-gaps", response_model=CareGapOut)
def add_care_gap(patient_id: int, payload: CareGapCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_care_gap(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "manual_care_gap_added", {"gap": record.gap}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/tasks", response_model=TaskOut)
def add_task(patient_id: int, payload: TaskCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_task(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "task_added", {"title": record.title}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/patients/{patient_id}/appointments", response_model=AppointmentOut)
def add_appointment(patient_id: int, payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        record = medical_record_service.add_appointment(db, patient_id, payload)
        audit_service.log_event(db, None, "clinic_staff", "appointment_added", {"reason": record.reason}, patient_id=patient_id)
        return record
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/patients/{patient_id}/communications", response_model=list[CommunicationOut])
def get_patient_communications(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return communication_service.list_patient_communications(db, patient_id)


@app.get("/settings/email", response_model=EmailSettingsResponse)
def get_email_settings():
    return email_service.email_settings_safe()


@app.get("/communications/{communication_id}", response_model=CommunicationOut)
def get_communication(communication_id: int, db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    return communication


@app.put("/communications/{communication_id}", response_model=CommunicationOut)
def update_communication(communication_id: int, payload: EmailDraftUpdate, db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    try:
        return communication_service.update_email_draft(db, communication, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/communications/{communication_id}/approve", response_model=CommunicationOut)
def approve_communication(communication_id: int, payload: EmailApprovalRequest = EmailApprovalRequest(), db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    try:
        return communication_service.approve_email_draft(db, communication, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/communications/{communication_id}/send", response_model=EmailSendResponse)
def send_communication(communication_id: int, db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    try:
        updated = communication_service.send_email_draft(db, communication)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "communication": updated,
        "status": updated.status,
        "provider": updated.provider,
        "provider_message_id": updated.provider_message_id,
        "error_message": updated.error_message,
        "sent_at": updated.sent_at,
        "message": "Email sent." if updated.status == "Sent" else "Real email disabled; recorded as Mock Sent." if updated.status == "Mock Sent" else f"Email failed: {updated.error_message}",
    }


@app.post("/communications/{communication_id}/cancel", response_model=CommunicationOut)
def cancel_communication(communication_id: int, db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    try:
        return communication_service.cancel_email_draft(db, communication)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/communications/{communication_id}/mock-send", response_model=CommunicationOut)
def mock_send_communication(communication_id: int, db: Session = Depends(get_db)):
    communication = communication_service.get_communication(db, communication_id)
    if not communication:
        raise HTTPException(status_code=404, detail="Communication draft not found")
    try:
        return communication_service.send_email_draft(db, communication)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/communications/test-email")
def send_test_email(payload: TestEmailRequest, db: Session = Depends(get_db)):
    result = communication_service.send_test_email(db, payload)
    if result.get("status") == "Failed":
        raise HTTPException(status_code=400, detail=result.get("error_message") or result.get("message"))
    return result


@app.get("/patients/{patient_id}/audit", response_model=list[AuditLogOut])
def get_patient_audit(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return audit_service.get_patient_audit_logs(db, patient_id)


@app.post("/visits/start", response_model=VisitOut)
def start_visit(payload: VisitStartRequest, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    visit = visit_service.start_visit(db, payload)
    audit_service.log_event(db, visit.id, "doctor", "visit_started", {"patient_id": payload.patient_id})
    return visit


@app.post("/agents/run", response_model=AgentRunResponse)
def run_agents(payload: AgentRunRequest, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        output = orchestrator.run_workflow(db, payload)
        return {"message": "Draft workflow generated. Doctor approval is required before simulated actions.", "output": output}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/approval/approve", response_model=ApprovalResponse)
def approve_outputs(payload: ApprovalRequest, db: Session = Depends(get_db)):
    generated = db.query(GeneratedOutput).filter(GeneratedOutput.visit_id == payload.visit_id).first()
    visit = visit_service.get_visit(db, payload.visit_id)
    if not generated or not visit:
        raise HTTPException(status_code=404, detail="Generated workflow not found for visit")

    approval = {
        "soap_note": payload.approve_soap_note,
        "patient_email": payload.approve_patient_email,
        "follow_up_tasks": payload.approve_follow_up_tasks,
        "medication_instructions": payload.approve_medication_instructions,
    }
    compliance = compliance_agent.post_approval_check(approval)
    generated.doctor_approval = {**approval, "doctor_name": payload.doctor_name, "status": compliance["approval_status"]}
    generated.approved = compliance["approval_status"] == "approved_for_simulated_execution"
    visit.status = "approved" if generated.approved else "approval_incomplete"
    if generated.approved:
        draft = db.query(CommunicationDraft).filter(CommunicationDraft.visit_id == visit.id).first()
        if draft:
            communication_service.set_status(db, draft, "Approved")
    db.commit()

    audit_service.log_event(db, payload.visit_id, payload.doctor_name, "doctor_approval_recorded", {"approval": generated.doctor_approval, "compliance": compliance})

    return {"visit_id": payload.visit_id, "approved": generated.approved, "approval_status": generated.doctor_approval, "message": "Doctor approval recorded. Simulated actions may now run." if generated.approved else "Approval incomplete. Actions remain blocked."}


@app.post("/actions/execute", response_model=ActionExecutionResponse)
def execute_actions(payload: ActionExecutionRequest, db: Session = Depends(get_db)):
    visit = visit_service.get_visit(db, payload.visit_id)
    generated = db.query(GeneratedOutput).filter(GeneratedOutput.visit_id == payload.visit_id).first()
    if not visit or not generated:
        raise HTTPException(status_code=404, detail="Visit or generated workflow not found")
    if not generated.approved:
        raise HTTPException(status_code=400, detail="Doctor approval required before executing simulated actions")

    result = task_agent.execute(db, visit, generated)
    communication_service.queue_for_visit(db, visit.id)
    compliance = compliance_agent.post_execution_check()
    generated.executed = True
    visit.status = "completed"

    updated_steps = []
    for step in generated.agent_steps:
        if step.get("name") == "Task Orchestration Agent":
            updated_steps.append({**step, "status": "completed", "detail": "Simulated EHR save, email queue, lab reminders, and tasks were created after approval."})
        else:
            updated_steps.append(step)
    generated.agent_steps = updated_steps
    db.commit()

    audit_service.log_event(db, payload.visit_id, "Task Orchestration Agent", "simulated_actions_executed", result)
    audit_service.log_event(db, payload.visit_id, "Compliance & Audit Agent", "post_execution_check", compliance)

    return {"visit_id": payload.visit_id, "executed": True, "action_log": result["action_log"], "task_statuses": result["task_statuses"], "safety_status": compliance["safety_status"], "message": "Approved simulated care coordination actions completed with audit trail."}


@app.get("/dashboard/metrics", response_model=MetricOut)
def dashboard_metrics(db: Session = Depends(get_db)):
    return dashboard_service.metrics(db)


@app.get("/dashboard/patient-summary/{patient_id}", response_model=PatientSummaryOut)
def dashboard_patient_summary(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dashboard_service.patient_summary(db, patient_id)


@app.get("/audit/{visit_id}", response_model=list[AuditLogOut])
def get_audit_log(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return audit_service.get_audit_logs(db, visit_id)
