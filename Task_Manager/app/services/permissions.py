from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.enums import TeamRole
from app.models.team import TeamMember

ROLE_LEVEL: dict[TeamRole, int] = {
    TeamRole.viewer: 10,
    TeamRole.member: 20,
    TeamRole.manager: 30,
    TeamRole.admin: 40,
    TeamRole.owner: 50,
}


class PermissionService:
    """Centralises authorisation checks for team-scoped actions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def _parse_role(self, raw: TeamRole | str) -> TeamRole:
        if isinstance(raw, TeamRole):
            return raw
        try:
            return TeamRole(raw)
        except ValueError:
            raise HTTPException(status_code=403, detail="Invalid team role")

    def get_membership(self, team_id: int, user_id: int) -> TeamMember | None:
        return (
            self.db.query(TeamMember)
            .filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id)
            .first()
        )

    def require_membership(self, team_id: int, user_id: int) -> TeamMember:
        member = self.get_membership(team_id, user_id)
        if member is None:
            raise HTTPException(status_code=403, detail="You are not a member of this team")
        return member

    def require_min_role(self, team_id: int, user_id: int, minimum: TeamRole) -> TeamMember:
        member = self.require_membership(team_id, user_id)
        role = self._parse_role(member.role)
        if ROLE_LEVEL[role] < ROLE_LEVEL[minimum]:
            raise HTTPException(status_code=403, detail="Insufficient permissions for this action")
        return member
