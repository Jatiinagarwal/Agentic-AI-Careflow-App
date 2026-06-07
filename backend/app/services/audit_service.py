from sqlalchemy.orm import Session

from app.models import AuditLog, Visit


def log_event(db: Session, visit_id: int | None, actor: str, event_type: str, details: dict, patient_id: int | None = None) -> AuditLog:
    if patient_id is None and visit_id is not None:
        visit = db.query(Visit).filter(Visit.id == visit_id).first()
        if visit:
            patient_id = visit.patient_id
    event = AuditLog(visit_id=visit_id, patient_id=patient_id, actor=actor, event_type=event_type, details=details)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_audit_logs(db: Session, visit_id: int) -> list[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.visit_id == visit_id).order_by(AuditLog.created_at.asc()).all()


def get_patient_audit_logs(db: Session, patient_id: int) -> list[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.patient_id == patient_id).order_by(AuditLog.created_at.desc()).all()
