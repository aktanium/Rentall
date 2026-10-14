"""add bookings no_overlap exclusion constraint

Active bookings (pending, confirmed, paid) of the same listing must not overlap in time.
Ranges are half-open [start_at, end_at), so back-to-back bookings are allowed.

Revision ID: c3d1f0a2b7e4
Revises: baf267ecf6e1
Create Date: 2026-10-14 05:40:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'c3d1f0a2b7e4'
down_revision = 'baf267ecf6e1'
branch_labels = None
depends_on = None


def upgrade():
    # btree_gist lets a GiST index combine "=" on an integer with "&&" on a range.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE bookings
        ADD CONSTRAINT no_overlap
        EXCLUDE USING gist (
            listing_id WITH =,
            tstzrange(start_at, end_at) WITH &&
        )
        WHERE (status IN ('pending', 'confirmed', 'paid'))
        """
    )


def downgrade():
    op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS no_overlap")
    # The btree_gist extension is left installed: other objects may depend on it.
