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
# .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

Optional OpenAI setup:

```bash
cp .env.example .env
# edit backend/.env and set OPENAI_API_KEY
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

Optional frontend env setup:

```bash
cp .env.example .env.local
# default: VITE_API_BASE_URL=http://localhost:8000
```

## Environment variables

### Backend variables

Set these in `backend/.env` locally or in the Render service Environment tab.

```text
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./careflow.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ENVIRONMENT=local
```

`OPENAI_API_KEY` must never be placed in the frontend. If it is missing, the app uses fallback mock responses so the demo still works.

### Frontend variables

Set this in `frontend/.env.local` locally or in the Vercel project Environment Variables.

```text
VITE_API_BASE_URL=http://localhost:8000
```

For production, use your Render backend URL:

```text
VITE_API_BASE_URL=https://your-careflow-md-backend.onrender.com
```

## Deployment plan

Recommended hackathon deployment:

```text
Frontend: Vercel
Backend: Render Web Service
Database: SQLite mock DB seeded on backend startup
OpenAI key: Render backend environment variable only
```

### Render backend settings

Use a Render Web Service with these settings:

```text
Root directory: backend
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set these Render environment variables:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./careflow.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://your-careflow-md.vercel.app
ENVIRONMENT=production
```

After deployment, test:

```text
https://your-render-backend.onrender.com/health
https://your-render-backend.onrender.com/patients
https://your-render-backend.onrender.com/dashboard/metrics
```

### Vercel frontend settings

Use these Vercel settings:

```text
Framework preset: Vite
Root directory: frontend
Install command: npm install
Build command: npm run build
Output directory: dist
```

Set this Vercel environment variable:

```text
VITE_API_BASE_URL=https://your-render-backend.onrender.com
```

After changing a Vercel environment variable, redeploy the frontend.

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

- `GET /`
- `GET /health`
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

### Backend: `ModuleNotFoundError: No module named 'app'`

Run the backend from the backend folder:

```bash
cd backend
uvicorn app.main:app --reload
```

Or from the project root:

```bash
uvicorn app.main:app --reload --app-dir backend
```

### Frontend: `npm` is not recognized

Install Node.js LTS, close all terminals, open a new terminal, then verify:

```bash
node -v
npm -v
```

### Frontend: `package.json` not found

Run npm commands from the frontend folder:

```bash
cd frontend
npm install
npm run dev
```

### Frontend cannot connect to backend locally

Make sure FastAPI is running on `http://localhost:8000`. If you change the API URL, set this in `frontend/.env.local`:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Then restart the Vite dev server.

### Deployed frontend cannot connect to deployed backend

Check all three items:

1. Vercel has `VITE_API_BASE_URL=https://your-render-backend.onrender.com`.
2. Render has `CORS_ORIGINS=https://your-vercel-app.vercel.app` plus localhost values if needed.
3. Both frontend and backend were redeployed after environment variable changes.

### OpenAI key missing

This is expected during local testing. The demo uses local fallback responses if `OPENAI_API_KEY` is not set.

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

## Phase 10: Real Email Sending Setup

CareFlow MD supports doctor-approved real email sending through SMTP, but it is disabled by default.

Safety rules:

- Agents only draft emails.
- Doctors approve and send emails.
- `/actions/execute` does not send real email.
- Real sending only works when `EMAIL_ENABLED=true` and SMTP settings are configured.
- If email is disabled or incomplete, sending is safely recorded as `Mock Sent`.
- Never use real patient data for hackathon demos.
- Never commit `.env` files or SMTP passwords.

### Local SMTP configuration

Copy the backend example file:

```bash
cd backend
cp .env.example .env
```

Set email variables in `backend/.env`:

```env
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=CareFlow MD
SMTP_USE_TLS=true
```

For Gmail, use an app password rather than your normal account password. Test only with your own email address.

### Testing mock email mode

With `EMAIL_ENABLED=false`:

1. Run the backend and frontend.
2. Run the CareFlow agent workflow.
3. Approve generated drafts.
4. Execute simulated actions.
5. Open Communications.
6. Preview the email, approve it, and click Send Email.
7. Status should become `Mock Sent`.
8. Audit trail should show `EMAIL_SEND_ATTEMPTED` and `EMAIL_MOCK_SENT`.

### Testing real SMTP mode

With `EMAIL_ENABLED=true` and valid SMTP settings:

1. Use your own email address as the mock patient email.
2. Run workflow and generate communication draft.
3. Edit the draft if needed.
4. Approve the email.
5. Click Send Email and confirm.
6. Status should become `Sent`.
7. Audit trail should show `EMAIL_SENT`.

If SMTP credentials are wrong, status becomes `Failed` and the error is stored without crashing the app.
