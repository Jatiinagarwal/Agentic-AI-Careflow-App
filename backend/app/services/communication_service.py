from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from app.models import CommunicationDraft, GeneratedOutput, Patient, Visit
from app.schemas import EmailDraftUpdate, EmailApprovalRequest, TestEmailRequest
from app.services import audit_service, email_service

TERMINAL_SENT_STATUSES = {"Sent", "Mock Sent"}


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
    draft.recipient_email = patient.email if patient else ""
    draft.instruction_draft = generated.medication_instruction_draft
    draft.follow_up_summary = generated.follow_up_summary
    draft.status = "Draft"
    draft.approval_status = "Pending"
    draft.approved_by = ""
    draft.approved_at = None
    draft.sent_at = None
    draft.provider = ""
    draft.provider_message_id = ""
    draft.error_message = ""
    draft.safety_label = "Draft - Doctor review required. Doctor-approved patient communication only."
    draft.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(draft)
    audit_service.log_event(db, visit.id, "Patient Communication Agent", "EMAIL_DRAFT_CREATED", {"communication_id": draft.id}, patient_id=visit.patient_id)
    return draft


def list_patient_communications(db: Session, patient_id: int) -> list[CommunicationDraft]:
    return db.query(CommunicationDraft).filter(CommunicationDraft.patient_id == patient_id).order_by(CommunicationDraft.created_at.desc()).all()


def get_communication(db: Session, communication_id: int) -> CommunicationDraft | None:
    return db.query(CommunicationDraft).filter(CommunicationDraft.id == communication_id).first()


def update_email_draft(db: Session, communication: CommunicationDraft, payload: EmailDraftUpdate, actor: str = "doctor") -> CommunicationDraft:
    if communication.status in TERMINAL_SENT_STATUSES:
        raise ValueError("Sent emails cannot be edited")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(communication, field, value or "")
    if communication.approval_status == "Approved":
        communication.approval_status = "Pending"
        communication.status = "Draft"
        communication.approved_by = ""
        communication.approved_at = None
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)
    audit_service.log_event(db, communication.visit_id, actor, "EMAIL_DRAFT_UPDATED", {"communication_id": communication.id}, patient_id=communication.patient_id)
    return communication


def approve_email_draft(db: Session, communication: CommunicationDraft, payload: EmailApprovalRequest) -> CommunicationDraft:
    if not communication.subject.strip() or not communication.body.strip():
        raise ValueError("Email subject and body are required before approval")
    if communication.status in TERMINAL_SENT_STATUSES:
        raise ValueError("Already sent emails cannot be approved again")
    communication.approval_status = "Approved" if payload.approved else "Rejected"
    communication.status = "Approved" if payload.approved else "Draft"
    communication.approved_by = payload.doctor_name
    communication.approved_at = datetime.utcnow()
    communication.error_message = ""
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)
    audit_service.log_event(db, communication.visit_id, payload.doctor_name, "EMAIL_APPROVED" if payload.approved else "EMAIL_REJECTED", {"communication_id": communication.id, "approved": payload.approved}, patient_id=communication.patient_id)
    return communication


def queue_for_visit(db: Session, visit_id: int) -> list[CommunicationDraft]:
    drafts = db.query(CommunicationDraft).filter(CommunicationDraft.visit_id == visit_id).all()
    for draft in drafts:
        if draft.approval_status == "Approved" and draft.status not in TERMINAL_SENT_STATUSES:
            draft.status = "Queued"
            draft.updated_at = datetime.utcnow()
            audit_service.log_event(db, draft.visit_id, "Task Orchestration Agent", "EMAIL_QUEUED", {"communication_id": draft.id}, patient_id=draft.patient_id)
    db.commit()
    return drafts


def set_status(db: Session, communication: CommunicationDraft, status: str) -> CommunicationDraft:
    communication.status = status
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)
    return communication


def _validate_send_ready(db: Session, communication: CommunicationDraft) -> Patient:
    patient = db.query(Patient).filter(Patient.id == communication.patient_id).first()
    if not patient:
        raise ValueError("Patient not found")
    if communication.status in TERMINAL_SENT_STATUSES:
        raise ValueError("This email has already been sent")
    if communication.approval_status != "Approved":
        raise ValueError("Doctor approval is required before sending email")
    if not (communication.recipient_email or patient.email):
        raise ValueError("Patient email address is required before sending")
    if not patient.consent_for_mock_email:
        raise ValueError("Patient email consent is not enabled")
    if not communication.subject.strip():
        raise ValueError("Email subject is required")
    if not communication.body.strip():
        raise ValueError("Email body is required")
    return patient


def send_email_draft(db: Session, communication: CommunicationDraft, actor: str = "doctor") -> CommunicationDraft:
    patient = _validate_send_ready(db, communication)
    recipient = communication.recipient_email or patient.email
    communication.recipient_email = recipient
    communication.status = "Queued"
    communication.error_message = ""
    communication.updated_at = datetime.utcnow()
    db.commit()
    audit_service.log_event(db, communication.visit_id, actor, "EMAIL_SEND_ATTEMPTED", {"communication_id": communication.id, "recipient_email": recipient}, patient_id=communication.patient_id)

    result = email_service.send_patient_email(recipient, communication.subject, communication.body)
    communication.status = result.status
    communication.provider = result.provider
    communication.provider_message_id = result.provider_message_id
    communication.error_message = result.error_message
    communication.sent_at = result.sent_at
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)

    event_type = "EMAIL_SENT" if result.status == "Sent" else "EMAIL_MOCK_SENT" if result.status == "Mock Sent" else "EMAIL_FAILED"
    audit_service.log_event(
        db,
        communication.visit_id,
        actor,
        event_type,
        {"communication_id": communication.id, "provider": result.provider, "provider_message_id": result.provider_message_id, "error_message": result.error_message},
        patient_id=communication.patient_id,
    )
    return communication


def cancel_email_draft(db: Session, communication: CommunicationDraft, actor: str = "doctor") -> CommunicationDraft:
    if communication.status in TERMINAL_SENT_STATUSES:
        raise ValueError("Sent emails cannot be cancelled")
    communication.status = "Cancelled"
    communication.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(communication)
    audit_service.log_event(db, communication.visit_id, actor, "EMAIL_CANCELLED", {"communication_id": communication.id}, patient_id=communication.patient_id)
    return communication


def send_test_email(db: Session, payload: TestEmailRequest, actor: str = "doctor") -> dict:
    result = email_service.send_test_email(payload.recipient_email, payload.subject, payload.body)
    audit_service.log_event(db, None, actor, "EMAIL_TEST_SENT" if result.status == "Sent" else "EMAIL_TEST_FAILED", {"recipient_email": payload.recipient_email, "status": result.status, "provider": result.provider, "error_message": result.error_message})
    return {
        "status": result.status,
        "provider": result.provider,
        "provider_message_id": result.provider_message_id,
        "error_message": result.error_message,
        "sent_at": result.sent_at,
        "message": "Test email sent." if result.status == "Sent" else result.error_message,
    }
