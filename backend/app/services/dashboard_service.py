from sqlalchemy.orm import Session

from app.models import CareGapRecord, CommunicationDraft, GeneratedOutput, Patient, Task, Visit


def metrics(db: Session) -> dict:
    generated_outputs = db.query(GeneratedOutput).all()
    completed_workflows = len([output for output in generated_outputs if output.executed])
    drafts_awaiting_approval = len([output for output in generated_outputs if not output.approved])
    generated_care_gaps = sum(len(output.care_gaps or []) for output in generated_outputs)
    persisted_care_gaps = db.query(CareGapRecord).count()
    tasks_created = db.query(Task).count()
    emails_queued = db.query(CommunicationDraft).filter(CommunicationDraft.status == "Queued").count()
    mock_emails_sent = db.query(CommunicationDraft).filter(CommunicationDraft.status == "Mock Sent").count()
    real_emails_sent = db.query(CommunicationDraft).filter(CommunicationDraft.status == "Sent").count()
    failed_email_attempts = db.query(CommunicationDraft).filter(CommunicationDraft.status == "Failed").count()
    email_drafts_pending_approval = db.query(CommunicationDraft).filter(CommunicationDraft.approval_status == "Pending").count()
    approved_emails_not_sent = db.query(CommunicationDraft).filter(CommunicationDraft.approval_status == "Approved", CommunicationDraft.status.notin_(["Sent", "Mock Sent", "Cancelled"])).count()
    denominator = completed_workflows if completed_workflows else 1
    active_patients = db.query(Patient).filter(Patient.status.in_(["Active", "Follow-up Due", "Labs Overdue", "Drafts Pending Approval"])).count()
    patients_with_overdue = {gap.patient_id for gap in db.query(CareGapRecord).filter(CareGapRecord.status.in_(["Open", "Overdue"])).all()}
    open_tasks = db.query(Task).filter(Task.status.in_(["created", "open", "Open", "Queued"])).count()
    actions_completed = completed_workflows * 5
    return {
        "documentation_time_saved_minutes": len(generated_outputs) * 18,
        "care_gaps_detected": generated_care_gaps + persisted_care_gaps,
        "follow_up_tasks_created": tasks_created,
        "drafts_awaiting_approval": drafts_awaiting_approval,
        "simulated_patient_communication_rate": int(((emails_queued + mock_emails_sent + real_emails_sent) / denominator) * 100),
        "reduced_missed_follow_up_risk": "High impact" if generated_care_gaps + persisted_care_gaps >= 4 else "Pending workflow run",
        "doctor_productivity_impact": "Estimated 18 minutes saved per completed visit workflow",
        "completed_workflows": completed_workflows,
        "total_active_patients": active_patients,
        "patients_with_overdue_care_gaps": len(patients_with_overdue),
        "emails_queued": emails_queued,
        "mock_emails_sent": mock_emails_sent,
        "follow_up_tasks_open": open_tasks,
        "actions_completed_after_approval": actions_completed,
        "email_drafts_pending_approval": email_drafts_pending_approval,
        "approved_emails_not_sent": approved_emails_not_sent,
        "emails_sent_today": real_emails_sent,
        "failed_email_attempts": failed_email_attempts,
    }


def patient_summary(db: Session, patient_id: int) -> dict:
    latest_visit = db.query(Visit).filter(Visit.patient_id == patient_id).order_by(Visit.created_at.desc()).first()
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    return {
        "patient_id": patient_id,
        "active_conditions": len(patient.conditions or []) if patient else 0,
        "open_care_gaps": db.query(CareGapRecord).filter(CareGapRecord.patient_id == patient_id, CareGapRecord.status.in_(["Open", "Overdue"])).count(),
        "open_tasks": db.query(Task).filter(Task.patient_id == patient_id, Task.status.in_(["created", "open", "Open", "Queued"])).count(),
        "queued_emails": db.query(CommunicationDraft).filter(CommunicationDraft.patient_id == patient_id, CommunicationDraft.status == "Queued").count(),
        "mock_sent_emails": db.query(CommunicationDraft).filter(CommunicationDraft.patient_id == patient_id, CommunicationDraft.status == "Mock Sent").count(),
        "latest_visit_status": latest_visit.status if latest_visit else "No current visit",
        "risk_level": patient.risk_level if patient else "Unknown",
    }
