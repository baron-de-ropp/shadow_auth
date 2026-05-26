# shadow_auth

Shared Flask-Login authentication package for the Flask apps under
`thearcanelibrary.com` — currently Shadowleague and Shadowdarklings. Provides
SQLAlchemy `User` and `UserRole` models pointing at the existing
`public.users` / `public.user_roles` tables, a preconfigured `LoginManager`,
and an auth blueprint with login/logout routes.

This is a **private** package. Install via SSH:

```
pip install "shadow_auth @ git+ssh://git@github.com/baron-de-ropp/shadow_auth.git@v0.1.0"
```

## Cross-subdomain SSO

Both consuming apps share `FLASK_SECRET_KEY` and set
`SESSION_COOKIE_DOMAIN=.thearcanelibrary.com`. Flask-Login's signed session
cookie is then valid on every subdomain, and each app's `user_loader` (the
same one in this package) looks up the user from the shared `users` table by
the integer `user_id` stored in the cookie. Logging in on one subdomain
authenticates the user on every subdomain automatically.

## Usage

```python
from flask import Flask
from shadow_auth import init_app, auth_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]
app.config["SESSION_COOKIE_DOMAIN"] = ".thearcanelibrary.com"

init_app(app)
app.register_blueprint(auth_bp)
```

`init_app` wires Flask-SQLAlchemy, Flask-Login, the `user_loader`, and asserts
that the cross-subdomain session-cookie config is set sanely. Pass the
consuming app's `SQLAlchemy()` instance explicitly via `init_app(app,
db=db)` if the app already has its own — otherwise shadow_auth creates one.

## Schema requirements

`shadow_auth` expects the `users` table to have these columns (in addition to
the legacy columns already defined by Shadowleague):

- `firebase_uid TEXT UNIQUE` (nullable) — only set on rows migrated from
  Firebase Auth; lets us re-key migrated characters back to their owners.
- `username TEXT UNIQUE` (nullable) — chosen at first login for migrated
  users; required for newly registered accounts.

Apply via the consuming app's Alembic migrations. The two migration files in
[src/shadow_auth/migrations/](src/shadow_auth/migrations/) are idempotent
templates — copy them into your `migrations/versions/` directory and adjust
`down_revision` to chain into your existing migration history.

## Versions

- **v0.1.0** — Models + LoginManager + `init_app` + `/login`/`/logout` routes
  + schema migration templates. The minimum to prove cross-subdomain SSO.
- **v0.2.0** _(planned)_ — `/register`, `/forgot-password`,
  `/reset-password/<token>`, `/confirm-email/<token>`, `@role_required`
  decorator, username force-pick UX.
- **v0.3.0** _(planned)_ — Real SMTP email sending.

## Development

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

ruff check . && ruff format --check .
pytest
```
