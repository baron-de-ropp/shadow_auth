"""Preconfigured Flask-Login LoginManager + user_loader.

The user_loader receives the string that login_user() stored in the session
cookie (User.get_id() — the integer user_id as a string) and returns the
matching User object, or None to log out the session.

This same loader works in every consuming app: as long as both apps share
SECRET_KEY and SESSION_COOKIE_DOMAIN, the cookie set by one app's
login_user() is decodable by the other app, and this user_loader will find
the user in the shared users table via the consumer's db.session.
"""

import logging

from flask_login import LoginManager

from shadow_auth._state import get_db
from shadow_auth.models import User

logger = logging.getLogger(__name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id or not user_id.isdigit():
        return None
    return get_db().session.get(User, int(user_id))


@login_manager.unauthorized_handler
def _unauthorized():
    from flask import abort, redirect, request, url_for

    if request.accept_mimetypes.best == "application/json":
        abort(401)
    return redirect(url_for(login_manager.login_view, next=request.path))
