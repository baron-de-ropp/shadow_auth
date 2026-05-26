"""Auth blueprint — /login and /logout for v0.1.0.

v0.2.0 adds /register, /forgot-password, /reset-password/<token>,
/confirm-email/<token>, and a force-pick-username flow. Kept narrow here so
the cross-subdomain SSO smoke test ships first.

The login identifier field accepts either email or username — if the input
contains '@' we look up by email, otherwise by username. Username login
won't do anything useful until the username column is populated (Phase 7
migration or v0.2.0 first-login picker), but the form already accepts it
so the UX doesn't have to change later.
"""

import logging

import flask_login as fl
from flask import Blueprint, redirect, render_template, request
from sqlalchemy import select
from werkzeug.security import check_password_hash

from shadow_auth._state import get_db
from shadow_auth.models import User

logger = logging.getLogger(__name__)

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
)


def _redirect_after_login() -> str:
    next_url = request.args.get("next") or request.form.get("next")
    if next_url and next_url.startswith("/"):
        return next_url
    return "/"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if fl.current_user.is_authenticated and request.method == "GET":
        return redirect(_redirect_after_login())

    if request.method == "GET":
        return render_template("shadow_auth/login.html", error=None)

    identifier = (request.form.get("identifier") or "").strip()
    password = request.form.get("password") or ""

    if not identifier or not password:
        return (
            render_template(
                "shadow_auth/login.html",
                error="Username/email and password are required.",
            ),
            400,
        )

    db = get_db()
    if "@" in identifier:
        user = db.session.execute(select(User).where(User.email == identifier)).scalar_one_or_none()
    else:
        user = db.session.execute(
            select(User).where(User.username == identifier)
        ).scalar_one_or_none()

    if not user or not check_password_hash(user.password_hash, password):
        logger.info("Failed login attempt for identifier=%r", identifier)
        return (
            render_template("shadow_auth/login.html", error="Invalid credentials."),
            401,
        )

    if not user.is_active:
        return (
            render_template(
                "shadow_auth/login.html",
                error=("This account is not yet active. Check your email for a confirmation link."),
            ),
            403,
        )

    fl.login_user(user)
    logger.info("User %s logged in", user.user_id)
    return redirect(_redirect_after_login())


@auth_bp.route("/logout")
def logout():
    if fl.current_user.is_authenticated:
        logger.info("User %s logged out", fl.current_user.user_id)
    fl.logout_user()
    return redirect("/")
