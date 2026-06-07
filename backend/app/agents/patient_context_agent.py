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
        allergies = history.get("allergies", [])
        care_gaps = history.get("care_gaps", [])
        tasks = history.get("tasks", [])

        fallback = (
            f"{patient['name']} is a {patient['age']}-year-old patient with "
            f"{', '.join(patient.get('conditions', []))}. Risk level is {patient.get('risk_level', 'unknown')}. "
            f"Relevant record includes {len(medications)} active medication records, {len(allergies)} allergy records, "
            f"{len(labs)} recent lab records, {len(previous_visits)} prior visit notes, {len(care_gaps)} care-gap records, "
            f"and {len(tasks)} follow-up tasks. Clinical workflow should focus on unresolved care gaps, recent labs, "
            "medication adherence, follow-up completion, and doctor-reviewed documentation."
        )

        system_prompt = (
            "You are a clinical documentation support agent for a doctor-in-the-loop workflow. "
            "Summarize full mock longitudinal patient record context without diagnosing, prescribing, or creating patient-facing advice. "
            "Include conditions, medications, allergies, recent labs, prior visits, care gaps, and open tasks. Keep it concise."
        )
        user_prompt = json.dumps(
            {
                "patient": patient,
                "conditions": history.get("conditions", []),
                "allergies": allergies,
                "medications": medications,
                "labs": labs,
                "previous_visits": previous_visits,
                "care_gaps": care_gaps,
                "tasks": tasks,
            },
            indent=2,
        )
        summary = openai_service.generate_text(system_prompt, user_prompt, fallback, max_output_tokens=600)

        return {
            "patient_context_summary": summary,
            "relevant_history": previous_visits,
            "risk_factors": patient["risk_factors"],
            "recent_labs": labs,
            "medication_list": medications,
        }
