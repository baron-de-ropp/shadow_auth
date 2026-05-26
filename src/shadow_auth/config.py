"""init_app — wire shadow_auth into a Flask app.

Call this in the consuming app's factory AFTER its Flask-SQLAlchemy `db`
has been instantiated (but before any auth-dependent blueprint handles a
request). It:

  1. Validates SECRET_KEY, SQLALCHEMY_DATABASE_URI, and warns on a
     SESSION_COOKIE_DOMAIN that won't carry across subdomains.
  2. Stashes the consumer's db so shadow_auth's user_loader and login
     route can query through it (we don't instantiate our own
     Flask-SQLAlchemy — Flask-SQLAlchemy 3.x forbids two per app).
  3. Initializes Flask-Login's LoginManager on the app.

The consuming app registers `auth_bp` itself so it can choose the URL
prefix (or omit it). For unit-test setups that want shadow_auth's tables
created on a sqlite in-memory DB, call:

    from shadow_auth.models import Base as ShadowAuthBase
    ShadowAuthBase.metadata.create_all(bind=db.engine)
"""

import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from shadow_auth._state import set_db
from shadow_auth.login_manager import login_manager

logger = logging.getLogger(__name__)


def init_app(app: Flask, *, db: SQLAlchemy) -> None:
    _validate_config(app)
    set_db(db)
    login_manager.init_app(app)
    logger.info("shadow_auth initialized on app %r", app.name)


def _validate_config(app: Flask) -> None:
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "shadow_auth requires app.config['SECRET_KEY']. For cross-subdomain "
            "SSO this must match every other app sharing this session cookie "
            "domain (typically read from the FLASK_SECRET_KEY env var)."
        )

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "shadow_auth requires app.config['SQLALCHEMY_DATABASE_URI']. "
            "Typically read from the DATABASE_URL env var."
        )

    cookie_domain = app.config.get("SESSION_COOKIE_DOMAIN")
    if cookie_domain and not cookie_domain.startswith("."):
        logger.warning(
            "SESSION_COOKIE_DOMAIN=%r has no leading dot — cross-subdomain "
            "SSO won't work. Set it to '.yourdomain.com' for prod.",
            cookie_domain,
        )
