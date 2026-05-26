"""Smoke tests — confirm the package's public API imports and wires up cleanly.

End-to-end testing (a real login round-trip against a Postgres) lives in the
consuming app's test suite, not here, because that's where the realistic
shared-DB scenario exists.
"""

import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from shadow_auth import Base, User, UserRole, auth_bp, init_app, login_manager


def _make_app(*, set_secret=True, set_db_uri=True) -> Flask:
    app = Flask(__name__)
    if set_secret:
        app.config["SECRET_KEY"] = "test-secret"
    if set_db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


def _make_db(app: Flask) -> SQLAlchemy:
    db = SQLAlchemy()
    db.init_app(app)
    return db


def test_public_api_exports():
    assert User is not None
    assert UserRole is not None
    assert Base is not None
    assert login_manager is not None
    assert auth_bp.name == "auth"


def test_init_app_wires_login_manager():
    app = _make_app()
    db = _make_db(app)
    init_app(app, db=db)

    assert app.login_manager is login_manager


def test_init_app_fails_without_secret_key():
    app = _make_app(set_secret=False)
    db = _make_db(app)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        init_app(app, db=db)


def test_init_app_fails_without_db_uri():
    app = _make_app(set_db_uri=False)
    # Use a stub since SQLAlchemy needs a URI to init, but our validation
    # should fire first.
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db = _make_db(app)
    del app.config["SQLALCHEMY_DATABASE_URI"]
    with pytest.raises(RuntimeError, match="SQLALCHEMY_DATABASE_URI"):
        init_app(app, db=db)


def test_models_have_expected_columns():
    cols = {c.name for c in User.__table__.columns}
    expected = {
        "user_id",
        "email",
        "password_hash",
        "user_role_id",
        "is_active",
        "created_at",
        "updated_at",
        "email_confirmation_token",
        "firebase_uid",
        "username",
    }
    assert expected.issubset(cols), f"missing columns: {expected - cols}"


def test_user_get_id_returns_string():
    # Flask-Login requires get_id() to return a string for the session cookie.
    u = User(user_id=42, email="x@y.z", password_hash="x", user_role_id=1)
    assert u.get_id() == "42"
    assert isinstance(u.get_id(), str)


def test_user_loader_returns_none_for_bogus_input():
    """user_loader should refuse garbage without raising."""
    app = _make_app()
    db = _make_db(app)
    init_app(app, db=db)

    with app.app_context():
        # Create the User table on this in-memory sqlite
        Base.metadata.create_all(bind=db.engine)

        from shadow_auth.login_manager import load_user

        assert load_user("") is None
        assert load_user("not-a-number") is None
        # Real-shaped input that doesn't match a row → None
        assert load_user("99999") is None
