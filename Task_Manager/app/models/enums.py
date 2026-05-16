from enum import Enum


class TeamRole(str, Enum):
    viewer = "viewer"
    member = "member"
    manager = "manager"
    admin = "admin"
    owner = "owner"
