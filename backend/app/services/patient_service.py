from sqlalchemy.orm import Session

from app.models import Lab, Medication, Patient, PreviousVisit


def list_patients(db: Session) -> list[Patient]:
    return db.query(Patient).order_by(Patient.name).all()


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()


def get_patient_history(db: Session, patient_id: int) -> dict:
    patient = get_patient(db, patient_id)
    if not patient:
        raise ValueError("Patient not found")

    medications = db.query(Medication).filter(Medication.patient_id == patient_id).order_by(Medication.name).all()
    labs = db.query(Lab).filter(Lab.patient_id == patient_id).order_by(Lab.collected_at.desc()).all()
    previous_visits = (
        db.query(PreviousVisit)
        .filter(PreviousVisit.patient_id == patient_id)
        .order_by(PreviousVisit.date.desc())
        .all()
    )
    return {
        "patient": patient,
        "medications": medications,
        "labs": labs,
        "previous_visits": previous_visits,
    }


def patient_history_as_dict(db: Session, patient_id: int) -> dict:
    history = get_patient_history(db, patient_id)
    patient = history["patient"]
    return {
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "conditions": patient.conditions,
            "risk_factors": patient.risk_factors,
        },
        "medications": [
            {
                "id": med.id,
                "name": med.name,
                "dose": med.dose,
                "frequency": med.frequency,
                "notes": med.notes,
            }
            for med in history["medications"]
        ],
        "labs": [
            {
                "id": lab.id,
                "name": lab.name,
                "value": lab.value,
                "unit": lab.unit,
                "collected_at": lab.collected_at,
                "status": lab.status,
            }
            for lab in history["labs"]
        ],
        "previous_visits": [
            {
                "id": visit.id,
                "date": visit.date,
                "visit_type": visit.visit_type,
                "summary": visit.summary,
                "plan": visit.plan,
            }
            for visit in history["previous_visits"]
        ],
    }
