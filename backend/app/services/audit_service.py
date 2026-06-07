from sqlalchemy.orm import Session

from app.models import AuditLog


def log_event(db: Session, visit_id: int | None, actor: str, event_type: str, details: dict) -> AuditLog:
    event = AuditLog(visit_id=visit_id, actor=actor, event_type=event_type, details=details)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_audit_logs(db: Session, visit_id: int) -> list[AuditLog]:
    return db.query(AuditLog).filter(AuditLog.visit_id == visit_id).order_by(AuditLog.created_at.asc()).all()
