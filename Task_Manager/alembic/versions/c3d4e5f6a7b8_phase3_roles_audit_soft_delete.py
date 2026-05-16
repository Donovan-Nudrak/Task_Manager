"""phase_3_roles_audit_soft_delete

Revision ID: c3d4e5f6a7b8
Revises: f8e9d7c6b5a4
Create Date: 2026-05-16

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "f8e9d7c6b5a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column("users", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column(
        "teams",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column(
        "teams",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column("teams", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    op.add_column(
        "tasks",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.add_column("tasks", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        "CREATE TYPE team_role AS ENUM ('owner', 'admin', 'manager', 'member', 'viewer')"
    )
    op.execute(
        """
        ALTER TABLE team_members
          ALTER COLUMN role DROP DEFAULT,
          ALTER COLUMN role TYPE team_role USING (
            CASE trim(role::text)
              WHEN 'owner' THEN 'owner'::team_role
              WHEN 'member' THEN 'member'::team_role
              ELSE 'member'::team_role
            END
          )
        """
    )
    op.execute("ALTER TABLE team_members ALTER COLUMN role SET DEFAULT 'member'::team_role")


def downgrade() -> None:
    op.execute("ALTER TABLE team_members ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE team_members ALTER COLUMN role TYPE VARCHAR(50) USING role::text")
    op.execute("ALTER TABLE team_members ALTER COLUMN role SET DEFAULT 'member'")
    op.execute("DROP TYPE team_role")

    op.drop_column("tasks", "deleted_at")
    op.drop_column("tasks", "updated_at")

    op.drop_column("teams", "deleted_at")
    op.drop_column("teams", "updated_at")
    op.drop_column("teams", "created_at")

    op.drop_column("users", "deleted_at")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
