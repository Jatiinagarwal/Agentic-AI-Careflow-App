import type { MetricOut } from '../types';

type Props = {
  metrics: MetricOut | null;
};

const fallbackMetrics: MetricOut = {
  documentation_time_saved_minutes: 0,
  care_gaps_detected: 0,
  follow_up_tasks_created: 0,
  drafts_awaiting_approval: 0,
  simulated_patient_communication_rate: 0,
  reduced_missed_follow_up_risk: 'Run workflow to calculate',
  doctor_productivity_impact: 'Run workflow to calculate',
  completed_workflows: 0,
  total_active_patients: 0,
  patients_with_overdue_care_gaps: 0,
  emails_queued: 0,
  mock_emails_sent: 0,
  follow_up_tasks_open: 0,
  actions_completed_after_approval: 0,
  email_drafts_pending_approval: 0,
  approved_emails_not_sent: 0,
  emails_sent_today: 0,
  failed_email_attempts: 0,
};

export default function MetricsCards({ metrics }: Props) {
  const value = metrics ?? fallbackMetrics;
  const cards = [
    {
      label: 'Documentation time saved',
      value: `${value.documentation_time_saved_minutes} min`,
      detail: value.doctor_productivity_impact,
    },
    {
      label: 'Care gaps detected',
      value: value.care_gaps_detected.toString(),
      detail: 'Rules-driven chronic care follow-up detection',
    },
    {
      label: 'Follow-up tasks created',
      value: value.follow_up_tasks_created.toString(),
      detail: 'Nurse/admin/lab reminders after approval',
    },
    {
      label: 'Drafts awaiting approval',
      value: value.drafts_awaiting_approval.toString(),
      detail: 'Human-in-the-loop safety gate',
    },
    {
      label: 'Patient communication rate',
      value: `${value.simulated_patient_communication_rate}%`,
      detail: `${value.emails_sent_today ?? 0} real sent • ${value.mock_emails_sent} mock sent • ${value.failed_email_attempts ?? 0} failed`,
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      {cards.map((card) => (
        <div key={card.label} className="card p-5 shadow-glow">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">{card.label}</p>
          <p className="mt-3 text-3xl font-bold text-slate-950">{card.value}</p>
          <p className="mt-2 text-sm text-slate-600">{card.detail}</p>
        </div>
      ))}
    </div>
  );
}
