"""initial_schema

Revision ID: 59730166bb2b
Revises:
Create Date: 2026-03-09 14:10:21.581825

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "59730166bb2b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=190), nullable=False, unique=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="user"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "saved_recipes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recipe_name", sa.String(length=255), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=True),
        sa.Column("source_recipe_id", sa.Integer(), nullable=True),
        sa.Column("tried", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "source_recipe_id", name="uq_saved_recipe_per_user"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("event_payload", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "detection_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("detected_ingredients", sa.Text(), nullable=True),
        sa.Column("typed_ingredients", sa.Text(), nullable=True),
        sa.Column("recommended_recipe_ids", sa.Text(), nullable=True),
        sa.Column("selected_recipe_id", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
    )

    op.create_table(
        "recipe_image_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("recipe_name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("recipe_image_url", sa.Text(), nullable=True),
        sa.Column("image_source", sa.String(length=40), nullable=True),
        sa.Column("image_verified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        ),
    )

    op.create_index("idx_users_role_status", "users", ["role", "status"], unique=False)
    op.create_index("idx_users_last_login", "users", ["last_login_at"], unique=False)
    op.create_index("idx_saved_recipes_user_id", "saved_recipes", ["user_id"], unique=False)
    op.create_index("idx_saved_recipes_created_at", "saved_recipes", ["created_at"], unique=False)
    op.create_index("idx_saved_recipes_source_recipe_id", "saved_recipes", ["source_recipe_id"], unique=False)
    op.create_index("idx_saved_recipes_user_favorite", "saved_recipes", ["user_id", "is_favorite"], unique=False)
    op.create_index("idx_saved_recipes_user_tried", "saved_recipes", ["user_id", "tried"], unique=False)
    op.create_index("idx_audit_logs_event_type", "audit_logs", ["event_type"], unique=False)
    op.create_index("idx_audit_logs_created_at", "audit_logs", ["created_at"], unique=False)
    op.create_index("idx_audit_logs_user_id", "audit_logs", ["user_id"], unique=False)
    op.create_index("idx_detection_history_user_id", "detection_history", ["user_id"], unique=False)
    op.create_index("idx_detection_history_timestamp", "detection_history", ["timestamp"], unique=False)
    op.create_index("idx_detection_history_selected_recipe", "detection_history", ["selected_recipe_id"], unique=False)
    op.create_index("idx_recipe_image_cache_name", "recipe_image_cache", ["recipe_name"], unique=False)


def downgrade():
    op.drop_index("idx_recipe_image_cache_name", table_name="recipe_image_cache")
    op.drop_index("idx_detection_history_selected_recipe", table_name="detection_history")
    op.drop_index("idx_detection_history_timestamp", table_name="detection_history")
    op.drop_index("idx_detection_history_user_id", table_name="detection_history")
    op.drop_index("idx_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("idx_audit_logs_created_at", table_name="audit_logs")
    op.drop_index("idx_audit_logs_event_type", table_name="audit_logs")
    op.drop_index("idx_saved_recipes_user_tried", table_name="saved_recipes")
    op.drop_index("idx_saved_recipes_user_favorite", table_name="saved_recipes")
    op.drop_index("idx_saved_recipes_source_recipe_id", table_name="saved_recipes")
    op.drop_index("idx_saved_recipes_created_at", table_name="saved_recipes")
    op.drop_index("idx_saved_recipes_user_id", table_name="saved_recipes")
    op.drop_index("idx_users_last_login", table_name="users")
    op.drop_index("idx_users_role_status", table_name="users")

    op.drop_table("recipe_image_cache")
    op.drop_table("detection_history")
    op.drop_table("audit_logs")
    op.drop_table("saved_recipes")
    op.drop_table("users")
