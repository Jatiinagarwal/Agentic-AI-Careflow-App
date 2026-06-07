from sqlalchemy.orm import Session

from app.models import Allergy, Appointment, CareGapRecord, Condition, Lab, Medication, Patient, PreviousVisit, Task
from app.schemas import AllergyCreate, AppointmentCreate, CareGapCreate, ConditionCreate, LabCreate, MedicationCreate, PreviousVisitCreate, TaskCreate


def _require_patient(db: Session, patient_id: int) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise ValueError("Patient not found")
    return patient


def add_condition(db: Session, patient_id: int, payload: ConditionCreate) -> Condition:
    patient = _require_patient(db, patient_id)
    record = Condition(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    if payload.name not in (patient.conditions or []):
        patient.conditions = [*(patient.conditions or []), payload.name]
    db.commit()
    db.refresh(record)
    return record


def add_allergy(db: Session, patient_id: int, payload: AllergyCreate) -> Allergy:
    _require_patient(db, patient_id)
    record = Allergy(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_medication(db: Session, patient_id: int, payload: MedicationCreate) -> Medication:
    _require_patient(db, patient_id)
    record = Medication(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_lab(db: Session, patient_id: int, payload: LabCreate) -> Lab:
    _require_patient(db, patient_id)
    record = Lab(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_previous_visit(db: Session, patient_id: int, payload: PreviousVisitCreate) -> PreviousVisit:
    _require_patient(db, patient_id)
    record = PreviousVisit(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_care_gap(db: Session, patient_id: int, payload: CareGapCreate) -> CareGapRecord:
    _require_patient(db, patient_id)
    record = CareGapRecord(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_task(db: Session, patient_id: int, payload: TaskCreate) -> Task:
    _require_patient(db, patient_id)
    record = Task(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_appointment(db: Session, patient_id: int, payload: AppointmentCreate) -> Appointment:
    _require_patient(db, patient_id)
    record = Appointment(patient_id=patient_id, **payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
