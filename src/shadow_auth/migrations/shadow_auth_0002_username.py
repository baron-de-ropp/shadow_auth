"""shadow_auth: add username column to users

Adds a nullable, unique `username TEXT` column to public.users. Existing
users have NULL here; on next login they're prompted to pick a username
(v0.2.0). New registrations require a username from the start.

Idempotent: re-running is a no-op.

When copying this into a consuming app's migrations/versions/ directory,
keep `down_revision = "shadow_auth_0001_firebase_uid"` so the two
shadow_auth migrations stay in their canonical order.

Revision ID: shadow_auth_0002_username
Revises: shadow_auth_0001_firebase_uid
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "shadow_auth_0002_username"
down_revision = "shadow_auth_0001_firebase_uid"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS username TEXT")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS users_username_key ON public.users (username)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS users_username_key")
    op.execute("ALTER TABLE public.users DROP COLUMN IF EXISTS username")
