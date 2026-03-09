from app.extensions import db


class UserTable(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(190), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    status = db.Column(db.String(20), nullable=False, default="active")
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)


class SavedRecipeTable(db.Model):
    __tablename__ = "saved_recipes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "source_recipe_id", name="uq_saved_recipe_per_user"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_name = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.Text, nullable=True)
    source_recipe_id = db.Column(db.Integer, nullable=True)
    tried = db.Column(db.Boolean, nullable=False, default=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)


class AuditLogTable(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    event_type = db.Column(db.String(80), nullable=False)
    event_payload = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)


class DetectionHistoryTable(db.Model):
    __tablename__ = "detection_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    detected_ingredients = db.Column(db.Text, nullable=True)
    typed_ingredients = db.Column(db.Text, nullable=True)
    recommended_recipe_ids = db.Column(db.Text, nullable=True)
    selected_recipe_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)


class RecipeImageCacheTable(db.Model):
    __tablename__ = "recipe_image_cache"

    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(255), unique=True, nullable=False)
    recipe_image_url = db.Column(db.Text, nullable=True)
    image_source = db.Column(db.String(40), nullable=True)
    image_verified = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp(),
        nullable=False,
    )
