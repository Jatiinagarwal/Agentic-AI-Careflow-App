from __future__ import annotations

import json
from typing import Any

from app.openai_service import OpenAIService


class PatientContextAgent:
    name = "Patient Context Agent"

    def run(self, history: dict[str, Any], openai_service: OpenAIService) -> dict[str, Any]:
        patient = history["patient"]
        medications = history["medications"]
        labs = history["labs"]
        previous_visits = history["previous_visits"]

        fallback = (
            f"{patient['name']} is a {patient['age']}-year-old patient with "
            f"{', '.join(patient['conditions'])}. Key longitudinal issues include missed HbA1c follow-up, "
            "elevated glucose and blood pressure trends, medication adherence uncertainty, and mild kidney function decline. "
            "Recent records support a chronic care coordination visit focused on labs, adherence, BP follow-up, and renal monitoring."
        )

        system_prompt = (
            "You are a clinical documentation support agent for a doctor-in-the-loop workflow. "
            "Summarize mock longitudinal patient context without diagnosing, prescribing, or creating patient-facing advice. "
            "Keep it concise and useful for a physician visit."
        )
        user_prompt = json.dumps(
            {
                "patient": patient,
                "medications": medications,
                "labs": labs,
                "previous_visits": previous_visits,
            },
            indent=2,
        )
        summary = openai_service.generate_text(system_prompt, user_prompt, fallback, max_output_tokens=500)

        return {
            "patient_context_summary": summary,
            "relevant_history": previous_visits,
            "risk_factors": patient["risk_factors"],
            "recent_labs": labs,
            "medication_list": medications,
        }
