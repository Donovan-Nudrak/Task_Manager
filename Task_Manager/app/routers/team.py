from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_team_member
from app.models.user import User
from app.schemas.team import TeamCreate, TeamMemberResponse, TeamResponse
from app.services.team import create_team, get_team, get_user_teams, join_team

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamResponse, status_code=201)
def create(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_team(db, team_data, current_user.id)


@router.post("/{team_id}/join", response_model=TeamMemberResponse)
def join(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return join_team(db, team_id, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=404 if str(exc) == "Team not found" else 400, detail=str(exc))


@router.get("/", response_model=list[TeamResponse])
def my_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_teams(db, current_user.id)


@router.get("/{team_id}", response_model=TeamResponse)
def get(
    team_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_team_member),
):
    team = get_team(db, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
