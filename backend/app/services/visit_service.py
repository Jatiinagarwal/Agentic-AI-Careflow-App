from sqlalchemy.orm import Session

from app.models import GeneratedOutput, Visit
from app.schemas import VisitInput, VisitStartRequest


def start_visit(db: Session, payload: VisitStartRequest) -> Visit:
    visit = Visit(
        patient_id=payload.patient_id,
        chief_complaint=payload.chief_complaint,
        symptoms=payload.symptoms,
        vitals=payload.vitals,
        doctor_notes=payload.doctor_notes,
        assessment_notes=payload.assessment_notes,
        suggested_plan=payload.suggested_plan,
        status="started",
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def get_visit(db: Session, visit_id: int) -> Visit | None:
    return db.query(Visit).filter(Visit.id == visit_id).first()


def create_visit_from_input(db: Session, patient_id: int, visit_input: VisitInput) -> Visit:
    payload = VisitStartRequest(patient_id=patient_id, **visit_input.model_dump())
    return start_visit(db, payload)


def update_visit_input(db: Session, visit: Visit, visit_input: VisitInput) -> Visit:
    for key, value in visit_input.model_dump().items():
        setattr(visit, key, value)
    db.commit()
    db.refresh(visit)
    return visit


def visit_as_dict(visit: Visit) -> dict[str, str]:
    return {
        "chief_complaint": visit.chief_complaint,
        "symptoms": visit.symptoms,
        "vitals": visit.vitals,
        "doctor_notes": visit.doctor_notes,
        "assessment_notes": visit.assessment_notes,
        "suggested_plan": visit.suggested_plan,
    }


def save_generated_output(db: Session, visit_id: int, output: dict) -> GeneratedOutput:
    existing = db.query(GeneratedOutput).filter(GeneratedOutput.visit_id == visit_id).first()
    if existing:
        generated = existing
    else:
        generated = GeneratedOutput(visit_id=visit_id)
        db.add(generated)

    generated.patient_context_summary = output["patient_context_summary"]
    generated.relevant_history = output["relevant_history"]
    generated.risk_factors = output["risk_factors"]
    generated.recent_labs = output["recent_labs"]
    generated.medication_list = output["medication_list"]
    generated.soap_note = output["soap_note"]
    generated.care_gaps = output["care_gaps"]
    generated.medication_safety = output["medication_safety"]
    generated.patient_email_draft = output["patient_email_draft"]
    generated.medication_instruction_draft = output["medication_instruction_draft"]
    generated.follow_up_summary = output["follow_up_summary"]
    generated.proposed_tasks = output["proposed_tasks"]
    generated.agent_steps = output["agent_steps"]
    generated.doctor_approval = output["doctor_approval"]
    generated.approved = False
    generated.executed = False

    visit = get_visit(db, visit_id)
    if visit:
        visit.status = "draft_generated"

    db.commit()
    db.refresh(generated)
    return generated


def generated_output_as_response(generated: GeneratedOutput) -> dict:
    return {
        "visit_id": generated.visit_id,
        "patient_context_summary": generated.patient_context_summary,
        "relevant_history": generated.relevant_history,
        "risk_factors": generated.risk_factors,
        "recent_labs": generated.recent_labs,
        "medication_list": generated.medication_list,
        "soap_note": generated.soap_note,
        "care_gaps": generated.care_gaps,
        "medication_safety": generated.medication_safety,
        "patient_email_draft": generated.patient_email_draft,
        "medication_instruction_draft": generated.medication_instruction_draft,
        "follow_up_summary": generated.follow_up_summary,
        "proposed_tasks": generated.proposed_tasks,
        "agent_steps": generated.agent_steps,
        "doctor_approval": generated.doctor_approval,
        "approved": generated.approved,
        "executed": generated.executed,
    }
