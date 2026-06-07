from __future__ import annotations

from typing import Any

from app.mock_rules import medication_safety_checks


class MedicationSafetyAgent:
    name = "Medication Safety Agent"

    def run(
        self,
        medications: list[dict[str, Any]],
        conditions: list[str],
        labs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return medication_safety_checks(medications, conditions, labs)
