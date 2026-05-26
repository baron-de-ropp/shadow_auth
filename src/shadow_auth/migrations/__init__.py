"""Migration templates for the shadow_auth schema requirements.

These are reference files. Each consuming Flask app should copy them into its
own `migrations/versions/` directory and adjust `down_revision` to chain into
the app's existing Alembic history. Once chained, run `flask db upgrade`.

All operations use IF NOT EXISTS / IF EXISTS — running these against a
database that already has the column is a no-op, which means it's safe for
both Shadowleague and Shadowdarklings to keep these in their own histories
even though they share one database.
"""
