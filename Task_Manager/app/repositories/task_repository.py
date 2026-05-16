from sqlalchemy.orm import Session

from app.models.task import Task


def count_team_tasks(
    db: Session,
    team_id: int,
    *,
    status: str | None = None,
) -> int:
    q = db.query(Task).filter(Task.team_id == team_id, Task.deleted_at.is_(None))
    if status is not None:
        q = q.filter(Task.status == status)
    return q.count()


def list_team_tasks_page(
    db: Session,
    team_id: int,
    *,
    page: int,
    limit: int,
    status: str | None = None,
) -> list[Task]:
    q = db.query(Task).filter(Task.team_id == team_id, Task.deleted_at.is_(None))
    if status is not None:
        q = q.filter(Task.status == status)
    offset = (page - 1) * limit
    return q.order_by(Task.id.asc()).offset(offset).limit(limit).all()


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id, Task.deleted_at.is_(None)).first()


def add_task(db: Session, task: Task) -> Task:
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def refresh_task(db: Session, task: Task) -> Task:
    db.commit()
    db.refresh(task)
    return task
