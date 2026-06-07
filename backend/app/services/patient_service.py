from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import (
    Allergy,
    Appointment,
    AuditLog,
    CareGapRecord,
    CommunicationDraft,
    Condition,
    Lab,
    Medication,
    Patient,
    PreviousVisit,
    Task,
)
from app.schemas import PatientCreate, PatientUpdate


def _sync_patient_name(patient: Patient) -> None:
    if patient.first_name or patient.last_name:
        patient.name = f"{patient.first_name} {patient.last_name}".strip()
    if not patient.name:
        patient.name = "Mock Patient"


def list_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.name).all()


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def create_patient(db: Session, payload: PatientCreate) -> Patient:
    data = payload.model_dump()
    if not data.get("name"):
        data["name"] = f"{payload.first_name} {payload.last_name}".strip()
    patient = Patient(**data)
    db.add(patient)
    db.flush()
    for condition in patient.conditions:
        db.add(Condition(patient_id=patient.id, name=condition, status="Active", notes="Added from patient creation form."))
    db.commit()
    db.refresh(patient)
    return patient


def update_patient(db: Session, patient: Patient, payload: PatientUpdate) -> Patient:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    _sync_patient_name(patient)
    db.commit()
    db.refresh(patient)
    return patient


def search_patients(db: Session, query: str) -> list[Patient]:
    normalized = f"%{query.lower()}%"
    patients = db.query(Patient).all()
    if not query:
        return patients
    matched: list[Patient] = []
    for patient in patients:
        haystack = " ".join(
            [
                patient.name,
                patient.phone,
                patient.email,
                patient.risk_level,
                patient.status,
                " ".join(patient.conditions or []),
                " ".join(patient.risk_factors or []),
            ]
        ).lower()
        if query.lower() in haystack:
            matched.append(patient)
    return matched


def get_patient_history(db: Session, patient_id: int) -> dict:
    patient = get_patient(db, patient_id)
    if not patient:
        raise ValueError("Patient not found")

    medications = db.query(Medication).filter(Medication.patient_id == patient_id).order_by(Medication.name).all()
    labs = db.query(Lab).filter(Lab.patient_id == patient_id).order_by(Lab.collected_at.desc()).all()
    previous_visits = db.query(PreviousVisit).filter(PreviousVisit.patient_id == patient_id).order_by(PreviousVisit.date.desc()).all()
    return {"patient": patient, "medications": medications, "labs": labs, "previous_visits": previous_visits}


def get_patient_record(db: Session, patient_id: int) -> dict:
    patient = get_patient(db, patient_id)
    if not patient:
        raise ValueError("Patient not found")
    return {
        "patient": patient,
        "conditions": db.query(Condition).filter(Condition.patient_id == patient_id).order_by(Condition.created_at.desc()).all(),
        "allergies": db.query(Allergy).filter(Allergy.patient_id == patient_id).order_by(Allergy.created_at.desc()).all(),
        "medications": db.query(Medication).filter(Medication.patient_id == patient_id).order_by(Medication.name).all(),
        "labs": db.query(Lab).filter(Lab.patient_id == patient_id).order_by(Lab.collected_at.desc()).all(),
        "previous_visits": db.query(PreviousVisit).filter(PreviousVisit.patient_id == patient_id).order_by(PreviousVisit.date.desc()).all(),
        "care_gaps": db.query(CareGapRecord).filter(CareGapRecord.patient_id == patient_id).order_by(CareGapRecord.created_at.desc()).all(),
        "communications": db.query(CommunicationDraft).filter(CommunicationDraft.patient_id == patient_id).order_by(CommunicationDraft.created_at.desc()).all(),
        "tasks": db.query(Task).filter(Task.patient_id == patient_id).order_by(Task.created_at.desc()).all(),
        "appointments": db.query(Appointment).filter(Appointment.patient_id == patient_id).order_by(Appointment.created_at.desc()).all(),
        "audit_logs": [
            {
                "id": log.id,
                "patient_id": log.patient_id,
                "visit_id": log.visit_id,
                "actor": log.actor,
                "event_type": log.event_type,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in db.query(AuditLog).filter(AuditLog.patient_id == patient_id).order_by(AuditLog.created_at.desc()).all()
        ],
    }


def get_patient_timeline(db: Session, patient_id: int) -> list[dict]:
    record = get_patient_record(db, patient_id)
    events: list[dict] = []
    for condition in record["conditions"]:
        events.append({"id": f"condition-{condition.id}", "date": condition.diagnosed_at or condition.created_at.date().isoformat(), "type": "Condition", "title": condition.name, "description": condition.notes or condition.status, "status": condition.status})
    for allergy in record["allergies"]:
        events.append({"id": f"allergy-{allergy.id}", "date": allergy.created_at.date().isoformat(), "type": "Allergy", "title": allergy.allergen, "description": f"{allergy.reaction} {allergy.notes}".strip(), "status": allergy.severity})
    for lab in record["labs"]:
        events.append({"id": f"lab-{lab.id}", "date": lab.collected_at, "type": "Lab", "title": lab.name, "description": f"{lab.value} {lab.unit}".strip(), "status": lab.status})
    for visit in record["previous_visits"]:
        events.append({"id": f"visit-{visit.id}", "date": visit.date, "type": "Visit", "title": visit.visit_type, "description": visit.summary, "status": "completed"})
    for gap in record["care_gaps"]:
        events.append({"id": f"gap-{gap.id}", "date": gap.created_at.date().isoformat(), "type": "Care Gap", "title": gap.gap, "description": gap.recommended_follow_up_action, "status": gap.status})
    for communication in record["communications"]:
        events.append({"id": f"communication-{communication.id}", "date": communication.updated_at.date().isoformat(), "type": "Communication", "title": communication.subject, "description": communication.safety_label, "status": communication.status})
    for task in record["tasks"]:
        events.append({"id": f"task-{task.id}", "date": task.created_at.date().isoformat(), "type": "Task", "title": task.title, "description": task.description, "status": task.status})
    return sorted(events, key=lambda event: event["date"], reverse=True)


def patient_history_as_dict(db: Session, patient_id: int) -> dict:
    record = get_patient_record(db, patient_id)
    patient = record["patient"]
    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "risk_level": patient.risk_level,
            "status": patient.status,
            "conditions": patient.conditions,
            "risk_factors": patient.risk_factors,
            "preferred_language": patient.preferred_language,
        },
        "conditions": [{"id": item.id, "name": item.name, "status": item.status, "notes": item.notes} for item in record["conditions"]],
        "allergies": [{"id": item.id, "allergen": item.allergen, "reaction": item.reaction, "severity": item.severity, "notes": item.notes} for item in record["allergies"]],
        "medications": [{"id": med.id, "name": med.name, "dose": med.dose, "frequency": med.frequency, "notes": med.notes} for med in record["medications"]],
        "labs": [{"id": lab.id, "name": lab.name, "value": lab.value, "unit": lab.unit, "collected_at": lab.collected_at, "status": lab.status} for lab in record["labs"]],
        "previous_visits": [{"id": visit.id, "date": visit.date, "visit_type": visit.visit_type, "summary": visit.summary, "plan": visit.plan} for visit in record["previous_visits"]],
        "care_gaps": [{"id": gap.id, "gap": gap.gap, "priority": gap.priority, "evidence": gap.evidence, "recommended_follow_up_action": gap.recommended_follow_up_action, "status": gap.status} for gap in record["care_gaps"]],
        "tasks": [{"id": task.id, "task_type": task.task_type, "title": task.title, "description": task.description, "owner": task.owner, "status": task.status} for task in record["tasks"]],
    }
