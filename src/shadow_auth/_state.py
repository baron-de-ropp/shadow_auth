"""Module-level handle to the consuming app's Flask-SQLAlchemy instance.

shadow_auth's models inherit from a bare SQLAlchemy DeclarativeBase, not from
the consumer's db.Model. This keeps shadow_auth from creating a second
Flask-SQLAlchemy instance (Flask-SQLAlchemy 3.x forbids more than one per
Flask app). The trade-off is that our models query through the consumer's
db.session — which we hold here so other shadow_auth modules can reach it.

init_app(app, db=...) sets the handle. Code that needs the session calls
get_db() so we fail loudly if init_app hasn't been called yet.
"""

from flask_sqlalchemy import SQLAlchemy

_db: SQLAlchemy | None = None


def set_db(db: SQLAlchemy) -> None:
    global _db
    _db = db


def get_db() -> SQLAlchemy:
    if _db is None:
        raise RuntimeError(
            "shadow_auth is not initialized. Call "
            "shadow_auth.init_app(app, db=your_sqlalchemy_instance) in your "
            "Flask app factory before handling requests."
        )
    return _db
