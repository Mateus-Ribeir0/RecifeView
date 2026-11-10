"""Tira a confirmação de e-mail do cadastro de cidadão: a conta já nasce pronta para entrar.

Os códigos de confirmação que sobraram vencem em 15 minutos e não servem para mais nada.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ESQUEMA = "app"


def upgrade() -> None:
    op.execute(f"DELETE FROM {ESQUEMA}.codigo_de_conta WHERE finalidade = 'CONFIRMAR_EMAIL'")
    op.drop_column("usuario", "email_confirmado_em", schema=ESQUEMA)


def downgrade() -> None:
    op.add_column(
        "usuario", sa.Column("email_confirmado_em", sa.DateTime(timezone=True)), schema=ESQUEMA
    )
    op.execute(f"UPDATE {ESQUEMA}.usuario SET email_confirmado_em = criado_em")
