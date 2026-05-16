from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_team_member
from app.models.user import User
from app.schemas.task import TaskCreate, TaskPage, TaskResponse, TaskStatus
from app.services.task import create_task, get_team_tasks_page, update_task_status

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    try:
        return create_task(db, task_data, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/team/{team_id}", response_model=TaskPage)
def list_for_team(
    team_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: TaskStatus | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_team_member),
):
    status_filter = status.value if status is not None else None
    try:
        items, total = get_team_tasks_page(
            db,
            team_id,
            current_user.id,
            page=page,
            limit=limit,
            status=status_filter,
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    return TaskPage(items=items, page=page, limit=limit, total=total)


@router.patch("/{task_id}/status", response_model=TaskResponse)
def update_status(
    task_id: int,
    status: TaskStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskResponse:
    try:
        return update_task_status(db, task_id, status.value, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
