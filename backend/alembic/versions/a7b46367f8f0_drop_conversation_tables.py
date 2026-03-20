"""drop_conversation_tables

Drop messages and conversations tables (discussion engine removed in cockpit pivot).

Revision ID: a7b46367f8f0
Revises: fb17f556ba07
Create Date: 2026-03-20 21:16:11.683147

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a7b46367f8f0'
down_revision: Union[str, Sequence[str], None] = 'fb17f556ba07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('messages')
    op.drop_table('conversations')


def downgrade() -> None:
    # Tables intentionally not recreated - discussion engine permanently removed
    pass
