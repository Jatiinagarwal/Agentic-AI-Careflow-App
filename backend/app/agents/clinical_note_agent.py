from __future__ import annotations

import json
from typing import Any

from app.openai_service import OpenAIService
from app.safety_rules import DRAFT_LABEL


class ClinicalNoteAgent:
    name = "Clinical Note Agent"

    def run(
        self,
        patient_context_summary: str,
        current_visit: dict[str, str],
        openai_service: OpenAIService,
    ) -> dict[str, Any]:
        fallback_sections = {
            "subjective": (
                f"Chief complaint: {current_visit.get('chief_complaint', '')}. "
                f"Symptoms/context documented by doctor: {current_visit.get('symptoms', '')}."
            ),
            "objective": f"Vitals and objective data provided: {current_visit.get('vitals', '')}. Prior labs and medication list reviewed from mock chart.",
            "assessment_draft": (
                "Draft documentation based on doctor-provided visit details and prior mock chart context. "
                "No autonomous diagnosis is made by the system."
            ),
            "plan_draft": current_visit.get("suggested_plan", "Plan to be reviewed and finalized by doctor."),
            "doctor_review_required_flag": True,
        }
        fallback_note = (
            f"{DRAFT_LABEL}\n\n"
            f"S: {fallback_sections['subjective']}\n\n"
            f"O: {fallback_sections['objective']}\n\n"
            f"A: {fallback_sections['assessment_draft']}\n\n"
            f"P: {fallback_sections['plan_draft']}\n\n"
            "Safety note: This SOAP note is draft documentation support and requires doctor review."
        )

        system_prompt = (
            "You draft doctor-ready SOAP documentation from doctor-provided information and mock chart context. "
            "Do not introduce new diagnoses. Do not prescribe. Label the note as draft and doctor review required. "
            "Use concise clinical language."
        )
        user_prompt = json.dumps(
            {
                "patient_context_summary": patient_context_summary,
                "current_visit_details": current_visit,
                "required_label": DRAFT_LABEL,
            },
            indent=2,
        )
        full_note = openai_service.generate_text(system_prompt, user_prompt, fallback_note, max_output_tokens=850)

        return {
            **fallback_sections,
            "full_note": full_note,
        }
