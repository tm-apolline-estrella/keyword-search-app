"""add_rm_tables

Revision ID: 7244b1fec49f
Revises: f855013dd732
Create Date: 2024-08-30 16:13:10.124858

"""

# Import standard library modules
from typing import Sequence, Union

# Import third-party library modules
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# Import local modules
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7244b1fec49f"
down_revision: Union[str, None] = "f855013dd732"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "Conversation",
        sa.Column("id", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False),
        sa.Column(
            "title", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "userId", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "lastMessageDate",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "createdAt",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("updatedAt", mssql.DATETIME2(), autoincrement=False, nullable=False),
        sa.Column("deletedAt", mssql.DATETIME2(), autoincrement=False, nullable=True),
        sa.Column("pinnedAt", mssql.DATETIME2(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["userId"], ["User.id"], name="Conversation_userId_fkey", onupdate="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="Conversation_pkey"),
    )

    op.create_table(
        "Message",
        sa.Column("id", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False),
        sa.Column(
            "conversationId",
            sa.NVARCHAR(length=1000),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "is_bot",
            mssql.BIT(),
            server_default=sa.text("((0))"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("text", sa.NVARCHAR(), autoincrement=False, nullable=False),
        sa.Column("token_count", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("rating", mssql.BIT(), autoincrement=False, nullable=True),
        sa.Column("ratingData", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("ratingText", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "createdAt",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("deletedAt", mssql.DATETIME2(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["conversationId"],
            ["Conversation.id"],
            name="Message_conversationId_fkey",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="Message_pkey"),
    )

    op.create_table(
        "MessageSource",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(always=False, start=1, increment=1),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "messageId", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "link", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "filename", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column("chunks", sa.NVARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "dateIngested", mssql.DATETIME2(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "dateCreated",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("dateDeleted", mssql.DATETIME2(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["messageId"],
            ["Message.id"],
            name="MessageSource_messageId_fkey",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="MessageSource_pkey"),
    )

    op.create_table(
        "MessageSuggestion",
        sa.Column("id", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False),
        sa.Column("suggestion", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "createdAt",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "messageId", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["messageId"],
            ["Message.id"],
            name="MessageSuggestion_messageId_fkey",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="MessageSuggestion_pkey"),
    )

    op.create_table(
        "RewriteResponse",
        sa.Column("id", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False),
        sa.Column(
            "messageId", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column(
            "instruction", sa.NVARCHAR(length=1000), autoincrement=False, nullable=False
        ),
        sa.Column("rewriteText", sa.NVARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "createdAt",
            mssql.DATETIME2(),
            server_default=sa.text("(getdate())"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["messageId"],
            ["Message.id"],
            name="RewriteResponse_messageId_fkey",
            onupdate="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="RewriteResponse_pkey"),
    )


def downgrade() -> None:
    op.drop_constraint("Conversation_userId_fkey", "Conversation", type_="foreignkey")
    op.drop_constraint("Message_conversationId_fkey", "Message", type_="foreignkey")
    op.drop_constraint(
        "MessageSource_messageId_fkey", "MessageSource", type_="foreignkey"
    )
    op.drop_constraint(
        "MessageSuggestion_messageId_fkey", "MessageSuggestion", type_="foreignkey"
    )
    op.drop_constraint(
        "RewriteResponse_messageId_fkey", "RewriteResponse", type_="foreignkey"
    )
    op.drop_table("Conversation")
    op.drop_table("Message")
    op.drop_table("MessageSource")
    op.drop_table("MessageSuggestion")
    op.drop_table("RewriteResponse")
