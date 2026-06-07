from datetime import datetime
from sqlalchemy.orm import Session

from app.models import CommunicationDraft, GeneratedOutput, Patient, Visit


def upsert_from_generated_output(db: Session, visit: Visit, generated: GeneratedOutput) -> CommunicationDraft:
    patient = db.query(Patient).filter(Patient.id == visit.patient_id).first()
    existing = db.query(CommunicationDraft).filter(CommunicationDraft.visit_id == visit.id).first()
    subject_name = patient.name if patient else "Patient"
    if existing:
        draft = existing
    else:
        draft = CommunicationDraft(patient_id=visit.patient_id, visit_id=visit.id)
        db.add(draft)
    draft.subject = f"CareFlow MD follow-up for {subject_name}"
    draft.body = generated.patient_email_draft
    draft.instruction_draft = generated.medication_instruction_draft
    draft.follow_up_summary = generated.follow_up_summary
    draft.status = "Draft"
    draft.safety_label = "Simulated email only. No real patient email is sent. Draft - Doctor review required."
    draft.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(draft)
    return draft


def list_patient_communications(db: Session, patient_id: int) -> list[CommunicationDraft]:
    return db.query(CommunicationDraft).filter(CommunicationDraft.patient_id == patient_id).order_by(CommunicationDraft.created_at.desc()).all()


def get_communication(db: Session, communication_id: int) -> CommunicationDraft | None:
    return db.query(CommunicationDraft).filter(CommunicationDraft.id == communication_id).first()


def set_status(db: Session, communication: CommunicationDraft, status: str) -> CommunicationDraft:
    communication.status = status
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)
    return communication


def queue_for_visit(db: Session, visit_id: int) -> list[CommunicationDraft]:
    drafts = db.query(CommunicationDraft).filter(CommunicationDraft.visit_id == visit_id).all()
    for draft in drafts:
        draft.status = "Queued"
        draft.updated_at = datetime.utcnow()
    db.commit()
    return drafts
