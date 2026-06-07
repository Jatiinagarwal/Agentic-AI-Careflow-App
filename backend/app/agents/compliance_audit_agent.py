from __future__ import annotations

from typing import Any

from app.safety_rules import AGENT_SAFETY_PRINCIPLES, approval_check_status


class ComplianceAuditAgent:
    name = "Compliance & Audit Agent"

    def pre_approval_check(self) -> dict[str, Any]:
        return {
            "approval_status": "blocked_pending_doctor_approval",
            "safety_status": "safe_for_draft_review",
            "required_controls": AGENT_SAFETY_PRINCIPLES,
            "message": "Draft workflow generated. Simulated actions are blocked until doctor approval is recorded.",
        }

    def post_approval_check(self, approval: dict[str, bool]) -> dict[str, Any]:
        status = approval_check_status(approval)
        return {
            "approval_status": status,
            "safety_status": "doctor_review_recorded" if status == "approved_for_simulated_execution" else "blocked",
            "required_controls": AGENT_SAFETY_PRINCIPLES,
        }

    def post_execution_check(self) -> dict[str, Any]:
        return {
            "approval_status": "executed_after_doctor_approval",
            "safety_status": "simulated_actions_completed_with_audit_trail",
            "required_controls": AGENT_SAFETY_PRINCIPLES,
        }
