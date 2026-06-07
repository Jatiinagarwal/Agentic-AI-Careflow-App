from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models import Lab, Medication, Patient, PreviousVisit


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def seed_database(db: Session) -> None:
    """Seed one rich mock patient for the hackathon demo."""
    existing = db.query(Patient).first()
    if existing:
        return

    rajesh = Patient(
        name="Rajesh Mehra",
        age=58,
        gender="Male",
        conditions=[
            "Type 2 diabetes",
            "Hypertension",
            "High cholesterol",
            "Mild kidney function decline",
            "Previous missed follow-up",
        ],
        risk_factors=[
            "HbA1c previously above goal",
            "Elevated blood pressure at prior visits",
            "Medication adherence uncertainty",
            "Mildly reduced eGFR requiring monitoring",
            "Missed follow-up lab appointment",
        ],
    )
    db.add(rajesh)
    db.flush()

    db.add_all(
        [
            Medication(
                patient_id=rajesh.id,
                name="Metformin",
                dose="1000 mg",
                frequency="twice daily",
                notes="Mock medication record; kidney function should be monitored.",
            ),
            Medication(
                patient_id=rajesh.id,
                name="Lisinopril",
                dose="20 mg",
                frequency="once daily",
                notes="Mock medication record; monitor potassium and renal function.",
            ),
            Medication(
                patient_id=rajesh.id,
                name="Atorvastatin",
                dose="20 mg",
                frequency="nightly",
                notes="Mock medication record for cholesterol management.",
            ),
            Medication(
                patient_id=rajesh.id,
                name="Amlodipine",
                dose="5 mg",
                frequency="once daily",
                notes="Mock medication record for blood pressure management.",
            ),
        ]
    )

    db.add_all(
        [
            Lab(patient_id=rajesh.id, name="HbA1c", value="8.4", unit="%", collected_at=_days_ago(132), status="overdue for repeat"),
            Lab(patient_id=rajesh.id, name="Fasting glucose", value="168", unit="mg/dL", collected_at=_days_ago(28), status="above reference range"),
            Lab(patient_id=rajesh.id, name="eGFR", value="52", unit="mL/min/1.73m2", collected_at=_days_ago(68), status="mild decline"),
            Lab(patient_id=rajesh.id, name="Creatinine", value="1.32", unit="mg/dL", collected_at=_days_ago(68), status="monitor"),
            Lab(patient_id=rajesh.id, name="LDL cholesterol", value="128", unit="mg/dL", collected_at=_days_ago(155), status="above goal"),
            Lab(patient_id=rajesh.id, name="Potassium", value="4.9", unit="mmol/L", collected_at=_days_ago(68), status="upper-normal mock value"),
        ]
    )

    db.add_all(
        [
            PreviousVisit(
                patient_id=rajesh.id,
                date=_days_ago(188),
                visit_type="Chronic care follow-up",
                summary="Diabetes and hypertension follow-up. HbA1c was above goal and blood pressure remained elevated in clinic.",
                plan="Continue current medications, reinforce home BP log, repeat HbA1c in 3 months, kidney function monitoring, lifestyle counseling.",
            ),
            PreviousVisit(
                patient_id=rajesh.id,
                date=_days_ago(116),
                visit_type="Lab review",
                summary="Patient had not completed scheduled HbA1c. Reported inconsistent exercise and occasional missed evening medication doses.",
                plan="Reschedule HbA1c, review medication routine, follow up in 4 weeks, consider care team outreach if labs remain overdue.",
            ),
            PreviousVisit(
                patient_id=rajesh.id,
                date=_days_ago(53),
                visit_type="Nurse phone follow-up",
                summary="Clinic attempted follow-up for overdue labs. Patient planned to complete labs but no result was documented.",
                plan="Send reminder, flag chart for physician review at next visit.",
            ),
        ]
    )

    db.commit()
