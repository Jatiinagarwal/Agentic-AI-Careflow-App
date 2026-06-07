from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models import Allergy, Appointment, CareGapRecord, Condition, Lab, Medication, Patient, PreviousVisit, Task


def _days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def _days_from_now(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _patient(db: Session, **kwargs) -> Patient:
    patient = Patient(**kwargs)
    db.add(patient)
    db.flush()
    for condition in patient.conditions:
        db.add(Condition(patient_id=patient.id, name=condition, status="Active", diagnosed_at="2024-01-15", notes="Seeded mock condition."))
    return patient


def seed_database(db: Session) -> None:
    """Seed three rich mock patients for the hackathon demo."""
    if db.query(Patient).count() >= 3:
        return

    db.query(Task).delete()
    db.query(Appointment).delete()
    db.query(CareGapRecord).delete()
    db.query(PreviousVisit).delete()
    db.query(Lab).delete()
    db.query(Medication).delete()
    db.query(Allergy).delete()
    db.query(Condition).delete()
    db.query(Patient).delete()
    db.commit()

    rajesh = _patient(
        db,
        first_name="Rajesh",
        last_name="Mehra",
        name="Rajesh Mehra",
        date_of_birth="1968-03-12",
        age=58,
        gender="Male",
        phone="+91-98765-10001",
        email="rajesh.mehra@example.test",
        address="Mock address, Gurugram, Haryana",
        emergency_contact_name="Neha Mehra",
        emergency_contact_phone="+91-98765-10002",
        primary_physician="Dr. Sharma",
        preferred_language="English / Hindi",
        risk_level="High",
        status="Labs Overdue",
        conditions=["Type 2 diabetes", "Hypertension", "High cholesterol", "Mild kidney function decline", "Previous missed follow-up"],
        risk_factors=["HbA1c previously above goal", "Elevated blood pressure at prior visits", "Medication adherence uncertainty", "Mildly reduced eGFR requiring monitoring", "Missed follow-up lab appointment"],
    )
    db.add_all([
        Allergy(patient_id=rajesh.id, allergen="Penicillin", reaction="Rash", severity="Moderate", notes="Mock allergy record."),
        Medication(patient_id=rajesh.id, name="Metformin", dose="1000 mg", frequency="twice daily", notes="Mock medication record; kidney function should be monitored."),
        Medication(patient_id=rajesh.id, name="Lisinopril", dose="20 mg", frequency="once daily", notes="Mock medication record; monitor potassium and renal function."),
        Medication(patient_id=rajesh.id, name="Atorvastatin", dose="20 mg", frequency="nightly", notes="Mock medication record for cholesterol management."),
        Medication(patient_id=rajesh.id, name="Amlodipine", dose="5 mg", frequency="once daily", notes="Mock medication record for blood pressure management."),
        Lab(patient_id=rajesh.id, name="HbA1c", value="8.4", unit="%", collected_at=_days_ago(132), status="overdue for repeat"),
        Lab(patient_id=rajesh.id, name="Fasting glucose", value="168", unit="mg/dL", collected_at=_days_ago(28), status="above reference range"),
        Lab(patient_id=rajesh.id, name="eGFR", value="52", unit="mL/min/1.73m2", collected_at=_days_ago(68), status="mild decline"),
        Lab(patient_id=rajesh.id, name="Creatinine", value="1.32", unit="mg/dL", collected_at=_days_ago(68), status="monitor"),
        Lab(patient_id=rajesh.id, name="LDL cholesterol", value="128", unit="mg/dL", collected_at=_days_ago(155), status="above goal"),
        PreviousVisit(patient_id=rajesh.id, date=_days_ago(188), visit_type="Chronic care follow-up", summary="Diabetes and hypertension follow-up. HbA1c was above goal and blood pressure remained elevated in clinic.", plan="Repeat HbA1c in 3 months, monitor kidney function, reinforce BP log and adherence."),
        PreviousVisit(patient_id=rajesh.id, date=_days_ago(116), visit_type="Lab review", summary="Patient had not completed scheduled HbA1c. Reported occasional missed evening medication doses.", plan="Reschedule HbA1c and review medication routine."),
        CareGapRecord(patient_id=rajesh.id, gap="HbA1c overdue", priority="High", evidence="Last HbA1c was 132 days ago and above goal.", recommended_follow_up_action="Order repeat HbA1c and review result.", status="Overdue"),
        Task(patient_id=rajesh.id, task_type="lab_reminder", title="Call Rajesh for overdue HbA1c", description="Mock nurse outreach task for missed diabetes lab.", owner="Nurse team", status="open"),
        Appointment(patient_id=rajesh.id, appointment_date=_days_from_now(14), reason="BP and diabetes follow-up", status="Needs confirmation", notes="Mock appointment reminder."),
    ])

    anita = _patient(
        db,
        first_name="Anita",
        last_name="Sharma",
        name="Anita Sharma",
        date_of_birth="1981-09-04",
        age=45,
        gender="Female",
        phone="+91-98765-20001",
        email="anita.sharma@example.test",
        address="Mock address, Noida, Uttar Pradesh",
        emergency_contact_name="Rohit Sharma",
        emergency_contact_phone="+91-98765-20002",
        primary_physician="Dr. Sharma",
        preferred_language="English / Hindi",
        risk_level="Moderate",
        status="Follow-up Due",
        conditions=["Asthma", "Allergic rhinitis", "Recent ER visit for wheezing", "Medication refill concern"],
        risk_factors=["Recent emergency visit", "Inhaler technique follow-up needed", "Controller medication refill uncertainty"],
    )
    db.add_all([
        Allergy(patient_id=anita.id, allergen="Dust mites", reaction="Wheezing and sneezing", severity="Moderate", notes="Mock allergy trigger."),
        Medication(patient_id=anita.id, name="Budesonide/Formoterol inhaler", dose="160/4.5 mcg", frequency="twice daily", notes="Review technique."),
        Medication(patient_id=anita.id, name="Salbutamol inhaler", dose="100 mcg", frequency="as needed", notes="Mock rescue inhaler."),
        Lab(patient_id=anita.id, name="Peak flow", value="330", unit="L/min", collected_at=_days_ago(9), status="below personal best"),
        PreviousVisit(patient_id=anita.id, date=_days_ago(12), visit_type="ER discharge follow-up", summary="Recent ER visit for wheezing; symptoms improved after treatment.", plan="Review inhaler technique, refill controller medication, follow up in 2 weeks."),
        CareGapRecord(patient_id=anita.id, gap="Inhaler technique follow-up needed", priority="Medium", evidence="Recent ER visit and refill concern.", recommended_follow_up_action="Schedule nurse inhaler education.", status="Open"),
        Task(patient_id=anita.id, task_type="education", title="Inhaler technique teaching", description="Mock respiratory nurse education task.", owner="Nurse team", status="open"),
    ])

    mohan = _patient(
        db,
        first_name="Mohan",
        last_name="Iyer",
        name="Mohan Iyer",
        date_of_birth="1959-11-20",
        age=67,
        gender="Male",
        phone="+91-98765-30001",
        email="mohan.iyer@example.test",
        address="Mock address, Bengaluru, Karnataka",
        emergency_contact_name="Lakshmi Iyer",
        emergency_contact_phone="+91-98765-30002",
        primary_physician="Dr. Rao",
        preferred_language="English / Tamil",
        risk_level="High",
        status="Active",
        conditions=["Heart failure history", "Hypertension", "Chronic kidney disease", "Recent weight gain"],
        risk_factors=["Fluid status monitoring needed", "Kidney function monitoring needed", "Recent weight gain may need clinician review"],
    )
    db.add_all([
        Allergy(patient_id=mohan.id, allergen="Sulfa drugs", reaction="Hives", severity="Moderate", notes="Mock allergy record."),
        Medication(patient_id=mohan.id, name="Furosemide", dose="40 mg", frequency="once daily", notes="Mock heart failure medication record."),
        Medication(patient_id=mohan.id, name="Carvedilol", dose="12.5 mg", frequency="twice daily", notes="Mock BP/heart failure medication record."),
        Lab(patient_id=mohan.id, name="eGFR", value="44", unit="mL/min/1.73m2", collected_at=_days_ago(31), status="CKD monitoring"),
        Lab(patient_id=mohan.id, name="Potassium", value="5.1", unit="mmol/L", collected_at=_days_ago(31), status="monitor closely"),
        PreviousVisit(patient_id=mohan.id, date=_days_ago(37), visit_type="Heart failure follow-up", summary="Reported mild weight gain and intermittent ankle swelling.", plan="Review weight log, repeat renal panel, follow up within 2 weeks if symptoms worsen."),
        CareGapRecord(patient_id=mohan.id, gap="Renal panel follow-up", priority="High", evidence="CKD with recent potassium 5.1 mock value.", recommended_follow_up_action="Repeat kidney function and electrolyte labs.", status="Open"),
        Appointment(patient_id=mohan.id, appointment_date=_days_from_now(7), reason="Heart failure and kidney monitoring", status="Scheduled", notes="Mock upcoming appointment."),
    ])

    db.commit()
