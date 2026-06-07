from sqlalchemy.orm import Session

from app.models import GeneratedOutput, Task, Visit


def create_tasks_from_proposals(db: Session, visit: Visit, generated: GeneratedOutput) -> list[Task]:
    created: list[Task] = []
    existing = db.query(Task).filter(Task.visit_id == visit.id).count()
    if existing:
        return db.query(Task).filter(Task.visit_id == visit.id).order_by(Task.created_at.asc()).all()

    for proposal in generated.proposed_tasks:
        task = Task(
            visit_id=visit.id,
            task_type=proposal.get("task_type", "follow_up"),
            title=proposal.get("title", "Follow-up task"),
            description=proposal.get("description", ""),
            owner=proposal.get("owner", "Clinic team"),
            status="created",
        )
        db.add(task)
        created.append(task)

    db.commit()
    for task in created:
        db.refresh(task)
    return created


def task_statuses(tasks: list[Task]) -> list[dict]:
    return [
        {
            "id": task.id,
            "task_type": task.task_type,
            "title": task.title,
            "owner": task.owner,
            "status": task.status,
        }
        for task in tasks
    ]
