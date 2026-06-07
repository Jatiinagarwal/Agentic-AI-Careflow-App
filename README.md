# CareFlow MD

**Tagline:** Agentic Clinical Care Coordination System for Doctors

CareFlow MD is a 48-hour hackathon MVP that turns one doctor visit into an auditable care coordination workflow. It is not a diagnosis bot, prescription bot, patient-facing chatbot, or generic note generator. It is a doctor-in-the-loop workflow assistant that uses mock clinical data, deterministic safety rules, draft generation, approval gates, simulated actions, and an audit trail.

## Safety disclaimer

This project is a hackathon demo using mock patient records only. It does not diagnose, prescribe, send real email, or integrate with any real EHR. All generated content is draft documentation or draft communication. A licensed clinician must review and approve every note, medication instruction, referral/task recommendation, and patient message before use.

## Architecture

```text
React/Vite/Tailwind UI
  -> FastAPI endpoints
  -> SQLite + SQLAlchemy mock clinical database
  -> Agent Orchestrator
      1. Patient Context Agent
      2. Clinical Note Agent
      3. Care Gap Agent
      4. Medication Safety Agent
      5. Patient Communication Agent
      6. Doctor Approval Step
      7. Task Orchestration Agent
      8. Compliance & Audit Agent
      9. Dashboard Update
  -> Simulated EHR/email/tasks/lab reminders
```

OpenAI is used for summarization and drafting when `OPENAI_API_KEY` is configured. If the key is missing or the API call fails, deterministic fallback text is used so the demo still runs.

## Local setup

### Backend

```bash
cd backend
python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows PowerShell
# .\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

Optional OpenAI setup:

```bash
cp ../.env.example .env
# edit backend/.env and set OPENAI_API_KEY
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## Demo patient

The SQLite seed creates one realistic mock patient:

- Rajesh Mehra, 58
- Type 2 diabetes
- Hypertension
- High cholesterol
- Mild kidney function decline
- Previous missed follow-up
- Current medication list
- Previous labs and previous visit notes

Default visit input includes fatigue, increased thirst, elevated BP, high glucose readings, missed HbA1c, and medication adherence uncertainty.

## API endpoints

- `GET /patients`
- `GET /patients/{patient_id}`
- `GET /patients/{patient_id}/history`
- `POST /visits/start`
- `POST /agents/run`
- `POST /approval/approve`
- `POST /actions/execute`
- `GET /dashboard/metrics`
- `GET /audit/{visit_id}`

## 3-minute demo script

### Minute 1: Fragmented chart problem

Open the dashboard and introduce Rajesh Mehra. Show the timeline: diabetes, hypertension, high cholesterol, mild kidney decline, overdue HbA1c, elevated prior labs, medication adherence uncertainty, and missed follow-up. Explain that doctors usually have to manually connect these signals during the visit.

### Minute 2: Run the agents

Click **Run CareFlow Agents**. Walk through the visible agent timeline. Show that the system summarizes longitudinal history, drafts a SOAP note, identifies care gaps, flags mock medication safety considerations, drafts patient communication, and proposes nurse/admin tasks.

### Minute 3: Doctor approval and simulated execution

Open the output tabs. Emphasize that everything is draft and blocked. Click **Approve All Drafts as Doctor**, then **Execute Approved Actions**. Show simulated EHR note saved, email queued, nurse task created, lab reminder created, appointment follow-up created, and the audit trail. Finish on dashboard impact metrics.

## 30-second elevator pitch

CareFlow MD is an agentic clinical care coordination system for doctors. It does not just write a visit note. It reviews mock longitudinal history, drafts doctor-ready SOAP documentation, detects care gaps, checks mock medication safety rules, prepares patient-friendly follow-up communication, creates operational tasks, blocks every action until doctor approval, and records an audit trail. In a 3-minute demo, it shows how a visit becomes an approved, auditable care workflow.

## Why this is agentic

CareFlow MD decomposes a clinical workflow into specialized agents with explicit handoffs, state, and visible progress. The agents retrieve context, generate drafts, apply rules, create proposed actions, wait for human approval, execute simulated side effects, and produce audit logs. The workflow has memory through SQLite and measurable impact through dashboard metrics.

## Why it can win

Judges see a complete business workflow, not a generic chatbot. The demo has a clear healthcare pain point, polished UI, visible agents, safety guardrails, human approval, operational action simulation, auditability, and an executive dashboard. It maps well to both hackathon tracks: business transformation for clinical care coordination and enterprise operations for task automation.

## What to mock vs. build

Build for the hackathon:

- Mock patient timeline
- Agent orchestration
- OpenAI/fallback generation
- Care gap rules
- Medication safety mock rules
- Approval gate
- Simulated EHR/email/task actions
- Audit trail
- Impact dashboard

Mock intentionally:

- EHR integration
- Email sending
- Authentication
- Real clinical data
- Real prescribing or diagnosis
- Production medical safety logic
- HIPAA/compliance integrations

## Troubleshooting

### Backend: `ModuleNotFoundError`

Run `pip install -r requirements.txt` inside the activated backend virtual environment.

### Frontend cannot connect to backend

Make sure FastAPI is running on `http://localhost:8000`. If you change the API URL, set `VITE_API_URL` before running `npm run dev`.

### OpenAI key missing

This is expected. The demo uses local fallback responses if `OPENAI_API_KEY` is not set.

### SQLite data looks stale

Delete `backend/careflow.db` and restart the backend to reseed mock data.

## Judge Q&A

**Q: Is this diagnosing or prescribing?**  
No. It drafts documentation and coordination support based on doctor-provided visit details and mock chart context. All outputs require doctor approval.

**Q: What makes it agentic rather than a chatbot?**  
It has multiple specialized agents, deterministic rules, workflow state, approval gates, simulated side effects, and an audit trail.

**Q: What is the enterprise value?**  
It reduces documentation burden, improves follow-up consistency, creates accountable tasks, and surfaces care gaps in a measurable workflow.

**Q: How would this become production-grade?**  
Add real EHR integration, identity/access control, consent and privacy controls, medically validated rules, clinician configuration, evaluation harnesses, observability, and compliance review.

## Future roadmap

- EHR sandbox integration with FHIR
- Role-based access control
- Specialty-specific workflow templates
- Clinician feedback loop and prompt evaluations
- Real task routing integration
- Configurable care-gap rules
- Structured output validation for all LLM calls
- Deployment hardening and audit exports

## Deployment plan

Recommended hackathon deployment:

```text
Frontend: Vercel
Backend: Render Web Service
Database: SQLite mock DB seeded on backend startup
OpenAI key: Render backend environment variable only