from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.agent_orchestrator import AgentOrchestrator
from app.agents.compliance_audit_agent import ComplianceAuditAgent
from app.agents.task_orchestration_agent import TaskOrchestrationAgent
from app.config import get_settings
from app.database import SessionLocal, get_db, init_db
from app.models import GeneratedOutput, Task, Visit
from app.schemas import (
    ActionExecutionRequest,
    ActionExecutionResponse,
    AgentRunRequest,
    AgentRunResponse,
    ApprovalRequest,
    ApprovalResponse,
    AuditLogOut,
    GeneratedWorkflowOutput,
    MetricOut,
    PatientHistoryOut,
    PatientOut,
    VisitOut,
    VisitStartRequest,
)
from app.seed_data import seed_database
from app.services import audit_service, patient_service, task_service, visit_service

settings = get_settings()
app = FastAPI(title="CareFlow MD API", version="1.0.0")

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


@app.get("/patients", response_model=list[PatientOut])
def get_patients(db: Session = Depends(get_db)):
    return patient_service.list_patients(db)


@app.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = patient_service.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@app.get("/patients/{patient_id}/history", response_model=PatientHistoryOut)
def get_patient_history(patient_id: int, db: Session = Depends(get_db)):
    try:
        history = patient_service.get_patient_history(db, patient_id)
        return history
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


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
    generated.doctor_approval = {
        **approval,
        "doctor_name": payload.doctor_name,
        "status": compliance["approval_status"],
    }
    generated.approved = compliance["approval_status"] == "approved_for_simulated_execution"
    visit.status = "approved" if generated.approved else "approval_incomplete"
    db.commit()

    audit_service.log_event(
        db,
        payload.visit_id,
        payload.doctor_name,
        "doctor_approval_recorded",
        {"approval": generated.doctor_approval, "compliance": compliance},
    )

    return {
        "visit_id": payload.visit_id,
        "approved": generated.approved,
        "approval_status": generated.doctor_approval,
        "message": "Doctor approval recorded. Simulated actions may now run." if generated.approved else "Approval incomplete. Actions remain blocked.",
    }


@app.post("/actions/execute", response_model=ActionExecutionResponse)
def execute_actions(payload: ActionExecutionRequest, db: Session = Depends(get_db)):
    visit = visit_service.get_visit(db, payload.visit_id)
    generated = db.query(GeneratedOutput).filter(GeneratedOutput.visit_id == payload.visit_id).first()
    if not visit or not generated:
        raise HTTPException(status_code=404, detail="Visit or generated workflow not found")
    if not generated.approved:
        raise HTTPException(status_code=400, detail="Doctor approval required before executing simulated actions")

    result = task_agent.execute(db, visit, generated)
    compliance = compliance_agent.post_execution_check()
    generated.executed = True
    visit.status = "completed"

    # Mark task-orchestration agent as completed in the visible timeline.
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

    return {
        "visit_id": payload.visit_id,
        "executed": True,
        "action_log": result["action_log"],
        "task_statuses": result["task_statuses"],
        "safety_status": compliance["safety_status"],
        "message": "Approved simulated care coordination actions completed with audit trail.",
    }


@app.get("/dashboard/metrics", response_model=MetricOut)
def dashboard_metrics(db: Session = Depends(get_db)):
    generated_outputs = db.query(GeneratedOutput).all()
    completed_workflows = len([output for output in generated_outputs if output.executed])
    drafts_awaiting_approval = len([output for output in generated_outputs if not output.approved])
    care_gaps_detected = sum(len(output.care_gaps or []) for output in generated_outputs)
    tasks_created = db.query(Task).count()
    emails_queued = len([output for output in generated_outputs if output.executed and output.patient_email_draft])
    denominator = completed_workflows if completed_workflows else 1

    return {
        "documentation_time_saved_minutes": len(generated_outputs) * 18,
        "care_gaps_detected": care_gaps_detected,
        "follow_up_tasks_created": tasks_created,
        "drafts_awaiting_approval": drafts_awaiting_approval,
        "simulated_patient_communication_rate": int((emails_queued / denominator) * 100),
        "reduced_missed_follow_up_risk": "High impact" if care_gaps_detected >= 4 else "Pending workflow run",
        "doctor_productivity_impact": "Estimated 18 minutes saved per completed visit workflow",
        "completed_workflows": completed_workflows,
    }


@app.get("/audit/{visit_id}", response_model=list[AuditLogOut])
def get_audit_log(visit_id: int, db: Session = Depends(get_db)):
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return audit_service.get_audit_logs(db, visit_id)
