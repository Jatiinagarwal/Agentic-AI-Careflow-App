from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.mock_rules import propose_tasks
from app.models import GeneratedOutput, Visit
from app.services.task_service import create_tasks_from_proposals, task_statuses


class TaskOrchestrationAgent:
    name = "Task Orchestration Agent"

    def propose(self, care_gaps: list[dict[str, Any]], medication_safety: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return propose_tasks(care_gaps, medication_safety)

    def execute(self, db: Session, visit: Visit, generated: GeneratedOutput) -> dict[str, Any]:
        tasks = create_tasks_from_proposals(db, visit, generated)
        action_log = [
            {"action": "mock_ehr_note_saved", "status": "completed", "detail": "SOAP note saved to simulated EHR."},
            {"action": "mock_patient_email_queued", "status": "completed", "detail": "Patient email placed in simulated queue; no real email sent."},
            {"action": "nurse_follow_up_task_created", "status": "completed", "detail": "Nurse/care team tasks created from approved proposals."},
            {"action": "lab_reminder_created", "status": "completed", "detail": "HbA1c and kidney monitoring reminders simulated where applicable."},
            {"action": "appointment_follow_up_created", "status": "completed", "detail": "Follow-up scheduling task simulated."},
        ]
        return {"action_log": action_log, "task_statuses": task_statuses(tasks)}
