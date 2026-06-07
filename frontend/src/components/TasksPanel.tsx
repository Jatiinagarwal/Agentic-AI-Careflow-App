import type { Task } from '../types';

type Props = {
  tasks: Task[];
};

export default function TasksPanel({ tasks }: Props) {
  return (
    <div className="space-y-3">
      {tasks.length === 0 && <p className="text-sm text-slate-600">No patient-specific tasks yet.</p>}
      {tasks.map((task) => (
        <div key={task.id} className="rounded-2xl border border-slate-200 bg-white p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="font-bold text-slate-950">{task.title}</p>
              <p className="mt-1 text-sm text-slate-600">{task.description}</p>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">{task.status}</span>
          </div>
          <p className="mt-2 text-xs font-semibold uppercase tracking-[0.16em] text-blue-700">{task.owner} • {task.task_type}</p>
        </div>
      ))}
    </div>
  );
}
