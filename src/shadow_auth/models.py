"""SQLAlchemy 2.0 models for the shared user tables.

Uses bare SQLAlchemy DeclarativeBase rather than Flask-SQLAlchemy's db.Model.
This keeps shadow_auth from instantiating its own SQLAlchemy engine — which
Flask-SQLAlchemy 3.x forbids when the consuming app already has one. Models
are queried through the consuming app's db.session (held in
shadow_auth._state.get_db()).

If a consuming app wants db.create_all() to include shadow_auth's tables
(e.g. for unit tests against sqlite in-memory), it can call:

    from shadow_auth.models import Base as ShadowAuthBase
    ShadowAuthBase.metadata.create_all(bind=db.engine)

In production, Alembic owns the schema — see the migration templates.
"""

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for shadow_auth's models.

    Separate from the consuming app's metadata so importing shadow_auth
    doesn't pollute the app's autogenerate or db.create_all() unless the
    app opts in via Base.metadata.create_all(bind=db.engine).
    """


class UserRole(Base):
    __tablename__ = "user_roles"

    user_role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_role: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<UserRole {self.user_role_id}:{self.user_role}>"


class User(Base, UserMixin):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    user_role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_roles.user_role_id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_confirmation_token: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    # Added by shadow_auth migrations:
    firebase_uid: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)

    role: Mapped[UserRole] = relationship(UserRole, lazy="joined")

    def get_id(self) -> str:
        """Flask-Login stores this in the session cookie. Must be a string."""
        return str(self.user_id)

    @property
    def role_name(self) -> str:
        return self.role.user_role if self.role else ""

    def __repr__(self) -> str:
        return f"<User {self.user_id}:{self.email}>"
