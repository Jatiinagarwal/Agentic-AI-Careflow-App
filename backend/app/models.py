from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(80), default="")
    last_name: Mapped[str] = mapped_column(String(80), default="")
    date_of_birth: Mapped[str] = mapped_column(String(20), default="")
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(40), nullable=False)
    phone: Mapped[str] = mapped_column(String(40), default="")
    email: Mapped[str] = mapped_column(String(120), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    emergency_contact_name: Mapped[str] = mapped_column(String(120), default="")
    emergency_contact_phone: Mapped[str] = mapped_column(String(40), default="")
    primary_physician: Mapped[str] = mapped_column(String(120), default="Dr. Sharma")
    preferred_language: Mapped[str] = mapped_column(String(60), default="English")
    consent_for_mock_email: Mapped[bool] = mapped_column(Boolean, default=True)
    risk_level: Mapped[str] = mapped_column(String(40), default="Moderate")
    status: Mapped[str] = mapped_column(String(60), default="Active")
    conditions: Mapped[list[str]] = mapped_column(JSON, default=list)
    risk_factors: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    medications: Mapped[list["Medication"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    labs: Mapped[list["Lab"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    previous_visits: Mapped[list["PreviousVisit"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    visits: Mapped[list["Visit"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    condition_records: Mapped[list["Condition"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    allergies: Mapped[list["Allergy"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    care_gap_records: Mapped[list["CareGapRecord"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    communication_drafts: Mapped[list["CommunicationDraft"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship(back_populates="patient", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient", cascade="all, delete-orphan")


class Condition(Base):
    __tablename__ = "condition_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(60), default="Active")
    diagnosed_at: Mapped[str] = mapped_column(String(20), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="condition_records")


class Allergy(Base):
    __tablename__ = "allergies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    allergen: Mapped[str] = mapped_column(String(160), nullable=False)
    reaction: Mapped[str] = mapped_column(String(200), default="")
    severity: Mapped[str] = mapped_column(String(60), default="Unknown")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="allergies")


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    dose: Mapped[str] = mapped_column(String(80), nullable=False)
    frequency: Mapped[str] = mapped_column(String(80), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")

    patient: Mapped[Patient] = relationship(back_populates="medications")


class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(String(80), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), default="")
    collected_at: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(80), default="available")

    patient: Mapped[Patient] = relationship(back_populates="labs")


class PreviousVisit(Base):
    __tablename__ = "previous_visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    date: Mapped[str] = mapped_column(String(20), nullable=False)
    visit_type: Mapped[str] = mapped_column(String(100), default="Follow-up")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[str] = mapped_column(Text, nullable=False)

    patient: Mapped[Patient] = relationship(back_populates="previous_visits")


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    chief_complaint: Mapped[str] = mapped_column(Text, default="")
    symptoms: Mapped[str] = mapped_column(Text, default="")
    vitals: Mapped[str] = mapped_column(Text, default="")
    doctor_notes: Mapped[str] = mapped_column(Text, default="")
    assessment_notes: Mapped[str] = mapped_column(Text, default="")
    suggested_plan: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="started")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="visits")
    generated_output: Mapped["GeneratedOutput"] = relationship(back_populates="visit", cascade="all, delete-orphan", uselist=False)
    tasks: Mapped[list["Task"]] = relationship(back_populates="visit")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="visit")


class GeneratedOutput(Base):
    __tablename__ = "generated_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visits.id"), nullable=False, unique=True)
    patient_context_summary: Mapped[str] = mapped_column(Text, default="")
    relevant_history: Mapped[list[dict]] = mapped_column(JSON, default=list)
    risk_factors: Mapped[list[str]] = mapped_column(JSON, default=list)
    recent_labs: Mapped[list[dict]] = mapped_column(JSON, default=list)
    medication_list: Mapped[list[dict]] = mapped_column(JSON, default=list)
    soap_note: Mapped[dict] = mapped_column(JSON, default=dict)
    care_gaps: Mapped[list[dict]] = mapped_column(JSON, default=list)
    medication_safety: Mapped[list[dict]] = mapped_column(JSON, default=list)
    patient_email_draft: Mapped[str] = mapped_column(Text, default="")
    medication_instruction_draft: Mapped[str] = mapped_column(Text, default="")
    follow_up_summary: Mapped[str] = mapped_column(Text, default="")
    proposed_tasks: Mapped[list[dict]] = mapped_column(JSON, default=list)
    agent_steps: Mapped[list[dict]] = mapped_column(JSON, default=list)
    doctor_approval: Mapped[dict] = mapped_column(JSON, default=dict)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    executed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    visit: Mapped[Visit] = relationship(back_populates="generated_output")


class CareGapRecord(Base):
    __tablename__ = "care_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id"), nullable=True)
    gap: Mapped[str] = mapped_column(String(200), nullable=False)
    priority: Mapped[str] = mapped_column(String(60), default="Medium")
    evidence: Mapped[str] = mapped_column(Text, default="")
    recommended_follow_up_action: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(60), default="Open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="care_gap_records")


class CommunicationDraft(Base):
    __tablename__ = "communication_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id"), nullable=True)
    subject: Mapped[str] = mapped_column(String(200), default="CareFlow MD follow-up")
    body: Mapped[str] = mapped_column(Text, default="")
    recipient_email: Mapped[str] = mapped_column(String(160), default="")
    instruction_draft: Mapped[str] = mapped_column(Text, default="")
    follow_up_summary: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(60), default="Draft")
    approval_status: Mapped[str] = mapped_column(String(60), default="Pending")
    approved_by: Mapped[str] = mapped_column(String(120), default="")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    provider: Mapped[str] = mapped_column(String(80), default="")
    provider_message_id: Mapped[str] = mapped_column(String(200), default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    safety_label: Mapped[str] = mapped_column(String(220), default="Doctor-approved patient communication. Email sending may contain sensitive information. Use only with consent and appropriate safeguards.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="communication_drafts")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id"), nullable=True)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(120), default="Clinic team")
    status: Mapped[str] = mapped_column(String(40), default="created")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient | None] = relationship(back_populates="tasks")
    visit: Mapped[Visit | None] = relationship(back_populates="tasks")


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    appointment_date: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), default="Follow-up")
    status: Mapped[str] = mapped_column(String(60), default="Scheduled")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient] = relationship(back_populates="appointments")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int | None] = mapped_column(ForeignKey("patients.id"), nullable=True)
    visit_id: Mapped[int | None] = mapped_column(ForeignKey("visits.id"), nullable=True)
    actor: Mapped[str] = mapped_column(String(120), default="system")
    event_type: Mapped[str] = mapped_column(String(120), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    patient: Mapped[Patient | None] = relationship(back_populates="audit_logs")
    visit: Mapped[Visit | None] = relationship(back_populates="audit_logs")
