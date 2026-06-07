import type { MetricOut } from '../types';

type Props = {
  metrics: MetricOut | null;
};

const defaultMetrics: MetricOut = {
  documentation_time_saved_minutes: 0,
  care_gaps_detected: 0,
  follow_up_tasks_created: 0,
  drafts_awaiting_approval: 0,
  simulated_patient_communication_rate: 0,
  reduced_missed_follow_up_risk: 'Pending workflow run',
  doctor_productivity_impact: 'Run a workflow to calculate impact',
  completed_workflows: 0,
  total_active_patients: 0,
  patients_with_overdue_care_gaps: 0,
  emails_queued: 0,
  mock_emails_sent: 0,
  follow_up_tasks_open: 0,
  actions_completed_after_approval: 0,
};

export default function MetricsCards({ metrics }: Props) {
  const data = metrics ?? defaultMetrics;

  const cards = [
    {
      label: 'Active patients',
      value: data.total_active_patients,
      detail: 'Mock clinic panel',
    },
    {
      label: 'Time saved',
      value: `${data.documentation_time_saved_minutes} min`,
      detail: data.doctor_productivity_impact,
    },
    {
      label: 'Care gaps',
      value: data.care_gaps_detected,
      detail: `${data.patients_with_overdue_care_gaps} patients with overdue gaps`,
    },
    {
      label: 'Open tasks',
      value: data.follow_up_tasks_open,
      detail: `${data.follow_up_tasks_created} total follow-up tasks`,
    },
    {
      label: 'Drafts pending',
      value: data.drafts_awaiting_approval,
      detail: 'Doctor approval required',
    },
    {
      label: 'Emails queued',
      value: data.emails_queued,
      detail: `${data.mock_emails_sent} mock emails sent`,
    },
    {
      label: 'Completed workflows',
      value: data.completed_workflows,
      detail: `${data.actions_completed_after_approval} approved action sets completed`,
    },
    {
      label: 'Communication rate',
      value: `${data.simulated_patient_communication_rate}%`,
      detail: 'Simulated only',
    },
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div key={card.label} className="card p-5">
          <p className="text-sm font-semibold text-slate-500">{card.label}</p>
          <p className="mt-2 text-3xl font-black text-slate-950">{card.value}</p>
          <p className="mt-2 text-sm text-slate-600">{card.detail}</p>
        </div>
      ))}
    </section>
  );
}