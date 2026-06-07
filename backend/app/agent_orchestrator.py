from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.agents.care_gap_agent import CareGapAgent
from app.agents.clinical_note_agent import ClinicalNoteAgent
from app.agents.compliance_audit_agent import ComplianceAuditAgent
from app.agents.medication_safety_agent import MedicationSafetyAgent
from app.agents.patient_communication_agent import PatientCommunicationAgent
from app.agents.patient_context_agent import PatientContextAgent
from app.agents.task_orchestration_agent import TaskOrchestrationAgent
from app.models import CareGapRecord
from app.openai_service import OpenAIService
from app.schemas import AgentRunRequest
from app.services import audit_service, communication_service, patient_service, visit_service


def _step(name: str, status: str, detail: str) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail, "timestamp": datetime.utcnow().isoformat() + "Z"}


class AgentOrchestrator:
    """Coordinates deterministic rules, LLM drafting, persistence, and audit logging."""

    def __init__(self) -> None:
        self.openai_service = OpenAIService()
        self.patient_context_agent = PatientContextAgent()
        self.clinical_note_agent = ClinicalNoteAgent()
        self.care_gap_agent = CareGapAgent()
        self.medication_safety_agent = MedicationSafetyAgent()
        self.patient_communication_agent = PatientCommunicationAgent()
        self.task_orchestration_agent = TaskOrchestrationAgent()
        self.compliance_audit_agent = ComplianceAuditAgent()

    def run_workflow(self, db: Session, request: AgentRunRequest) -> dict[str, Any]:
        patient_history = patient_service.patient_history_as_dict(db, request.patient_id)
        patient = patient_history["patient"]

        if request.visit_id:
            visit = visit_service.get_visit(db, request.visit_id)
            if not visit:
                raise ValueError("Visit not found")
            visit = visit_service.update_visit_input(db, visit, request.current_visit)
        else:
            visit = visit_service.create_visit_from_input(db, request.patient_id, request.current_visit)

        current_visit = visit_service.visit_as_dict(visit)
        agent_steps: list[dict[str, Any]] = []

        context = self.patient_context_agent.run(patient_history, self.openai_service)
        agent_steps.append(_step(self.patient_context_agent.name, "completed", "Retrieved full mock patient record and summarized longitudinal context."))
        audit_service.log_event(db, visit.id, "Patient Context Agent", "agent_completed", {"summary_length": len(context["patient_context_summary"])})

        soap_note = self.clinical_note_agent.run(context["patient_context_summary"], current_visit, self.openai_service)
        agent_steps.append(_step(self.clinical_note_agent.name, "completed", "Generated draft SOAP note for doctor review."))
        audit_service.log_event(db, visit.id, "Clinical Note Agent", "agent_completed", {"doctor_review_required": True})

        care_gaps = self.care_gap_agent.run(patient, patient_history["labs"], current_visit)
        agent_steps.append(_step(self.care_gap_agent.name, "completed", f"Identified {len(care_gaps)} care gaps using deterministic mock rules."))
        audit_service.log_event(db, visit.id, "Care Gap Agent", "agent_completed", {"care_gaps_detected": len(care_gaps)})
        for gap in care_gaps:
            exists = db.query(CareGapRecord).filter(CareGapRecord.visit_id == visit.id, CareGapRecord.gap == gap.get("gap", "")).first()
            if not exists:
                db.add(
                    CareGapRecord(
                        patient_id=visit.patient_id,
                        visit_id=visit.id,
                        gap=gap.get("gap", "Care gap"),
                        priority=gap.get("priority", "Medium"),
                        evidence=gap.get("evidence", ""),
                        recommended_follow_up_action=gap.get("recommended_follow_up_action", ""),
                        status="Open",
                    )
                )
        db.commit()

        medication_safety = self.medication_safety_agent.run(patient_history["medications"], patient["conditions"], patient_history["labs"])
        agent_steps.append(_step(self.medication_safety_agent.name, "completed", f"Flagged {len(medication_safety)} mock medication safety considerations."))
        audit_service.log_event(db, visit.id, "Medication Safety Agent", "agent_completed", {"flags_detected": len(medication_safety)})

        communication = self.patient_communication_agent.run(
            patient_name=patient["name"],
            doctor_plan=current_visit["suggested_plan"],
            care_gaps=care_gaps,
            medication_safety=medication_safety,
            openai_service=self.openai_service,
        )
        agent_steps.append(_step(self.patient_communication_agent.name, "completed", "Generated draft patient-friendly communication for doctor review."))
        audit_service.log_event(db, visit.id, "Patient Communication Agent", "agent_completed", {"draft_created": True})

        proposed_tasks = self.task_orchestration_agent.propose(care_gaps, medication_safety)
        agent_steps.append(_step(self.task_orchestration_agent.name, "blocked", "Proposed actions are waiting for doctor approval before simulation."))

        compliance = self.compliance_audit_agent.pre_approval_check()
        agent_steps.append(_step(self.compliance_audit_agent.name, "completed", compliance["message"]))
        audit_service.log_event(db, visit.id, "Compliance & Audit Agent", "pre_approval_check", compliance)

        doctor_approval = {"soap_note": False, "patient_email": False, "follow_up_tasks": False, "medication_instructions": False, "status": "pending_doctor_review"}

        output = {
            "visit_id": visit.id,
            "patient_context_summary": context["patient_context_summary"],
            "relevant_history": context["relevant_history"],
            "risk_factors": context["risk_factors"],
            "recent_labs": context["recent_labs"],
            "medication_list": context["medication_list"],
            "soap_note": soap_note,
            "care_gaps": care_gaps,
            "medication_safety": medication_safety,
            "patient_email_draft": communication["patient_email_draft"],
            "medication_instruction_draft": communication["medication_instruction_draft"],
            "follow_up_summary": communication["follow_up_summary"],
            "proposed_tasks": proposed_tasks,
            "agent_steps": agent_steps,
            "doctor_approval": doctor_approval,
        }
        generated = visit_service.save_generated_output(db, visit.id, output)
        communication_service.upsert_from_generated_output(db, visit, generated)
        audit_service.log_event(db, visit.id, "system", "workflow_draft_generated", {"visit_id": visit.id})
        return visit_service.generated_output_as_response(generated)
