import type { MetricOut } from '../types';
import MetricsCards from './MetricsCards';

type Props = {
  metrics: MetricOut | null;
};

export default function Dashboard({ metrics }: Props) {
  return (
    <section className="relative overflow-hidden rounded-[2rem] border border-blue-100 bg-gradient-to-br from-slate-950 via-blue-950 to-sky-800 p-8 text-white shadow-glow">
      <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl" />
      <div className="absolute -bottom-32 left-1/3 h-72 w-72 rounded-full bg-blue-500/20 blur-3xl" />
      <div className="relative z-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.35em] text-cyan-200">CareFlow MD</p>
            <h1 className="mt-4 max-w-4xl text-4xl font-black tracking-tight md:text-6xl">Agentic Clinical Care Coordination System for Doctors</h1>
            <p className="mt-5 max-w-3xl text-lg text-blue-100">
              Now with patient management, longitudinal medical records, communication queue, task history, and auditable doctor-approved workflows.
            </p>
          </div>
          <div className="rounded-3xl border border-white/20 bg-white/10 p-5 backdrop-blur">
            <p className="text-sm text-blue-100">Safety posture</p>
            <p className="mt-2 text-2xl font-bold">Doctor-in-the-loop</p>
            <p className="mt-2 max-w-xs text-sm text-blue-100">No autonomous diagnosis. No autonomous prescribing. Mock data only.</p>
          </div>
        </div>
        <div className="mt-8 text-slate-950">
          <MetricsCards metrics={metrics} />
        </div>
        <div className="mt-6 grid gap-3 md:grid-cols-4">
          <div className="rounded-2xl bg-white/10 p-4 backdrop-blur"><p className="text-sm text-blue-100">Active patients</p><p className="mt-2 text-2xl font-black">{metrics?.total_active_patients ?? 0}</p></div>
          <div className="rounded-2xl bg-white/10 p-4 backdrop-blur"><p className="text-sm text-blue-100">Overdue care gaps</p><p className="mt-2 text-2xl font-black">{metrics?.patients_with_overdue_care_gaps ?? 0}</p></div>
          <div className="rounded-2xl bg-white/10 p-4 backdrop-blur"><p className="text-sm text-blue-100">Emails queued</p><p className="mt-2 text-2xl font-black">{metrics?.emails_queued ?? 0}</p></div>
          <div className="rounded-2xl bg-white/10 p-4 backdrop-blur"><p className="text-sm text-blue-100">Open tasks</p><p className="mt-2 text-2xl font-black">{metrics?.follow_up_tasks_open ?? 0}</p></div>
        </div>
      </div>
    </section>
  );
}
