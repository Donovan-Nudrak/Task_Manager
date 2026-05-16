from sqlalchemy.orm import Session

from app.models.enums import TeamRole
from app.models.team import Team, TeamMember


def get_team_active(db: Session, team_id: int) -> Team | None:
    return db.query(Team).filter(Team.id == team_id, Team.deleted_at.is_(None)).first()


def list_teams_for_user(db: Session, user_id: int) -> list[Team]:
    return (
        db.query(Team)
        .join(TeamMember)
        .filter(TeamMember.user_id == user_id, Team.deleted_at.is_(None))
        .all()
    )


def get_membership(db: Session, team_id: int, user_id: int) -> TeamMember | None:
    return (
        db.query(TeamMember)
        .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
        .first()
    )


def create_team_with_owner(db: Session, team: Team, owner_id: int) -> Team:
    db.add(team)
    db.flush()
    member = TeamMember(user_id=owner_id, team_id=team.id, role=TeamRole.owner)
    db.add(member)
    db.commit()
    db.refresh(team)
    return team


def add_member(db: Session, member: TeamMember) -> TeamMember:
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
