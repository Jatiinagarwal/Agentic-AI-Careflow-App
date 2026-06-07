from __future__ import annotations

from typing import Any

from app.mock_rules import identify_care_gaps


class CareGapAgent:
    name = "Care Gap Agent"

    def run(self, patient: dict[str, Any], labs: list[dict[str, Any]], current_visit: dict[str, str]) -> list[dict[str, Any]]:
        return identify_care_gaps(patient, labs, current_visit)
