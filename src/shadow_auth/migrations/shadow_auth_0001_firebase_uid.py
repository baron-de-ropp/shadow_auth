"""shadow_auth: add firebase_uid column to users

Adds a nullable, unique `firebase_uid TEXT` column to public.users. Used to
re-key migrated characters from their original Firebase Auth UID back to the
new integer user_id during the Firestore → Postgres data migration. Stays
populated for forensics after the migration completes.

Idempotent: re-running is a no-op.

When copying this into a consuming app's migrations/versions/ directory,
update `down_revision` to chain into the app's existing migration history.

Revision ID: shadow_auth_0001_firebase_uid
Revises: <CHANGE ME TO YOUR APP'S CURRENT HEAD>
"""

from alembic import op

# revision identifiers, used by Alembic
revision = "shadow_auth_0001_firebase_uid"
down_revision = None  # TODO consumer: set this to your app's current head
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS firebase_uid TEXT")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS users_firebase_uid_key ON public.users (firebase_uid)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS users_firebase_uid_key")
    op.execute("ALTER TABLE public.users DROP COLUMN IF EXISTS firebase_uid")
