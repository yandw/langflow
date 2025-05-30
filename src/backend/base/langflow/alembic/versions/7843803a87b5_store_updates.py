"""Store updates

Revision ID: 7843803a87b5
Revises: eb5866d51fd2
Create Date: 2023-10-18 23:08:57.744906

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "7843803a87b5"
down_revision: Union[str, None] = "eb5866d51fd2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    inspector = sa.inspect(conn)  # type: ignore
    flow_columns = [column["name"] for column in inspector.get_columns("flow")]
    user_columns = [column["name"] for column in inspector.get_columns("user")]
    try:
        if "is_component" not in flow_columns:
            with op.batch_alter_table("flow", schema=None) as batch_op:
                batch_op.add_column(sa.Column("is_component", sa.Boolean(), nullable=True))
    except Exception:
        pass
    try:
        if "store_api_key" not in user_columns:
            with op.batch_alter_table("user", schema=None) as batch_op:
                batch_op.add_column(sa.Column("store_api_key", sqlmodel.AutoString(), nullable=True))
    except Exception:
        pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        with op.batch_alter_table("user", schema=None) as batch_op:
            batch_op.drop_column("store_api_key")

        with op.batch_alter_table("flow", schema=None) as batch_op:
            batch_op.drop_column("is_component")
    except Exception as e:
        print(e)
        pass
    # ### end Alembic commands ###
