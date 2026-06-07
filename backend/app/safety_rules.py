SAFETY_DISCLAIMER = (
    "CareFlow MD is a hackathon demo using mock patient records only. "
    "Generated content is draft clinical documentation and care coordination support. "
    "It is not autonomous diagnosis, prescribing, or patient-facing medical advice. "
    "A licensed clinician must review and approve every note, instruction, referral, task, and message before use."
)

DRAFT_LABEL = "DRAFT - Doctor review and approval required"

AGENT_SAFETY_PRINCIPLES = [
    "No autonomous diagnosis",
    "No autonomous prescribing",
    "Mock patient data only",
    "Doctor approval required before actions",
    "Generated content labeled as draft",
    "Rule-based mock medication safety support only",
    "Audit trail captured for agent outputs, approvals, and simulated actions",
]


def enforce_draft_label(text: str) -> str:
    if text.startswith(DRAFT_LABEL):
        return text
    return f"{DRAFT_LABEL}\n\n{text}"


def approval_check_status(approval: dict) -> str:
    required_keys = [
        "soap_note",
        "patient_email",
        "follow_up_tasks",
        "medication_instructions",
    ]
    if all(approval.get(key) is True for key in required_keys):
        return "approved_for_simulated_execution"
    return "blocked_pending_doctor_approval"
