"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

revision = 'head'
down_revision = None


from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}
    op.add_column('product', sa.Column('image_filename', sa.String(length=255), nullable=True))
    op.add_column('product', sa.Column('description', sa.String(length=255), nullable=True))


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
    op.drop_column('product', 'image_filename')
    op.drop_column('product', 'description')
