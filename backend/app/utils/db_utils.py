import json
import os

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor

load_dotenv()


def _safe_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": _safe_int(os.getenv("DB_PORT", "3306"), 3306),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "ingredient_recipe_ai"),
    "cursorclass": DictCursor,
}

OWNER_ADMIN_EMAIL = os.getenv("OWNER_ADMIN_EMAIL", "swapnilpanchal935@gmail.com").strip().lower()
ALLOWED_USER_ROLES = {"user", "admin", "super_admin"}
ALLOWED_USER_STATUSES = {"active", "inactive"}


def configure_db_from_app(app_config):
    global OWNER_ADMIN_EMAIL
    DB_CONFIG["host"] = app_config.get("DB_HOST", DB_CONFIG["host"])
    DB_CONFIG["port"] = _safe_int(app_config.get("DB_PORT", DB_CONFIG["port"]), DB_CONFIG["port"])
    DB_CONFIG["user"] = app_config.get("DB_USER", DB_CONFIG["user"])
    DB_CONFIG["password"] = app_config.get("DB_PASSWORD", DB_CONFIG["password"])
    DB_CONFIG["database"] = app_config.get("DB_NAME", DB_CONFIG["database"])
    owner_email = str(app_config.get("OWNER_ADMIN_EMAIL", OWNER_ADMIN_EMAIL)).strip().lower()
    if owner_email:
        OWNER_ADMIN_EMAIL = owner_email


def get_connection():
    try:
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            cursorclass=DB_CONFIG["cursorclass"],
        )
        return connection
    except Exception as exc:
        print(f"[!] Database connection error: {exc}")
        return None


def execute_query(query, params=None):
    connection = get_connection()
    if connection is None:
        return []
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchall()
        return result
    except Exception as exc:
        print(f"[!] Query error: {exc}")
        return []
    finally:
        connection.close()


def execute_commit(query, params=None):
    connection = get_connection()
    if connection is None:
        print("[!] Cannot execute commit - no database connection")
        return False
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
        connection.commit()
        return True
    except Exception as exc:
        print(f"[!] Commit error: {exc}")
        connection.rollback()
        return False
    finally:
        connection.close()


def _table_exists(table_name):
    result = execute_query(
        """
        SELECT 1
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
        LIMIT 1
        """,
        (DB_CONFIG["database"], table_name),
    )
    return bool(result)


def _table_has_column(table_name, column_name):
    result = execute_query(
        """
        SELECT 1
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        LIMIT 1
        """,
        (DB_CONFIG["database"], table_name, column_name),
    )
    return bool(result)


def _index_exists(table_name, index_name):
    result = execute_query(
        """
        SELECT 1
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND INDEX_NAME = %s
        LIMIT 1
        """,
        (DB_CONFIG["database"], table_name, index_name),
    )
    return bool(result)


def _ensure_owner_admin():
    if not OWNER_ADMIN_EMAIL:
        return
    execute_commit(
        """
        UPDATE users
        SET role = 'super_admin',
            status = 'active'
        WHERE LOWER(email) = %s
        """,
        (OWNER_ADMIN_EMAIL,),
    )


def initialize_database():
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(190) UNIQUE,
        password VARCHAR(255),
        role VARCHAR(20) NOT NULL DEFAULT 'user',
        status VARCHAR(20) NOT NULL DEFAULT 'active',
        last_login_at TIMESTAMP NULL DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    recipes_table = """
    CREATE TABLE IF NOT EXISTS saved_recipes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        recipe_name VARCHAR(255),
        ingredients TEXT,
        source_recipe_id INT NULL,
        tried TINYINT(1) NOT NULL DEFAULT 0,
        is_favorite TINYINT(1) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """

    logs_table = """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        event_type VARCHAR(80) NOT NULL,
        event_payload TEXT NULL,
        ip_address VARCHAR(64) NULL,
        user_agent VARCHAR(255) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    detection_history_table = """
    CREATE TABLE IF NOT EXISTS detection_history (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NULL,
        detected_ingredients LONGTEXT NULL,
        typed_ingredients LONGTEXT NULL,
        recommended_recipe_ids LONGTEXT NULL,
        selected_recipe_id INT NULL,
        `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """

    recipe_image_cache_table = """
    CREATE TABLE IF NOT EXISTS recipe_image_cache (
        id INT AUTO_INCREMENT PRIMARY KEY,
        recipe_name VARCHAR(255) NOT NULL UNIQUE,
        recipe_image_url TEXT NULL,
        image_source VARCHAR(40) NULL,
        image_verified TINYINT(1) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """

    users_ok = execute_commit(users_table)
    if users_ok:
        print("[OK] Users table created/verified")
        if not _table_has_column("users", "role"):
            execute_commit("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user'")
        if not _table_has_column("users", "status"):
            execute_commit("ALTER TABLE users ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'active'")
        if not _table_has_column("users", "last_login_at"):
            execute_commit("ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP NULL DEFAULT NULL")
        execute_commit(
            """
            UPDATE users
            SET role = CASE
                WHEN role IN ('user','admin','super_admin') THEN role
                ELSE 'user'
            END
            """
        )
        execute_commit(
            """
            UPDATE users
            SET status = CASE
                WHEN status IN ('active','inactive') THEN status
                ELSE 'active'
            END
            """
        )
        _ensure_owner_admin()
    else:
        print("[!] Users table not initialized (database connection unavailable)")

    recipes_ok = execute_commit(recipes_table)
    if recipes_ok:
        print("[OK] Recipes table created/verified")
        if not _table_has_column("saved_recipes", "source_recipe_id"):
            execute_commit("ALTER TABLE saved_recipes ADD COLUMN source_recipe_id INT NULL")
        if not _table_has_column("saved_recipes", "tried"):
            execute_commit("ALTER TABLE saved_recipes ADD COLUMN tried TINYINT(1) NOT NULL DEFAULT 0")
        if not _table_has_column("saved_recipes", "is_favorite"):
            execute_commit("ALTER TABLE saved_recipes ADD COLUMN is_favorite TINYINT(1) NOT NULL DEFAULT 0")
    else:
        print("[!] Recipes table not initialized (database connection unavailable)")

    logs_ok = execute_commit(logs_table)
    if logs_ok:
        print("[OK] Audit logs table created/verified")
    else:
        print("[!] Audit logs table not initialized (database connection unavailable)")

    history_ok = execute_commit(detection_history_table)
    if history_ok:
        print("[OK] Detection history table created/verified")
        if not _table_has_column("detection_history", "detected_ingredients"):
            execute_commit("ALTER TABLE detection_history ADD COLUMN detected_ingredients LONGTEXT NULL")
        if not _table_has_column("detection_history", "typed_ingredients"):
            execute_commit("ALTER TABLE detection_history ADD COLUMN typed_ingredients LONGTEXT NULL")
        if not _table_has_column("detection_history", "recommended_recipe_ids"):
            execute_commit("ALTER TABLE detection_history ADD COLUMN recommended_recipe_ids LONGTEXT NULL")
        if not _table_has_column("detection_history", "selected_recipe_id"):
            execute_commit("ALTER TABLE detection_history ADD COLUMN selected_recipe_id INT NULL")
        if not _table_has_column("detection_history", "timestamp"):
            execute_commit("ALTER TABLE detection_history ADD COLUMN `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        if not _index_exists("detection_history", "idx_detection_history_user_id"):
            execute_commit("CREATE INDEX idx_detection_history_user_id ON detection_history(user_id)")
        if not _index_exists("detection_history", "idx_detection_history_timestamp"):
            execute_commit("CREATE INDEX idx_detection_history_timestamp ON detection_history(`timestamp`)")
        if not _index_exists("detection_history", "idx_detection_history_selected_recipe"):
            execute_commit(
                "CREATE INDEX idx_detection_history_selected_recipe ON detection_history(selected_recipe_id)"
            )
    else:
        print("[!] Detection history table not initialized (database connection unavailable)")

    image_cache_ok = execute_commit(recipe_image_cache_table)
    if image_cache_ok:
        print("[OK] Recipe image cache table created/verified")
        if not _table_has_column("recipe_image_cache", "recipe_image_url"):
            execute_commit("ALTER TABLE recipe_image_cache ADD COLUMN recipe_image_url TEXT NULL")
        if not _table_has_column("recipe_image_cache", "image_source"):
            execute_commit("ALTER TABLE recipe_image_cache ADD COLUMN image_source VARCHAR(40) NULL")
        if not _table_has_column("recipe_image_cache", "image_verified"):
            execute_commit("ALTER TABLE recipe_image_cache ADD COLUMN image_verified TINYINT(1) NOT NULL DEFAULT 0")
        if not _index_exists("recipe_image_cache", "idx_recipe_image_cache_name"):
            execute_commit("CREATE INDEX idx_recipe_image_cache_name ON recipe_image_cache(recipe_name)")
    else:
        print("[!] Recipe image cache table not initialized (database connection unavailable)")


def init_db(app=None):
    """Initialize the database tables."""
    if app:
        with app.app_context():
            configure_db_from_app(app.config)
            initialize_database()
    else:
        initialize_database()


# User helper functions
def create_user(name, email, password):
    role = "super_admin" if str(email or "").strip().lower() == OWNER_ADMIN_EMAIL else "user"
    return execute_commit(
        "INSERT INTO users (name, email, password, role, status) VALUES (%s, %s, %s, %s, 'active')",
        (name, email, password, role),
    )


def get_user_by_email(email):
    result = execute_query("SELECT * FROM users WHERE email = %s", (email,))
    return result[0] if result else None


def get_user_by_id(user_id):
    result = execute_query("SELECT * FROM users WHERE id = %s", (user_id,))
    return result[0] if result else None


def update_user_last_login(user_id):
    return execute_commit(
        "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = %s",
        (user_id,),
    )


def update_user_password(user_id, password_hash):
    return execute_commit(
        "UPDATE users SET password = %s WHERE id = %s",
        (password_hash, user_id),
    )


def set_user_status(user_id, status):
    if status not in ALLOWED_USER_STATUSES:
        return False
    return execute_commit(
        "UPDATE users SET status = %s WHERE id = %s",
        (status, user_id),
    )


def set_user_role(user_id, role):
    if role not in ALLOWED_USER_ROLES:
        return False
    return execute_commit(
        "UPDATE users SET role = %s WHERE id = %s",
        (role, user_id),
    )


def delete_user_account(user_id):
    return execute_commit("DELETE FROM users WHERE id = %s", (user_id,))


def save_recipe(user_id, recipe_name, ingredients, source_recipe_id=None):
    if _table_has_column("saved_recipes", "source_recipe_id"):
        return execute_commit(
            "INSERT INTO saved_recipes (user_id, recipe_name, ingredients, source_recipe_id) VALUES (%s, %s, %s, %s)",
            (user_id, recipe_name, ingredients, source_recipe_id),
        )
    return execute_commit(
        "INSERT INTO saved_recipes (user_id, recipe_name, ingredients) VALUES (%s, %s, %s)",
        (user_id, recipe_name, ingredients),
    )


def get_user_recipes(user_id, limit=None):
    if limit and int(limit) > 0:
        return execute_query(
            "SELECT * FROM saved_recipes WHERE user_id = %s ORDER BY created_at DESC LIMIT %s",
            (user_id, int(limit)),
        )
    return execute_query(
        "SELECT * FROM saved_recipes WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,),
    )


def get_saved_recipes_count(user_id):
    result = execute_query(
        "SELECT COUNT(*) AS count FROM saved_recipes WHERE user_id = %s",
        (user_id,),
    )
    return result[0]["count"] if result else 0


def get_user_tried_recipes_count(user_id):
    if not _table_has_column("saved_recipes", "tried"):
        return 0
    result = execute_query(
        "SELECT COUNT(*) AS count FROM saved_recipes WHERE user_id = %s AND tried = 1",
        (user_id,),
    )
    return result[0]["count"] if result else 0


def get_user_favorites_count(user_id):
    if not _table_has_column("saved_recipes", "is_favorite"):
        return 0
    result = execute_query(
        "SELECT COUNT(*) AS count FROM saved_recipes WHERE user_id = %s AND is_favorite = 1",
        (user_id,),
    )
    return result[0]["count"] if result else 0


def get_user_favorite_recipes(user_id, limit=None):
    if not _table_has_column("saved_recipes", "is_favorite"):
        return []
    if limit and int(limit) > 0:
        return execute_query(
            "SELECT * FROM saved_recipes WHERE user_id = %s AND is_favorite = 1 ORDER BY created_at DESC LIMIT %s",
            (user_id, int(limit)),
        )
    return execute_query(
        "SELECT * FROM saved_recipes WHERE user_id = %s AND is_favorite = 1 ORDER BY created_at DESC",
        (user_id,),
    )


def log_audit_event(user_id=None, event_type="", event_payload=None, ip_address=None, user_agent=None):
    if not _table_exists("audit_logs"):
        return False
    payload_text = None
    if event_payload is not None:
        try:
            payload_text = json.dumps(event_payload, ensure_ascii=False)
        except Exception:
            payload_text = str(event_payload)
    ip_text = str(ip_address or "")[:64] if ip_address else None
    user_agent_text = str(user_agent or "")[:250] if user_agent else None
    return execute_commit(
        """
        INSERT INTO audit_logs (user_id, event_type, event_payload, ip_address, user_agent)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, event_type, payload_text, ip_text, user_agent_text),
    )


def _safe_json_dumps(value):
    try:
        return json.dumps(value if value is not None else [], ensure_ascii=False)
    except Exception:
        return json.dumps([], ensure_ascii=False)


def log_detection_history(
    user_id=None,
    detected_ingredients=None,
    typed_ingredients=None,
    recommended_recipe_ids=None,
    selected_recipe_id=None,
):
    if not _table_exists("detection_history"):
        return False
    return execute_commit(
        """
        INSERT INTO detection_history (
            user_id,
            detected_ingredients,
            typed_ingredients,
            recommended_recipe_ids,
            selected_recipe_id
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            user_id,
            _safe_json_dumps(detected_ingredients),
            _safe_json_dumps(typed_ingredients),
            _safe_json_dumps(recommended_recipe_ids),
            selected_recipe_id,
        ),
    )


def update_latest_detection_selected_recipe(user_id, selected_recipe_id):
    if not _table_exists("detection_history"):
        return False
    return execute_commit(
        """
        UPDATE detection_history
        SET selected_recipe_id = %s
        WHERE user_id = %s
          AND selected_recipe_id IS NULL
        ORDER BY `timestamp` DESC
        LIMIT 1
        """,
        (selected_recipe_id, user_id),
    )


def get_ingredient_analytics_data(days=30):
    if not _table_exists("detection_history"):
        return {
            "most_detected_ingredients": [],
            "most_selected_recipes": [],
            "ingredient_trends": [],
        }

    rows = execute_query(
        """
        SELECT
            id,
            user_id,
            detected_ingredients,
            typed_ingredients,
            recommended_recipe_ids,
            selected_recipe_id,
            `timestamp`
        FROM detection_history
        WHERE `timestamp` >= (NOW() - INTERVAL %s DAY)
        ORDER BY `timestamp` DESC
        LIMIT 5000
        """,
        (int(days),),
    )

    ingredient_counter = {}
    trend_by_day = {}

    for row in rows:
        timestamp = row.get("timestamp")
        day_key = str(timestamp.date()) if hasattr(timestamp, "date") else str(timestamp)[:10]
        bucket = trend_by_day.setdefault(
            day_key,
            {"date": day_key, "total_detections": 0, "ingredient_counts": {}},
        )
        bucket["total_detections"] += 1

        payload = row.get("detected_ingredients")
        detected_values = []
        if payload:
            try:
                parsed = json.loads(payload)
                if isinstance(parsed, list):
                    detected_values = parsed
            except Exception:
                detected_values = []

        seen_once = set()
        for ingredient in detected_values:
            clean = str(ingredient or "").strip().lower()
            if not clean:
                continue
            ingredient_counter[clean] = ingredient_counter.get(clean, 0) + 1
            if clean not in seen_once:
                bucket["ingredient_counts"][clean] = bucket["ingredient_counts"].get(clean, 0) + 1
                seen_once.add(clean)

    most_detected_ingredients = [
        {"ingredient": ingredient, "count": count}
        for ingredient, count in sorted(
            ingredient_counter.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:20]
    ]

    selected_rows = execute_query(
        """
        SELECT
            selected_recipe_id AS recipe_id,
            COUNT(*) AS count
        FROM detection_history
        WHERE selected_recipe_id IS NOT NULL
          AND `timestamp` >= (NOW() - INTERVAL %s DAY)
        GROUP BY selected_recipe_id
        ORDER BY count DESC
        LIMIT 20
        """,
        (int(days),),
    )
    most_selected_recipes = [
        {"recipe_id": int(row.get("recipe_id")), "count": int(row.get("count") or 0)}
        for row in selected_rows
        if row.get("recipe_id") is not None
    ]

    ingredient_trends = []
    for day_key in sorted(trend_by_day.keys()):
        bucket = trend_by_day[day_key]
        top_ingredients = [
            {"ingredient": ingredient, "count": count}
            for ingredient, count in sorted(
                bucket["ingredient_counts"].items(),
                key=lambda item: item[1],
                reverse=True,
            )[:8]
        ]
        ingredient_trends.append(
            {
                "date": bucket["date"],
                "total_detections": int(bucket["total_detections"]),
                "top_ingredients": top_ingredients,
            }
        )

    return {
        "most_detected_ingredients": most_detected_ingredients,
        "most_selected_recipes": most_selected_recipes,
        "ingredient_trends": ingredient_trends,
    }


def get_all_users_admin(limit=500):
    if not _table_exists("users"):
        return []
    return execute_query(
        """
        SELECT
            u.id,
            u.name,
            u.email,
            u.role,
            u.status,
            u.created_at,
            u.last_login_at,
            COALESCE(sr.saved_count, 0) AS saved_count,
            COALESCE(sr.favorite_count, 0) AS favorite_count,
            COALESCE(sr.tried_count, 0) AS tried_count
        FROM users u
        LEFT JOIN (
            SELECT
                user_id,
                COUNT(*) AS saved_count,
                SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) AS favorite_count,
                SUM(CASE WHEN tried = 1 THEN 1 ELSE 0 END) AS tried_count
            FROM saved_recipes
            GROUP BY user_id
        ) sr ON u.id = sr.user_id
        ORDER BY u.created_at DESC
        LIMIT %s
        """,
        (int(limit),),
    )


def get_cached_recipe_image(recipe_name):
    if not _table_exists("recipe_image_cache"):
        return None
    clean = str(recipe_name or "").strip().lower()
    if not clean:
        return None
    rows = execute_query(
        """
        SELECT recipe_name, recipe_image_url, image_source, image_verified
        FROM recipe_image_cache
        WHERE LOWER(recipe_name) = %s
        LIMIT 1
        """,
        (clean,),
    )
    return rows[0] if rows else None


def upsert_recipe_image_cache(recipe_name, recipe_image_url, image_source, image_verified):
    if not _table_exists("recipe_image_cache"):
        return False
    clean_name = str(recipe_name or "").strip().lower()
    if not clean_name:
        return False
    verified_val = 1 if bool(image_verified) else 0
    return execute_commit(
        """
        INSERT INTO recipe_image_cache (recipe_name, recipe_image_url, image_source, image_verified)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            recipe_image_url = VALUES(recipe_image_url),
            image_source = VALUES(image_source),
            image_verified = VALUES(image_verified),
            updated_at = CURRENT_TIMESTAMP
        """,
        (clean_name, recipe_image_url, image_source, verified_val),
    )


def get_recent_audit_logs(limit=40):
    if not _table_exists("audit_logs"):
        return []
    return execute_query(
        """
        SELECT
            a.id,
            a.user_id,
            a.event_type,
            a.event_payload,
            a.ip_address,
            a.created_at,
            u.name AS user_name,
            u.email AS user_email
        FROM audit_logs a
        LEFT JOIN users u ON u.id = a.user_id
        ORDER BY a.created_at DESC
        LIMIT %s
        """,
        (int(limit),),
    )


def get_admin_overview_data(days=7):
    stats = {
        "total_users": 0,
        "active_users": 0,
        "inactive_users": 0,
        "logins_last_days": 0,
        "total_saved_recipes": 0,
        "detections_last_days": 0,
    }

    total_users = execute_query("SELECT COUNT(*) AS count FROM users")
    if total_users:
        stats["total_users"] = int(total_users[0]["count"])

    active_users = execute_query("SELECT COUNT(*) AS count FROM users WHERE status = 'active'")
    if active_users:
        stats["active_users"] = int(active_users[0]["count"])

    inactive_users = execute_query("SELECT COUNT(*) AS count FROM users WHERE status = 'inactive'")
    if inactive_users:
        stats["inactive_users"] = int(inactive_users[0]["count"])

    login_count = execute_query(
        """
        SELECT COUNT(*) AS count
        FROM audit_logs
        WHERE event_type = 'login_success'
          AND created_at >= (NOW() - INTERVAL %s DAY)
        """,
        (int(days),),
    )
    if login_count:
        stats["logins_last_days"] = int(login_count[0]["count"])

    saved_count = execute_query("SELECT COUNT(*) AS count FROM saved_recipes")
    if saved_count:
        stats["total_saved_recipes"] = int(saved_count[0]["count"])

    detection_count = execute_query(
        """
        SELECT COUNT(*) AS count
        FROM audit_logs
        WHERE event_type = 'detect_success'
          AND created_at >= (NOW() - INTERVAL %s DAY)
        """,
        (int(days),),
    )
    if detection_count:
        stats["detections_last_days"] = int(detection_count[0]["count"])

    top_ingredients = []
    raw_rows = execute_query(
        """
        SELECT event_payload
        FROM audit_logs
        WHERE event_type = 'detect_success'
          AND created_at >= (NOW() - INTERVAL %s DAY)
        ORDER BY created_at DESC
        LIMIT 700
        """,
        (int(days),),
    )
    counters = {}
    for row in raw_rows:
        payload_raw = row.get("event_payload")
        if not payload_raw:
            continue
        try:
            payload = json.loads(payload_raw)
        except Exception:
            continue
        ingredient = str(payload.get("primary_ingredient") or "").strip().lower()
        if not ingredient:
            continue
        counters[ingredient] = counters.get(ingredient, 0) + 1
    for ingredient, count in sorted(counters.items(), key=lambda item: item[1], reverse=True)[:8]:
        top_ingredients.append({"ingredient": ingredient, "count": count})

    return {
        "stats": stats,
        "top_ingredients": top_ingredients,
        "recent_logs": get_recent_audit_logs(limit=30),
    }
