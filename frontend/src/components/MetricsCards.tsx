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
      detail: 'Simulated only; no real email sent',
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
