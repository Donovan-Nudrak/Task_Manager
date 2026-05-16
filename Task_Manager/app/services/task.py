from sqlalchemy.orm import Session

from app.models.enums import TeamRole
from app.models.task import Task
from app.repositories import task_repository, team_repository
from app.schemas.task import TaskCreate
from app.services.permissions import PermissionService


def _team_member(db: Session, team_id: int, user_id: int) -> bool:
    if team_repository.get_team_active(db, team_id) is None:
        return False
    return team_repository.get_membership(db, team_id, user_id) is not None


def create_task(db: Session, task_data: TaskCreate, created_by: int) -> Task:
    PermissionService(db).require_min_role(task_data.team_id, created_by, TeamRole.member)

    if task_data.assigned_to is not None and not _team_member(db, task_data.team_id, task_data.assigned_to):
        raise ValueError("Assigned user is not a member of this team")

    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status.value,
        priority=task_data.priority.value,
        team_id=task_data.team_id,
        created_by=created_by,
        assigned_to=task_data.assigned_to,
    )
    return task_repository.add_task(db, task)


def get_team_tasks_page(
    db: Session,
    team_id: int,
    user_id: int,
    *,
    page: int,
    limit: int,
    status: str | None,
) -> tuple[list[Task], int]:
    if not _team_member(db, team_id, user_id):
        raise ValueError("You are not a member of this team")
    total = task_repository.count_team_tasks(db, team_id, status=status)
    items = task_repository.list_team_tasks_page(db, team_id, page=page, limit=limit, status=status)
    return items, total


def update_task_status(db: Session, task_id: int, status: str, user_id: int) -> Task:
    task = task_repository.get_task(db, task_id)
    if task is None:
        raise ValueError("Task not found")
    PermissionService(db).require_min_role(task.team_id, user_id, TeamRole.member)
    task.status = status
    return task_repository.refresh_task(db, task)
