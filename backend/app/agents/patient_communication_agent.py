from __future__ import annotations

import json
from typing import Any

from app.openai_service import OpenAIService
from app.safety_rules import DRAFT_LABEL, enforce_draft_label


class PatientCommunicationAgent:
    name = "Patient Communication Agent"

    def run(
        self,
        patient_name: str,
        doctor_plan: str,
        care_gaps: list[dict[str, Any]],
        medication_safety: list[dict[str, Any]],
        openai_service: OpenAIService,
    ) -> dict[str, str]:
        care_gap_lines = "\n".join(
            f"- {gap.get('gap')}: {gap.get('recommended_follow_up_action')}" for gap in care_gaps
        )
        safety_lines = "\n".join(f"- {flag.get('flag')}: {flag.get('doctor_review_note')}" for flag in medication_safety)

        fallback_email = enforce_draft_label(
            f"Dear {patient_name},\n\n"
            "Thank you for your visit today. Your doctor would like you to complete the recommended lab work, "
            "keep a home blood pressure and glucose log as discussed, and follow the care team's scheduling instructions. "
            "Please contact the clinic if you have questions or if symptoms worsen.\n\n"
            "This message is a draft and will only be sent after doctor review and approval."
        )
        fallback_med_instructions = enforce_draft_label(
            "Continue medications only as your doctor has instructed. Bring your medication bottles or an updated list to the next visit. "
            "Do not change doses or stop medications based on this draft. The care team may review kidney function and potassium monitoring."
        )
        fallback_summary = (
            "Patient communication draft prepared for doctor review: lab reminder, BP/glucose tracking, adherence support, and follow-up scheduling."
        )

        system_prompt = (
            "You write patient-friendly draft communication for a doctor-in-the-loop healthcare workflow. "
            "Do not provide independent medical advice, diagnosis, or prescribing. Clearly label as draft and doctor review required. "
            "Use warm, plain language."
        )
        user_prompt = json.dumps(
            {
                "patient_name": patient_name,
                "doctor_plan": doctor_plan,
                "care_gaps": care_gap_lines,
                "medication_safety_notes_for_doctor": safety_lines,
                "required_label": DRAFT_LABEL,
            },
            indent=2,
        )
        email = openai_service.generate_text(system_prompt, user_prompt, fallback_email, max_output_tokens=700)

        med_prompt = json.dumps(
            {
                "patient_name": patient_name,
                "doctor_plan": doctor_plan,
                "medication_safety_notes_for_doctor": safety_lines,
                "instruction": "Create brief medication routine instructions that remind patient not to change medications without clinician direction.",
                "required_label": DRAFT_LABEL,
            },
            indent=2,
        )
        medication_instructions = openai_service.generate_text(
            system_prompt,
            med_prompt,
            fallback_med_instructions,
            max_output_tokens=450,
        )

        return {
            "patient_email_draft": enforce_draft_label(email),
            "medication_instruction_draft": enforce_draft_label(medication_instructions),
            "follow_up_summary": fallback_summary,
        }
