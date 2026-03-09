from app.extensions import bcrypt
from app.utils.db_utils import create_user, get_user_by_email, update_user_password


class User:

    @staticmethod
    def _is_bcrypt_hash(password_value):
        value = str(password_value or "")
        return value.startswith("$2a$") or value.startswith("$2b$") or value.startswith("$2y$")

    @staticmethod
    def register(name, email, password):
        """
        Register new user
        """

        existing_user = get_user_by_email(email)

        if existing_user:
            return False, "User already exists"

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        create_user(name, email, password_hash)

        return True, "User created successfully"


    @staticmethod
    def login(email, password):
        """
        Authenticate user
        """

        user = get_user_by_email(email)

        if not user:
            return False, "User not found"

        if str(user.get("status", "active")).lower() != "active":
            return False, "Account is inactive. Please contact administrator."

        stored_password = user.get("password")
        is_valid_password = False

        if User._is_bcrypt_hash(stored_password):
            try:
                is_valid_password = bcrypt.check_password_hash(stored_password, password)
            except Exception:
                is_valid_password = False
        else:
            # Backward compatibility for existing plaintext rows.
            is_valid_password = str(stored_password or "") == str(password or "")
            if is_valid_password:
                try:
                    upgraded_hash = bcrypt.generate_password_hash(password).decode("utf-8")
                    update_user_password(user.get("id"), upgraded_hash)
                    user["password"] = upgraded_hash
                except Exception:
                    pass

        if not is_valid_password:
            return False, "Invalid password"

        return True, user
