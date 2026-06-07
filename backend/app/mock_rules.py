from __future__ import annotations

from datetime import date
from typing import Any


def _parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _latest_lab(labs: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    matches = [lab for lab in labs if lab.get("name", "").lower() == name.lower()]
    if not matches:
        return None
    return sorted(matches, key=lambda lab: lab.get("collected_at", ""), reverse=True)[0]


def _numeric_lab_value(lab: dict[str, Any] | None) -> float | None:
    if not lab:
        return None
    try:
        return float(str(lab.get("value", "")).strip())
    except ValueError:
        return None


def identify_care_gaps(patient: dict[str, Any], labs: list[dict[str, Any]], current_visit: dict[str, str]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    today = date.today()
    visit_text = " ".join(current_visit.values()).lower()

    hba1c = _latest_lab(labs, "HbA1c")
    hba1c_date = _parse_iso_date(hba1c.get("collected_at", "")) if hba1c else None
    if not hba1c or not hba1c_date or (today - hba1c_date).days > 90 or "missed" in visit_text:
        gaps.append(
            {
                "gap": "HbA1c overdue",
                "priority": "High",
                "evidence": "Last HbA1c is older than 90 days or the visit note states the patient missed the test.",
                "recommended_follow_up_action": "Order repeat HbA1c and assign lab reminder before checkout.",
            }
        )

    if "bp" in visit_text or "blood pressure" in visit_text or "154/94" in visit_text:
        gaps.append(
            {
                "gap": "Blood pressure follow-up required",
                "priority": "High",
                "evidence": "Current visit vitals indicate elevated blood pressure.",
                "recommended_follow_up_action": "Create nurse BP log review task and schedule follow-up appointment.",
            }
        )

    if "adherence" in visit_text or "missed" in visit_text or "unsure" in visit_text:
        gaps.append(
            {
                "gap": "Medication adherence discussion needed",
                "priority": "Medium",
                "evidence": "Current visit details mention uncertainty or missed doses.",
                "recommended_follow_up_action": "Document adherence conversation and provide patient-friendly medication routine instructions.",
            }
        )

    egfr = _latest_lab(labs, "eGFR")
    egfr_value = _numeric_lab_value(egfr)
    if egfr_value is not None and egfr_value < 60:
        gaps.append(
            {
                "gap": "Kidney function monitoring needed",
                "priority": "Medium",
                "evidence": f"Latest mock eGFR is {egfr_value:g}, consistent with mild decline requiring monitoring.",
                "recommended_follow_up_action": "Order kidney function panel and review medication safety considerations.",
            }
        )

    if "thirst" in visit_text or "glucose" in visit_text:
        gaps.append(
            {
                "gap": "Diabetes control review needed",
                "priority": "High",
                "evidence": "Current visit mentions increased thirst or high glucose readings.",
                "recommended_follow_up_action": "Review home glucose log and reinforce follow-up plan after labs result.",
            }
        )

    return gaps


def medication_safety_checks(
    medications: list[dict[str, Any]],
    conditions: list[str],
    labs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    med_names = {med.get("name", "").lower() for med in medications}
    condition_text = " ".join(conditions).lower()
    flags: list[dict[str, Any]] = []

    egfr = _latest_lab(labs, "eGFR")
    egfr_value = _numeric_lab_value(egfr)
    potassium = _latest_lab(labs, "Potassium")
    potassium_value = _numeric_lab_value(potassium)

    if "metformin" in med_names and egfr_value is not None and egfr_value < 60:
        flags.append(
            {
                "severity": "Monitor",
                "flag": "Metformin with reduced eGFR",
                "mock_rule": "If eGFR is below 60, prompt clinician to monitor kidney function while metformin is listed.",
                "doctor_review_note": "Decision support only: verify current renal function, dose appropriateness, and local guidelines.",
            }
        )

    if "lisinopril" in med_names and potassium_value is not None and potassium_value >= 4.8:
        flags.append(
            {
                "severity": "Monitor",
                "flag": "ACE inhibitor with upper-normal potassium",
                "mock_rule": "If lisinopril is listed and potassium is near high range, suggest potassium monitoring.",
                "doctor_review_note": "Decision support only: review potassium trend and kidney function before changing therapy.",
            }
        )

    if "mild kidney function decline" in condition_text or (egfr_value is not None and egfr_value < 60):
        flags.append(
            {
                "severity": "Counseling",
                "flag": "Kidney function decline: avoid unsupervised OTC NSAID use",
                "mock_rule": "For kidney decline and hypertension, remind clinician to discuss OTC NSAID safety if relevant.",
                "doctor_review_note": "Decision support only: include patient counseling only if clinically appropriate.",
            }
        )

    if not flags:
        flags.append(
            {
                "severity": "None",
                "flag": "No mock medication safety issues detected",
                "mock_rule": "Demo rules did not detect a configured concern.",
                "doctor_review_note": "Medication safety review still requires clinician judgment.",
            }
        )

    return flags


def propose_tasks(care_gaps: list[dict[str, Any]], safety_flags: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = [
        {
            "task_type": "ehr_note",
            "title": "Save doctor-approved SOAP note to mock EHR",
            "description": "Simulated EHR save after doctor approval.",
            "owner": "Physician",
        },
        {
            "task_type": "patient_email",
            "title": "Queue doctor-approved patient follow-up email",
            "description": "Simulated email queue; no real email is sent.",
            "owner": "Front desk",
        },
    ]

    for gap in care_gaps:
        title = gap.get("gap", "Care gap follow-up")
        if "HbA1c" in title:
            task_type = "lab_reminder"
            owner = "Nurse"
        elif "Blood pressure" in title:
            task_type = "bp_follow_up"
            owner = "Nurse"
        elif "Medication adherence" in title:
            task_type = "adherence_call"
            owner = "Care coordinator"
        elif "Kidney" in title:
            task_type = "lab_order_reminder"
            owner = "Nurse"
        else:
            task_type = "follow_up"
            owner = "Clinic team"
        tasks.append(
            {
                "task_type": task_type,
                "title": title,
                "description": gap.get("recommended_follow_up_action", "Review care gap."),
                "owner": owner,
            }
        )

    if safety_flags:
        tasks.append(
            {
                "task_type": "medication_safety_review",
                "title": "Review mock medication safety flags",
                "description": "Clinician to review decision-support flags before finalizing patient instructions.",
                "owner": "Physician",
            }
        )

    return tasks
