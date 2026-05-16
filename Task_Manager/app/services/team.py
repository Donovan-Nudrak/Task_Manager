from sqlalchemy.orm import Session

from app.models.enums import TeamRole
from app.models.team import Team, TeamMember
from app.repositories import team_repository
from app.schemas.team import TeamCreate


def create_team(db: Session, team_data: TeamCreate, owner_id: int) -> Team:
    team = Team(name=team_data.name, description=team_data.description, owner_id=owner_id)
    return team_repository.create_team_with_owner(db, team, owner_id)


def join_team(db: Session, team_id: int, user_id: int) -> TeamMember:
    team = team_repository.get_team_active(db, team_id)
    if team is None:
        raise ValueError("Team not found")

    existing = team_repository.get_membership(db, team_id, user_id)
    if existing:
        raise ValueError("User already belongs to this team")

    member = TeamMember(user_id=user_id, team_id=team_id, role=TeamRole.member)
    return team_repository.add_member(db, member)


def get_team(db: Session, team_id: int) -> Team | None:
    return team_repository.get_team_active(db, team_id)


def get_user_teams(db: Session, user_id: int) -> list[Team]:
    return team_repository.list_teams_for_user(db, user_id)
