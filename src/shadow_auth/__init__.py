"""shadow_auth — Shared Flask-Login auth for thearcanelibrary.com apps.

Public API:
    init_app(app, *, db) — wire shadow_auth's LoginManager into a Flask app,
                           sharing the app's existing Flask-SQLAlchemy db
    auth_bp              — blueprint exposing /login and /logout
    login_manager        — the Flask-Login LoginManager (already configured)
    User, UserRole       — SQLAlchemy models pointing at public.users /
                           public.user_roles (bare DeclarativeBase, not the
                           consumer's db.Model — see models.py for why)
    Base                 — shadow_auth's declarative base; expose it if you
                           want to db.create_all(bind=db.engine) shadow_auth's
                           tables in test setup
"""

from shadow_auth.blueprint import auth_bp
from shadow_auth.config import init_app
from shadow_auth.login_manager import login_manager
from shadow_auth.models import Base, User, UserRole

__version__ = "0.1.0"

__all__ = [
    "Base",
    "User",
    "UserRole",
    "auth_bp",
    "init_app",
    "login_manager",
]
