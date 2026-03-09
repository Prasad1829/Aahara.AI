from app.models.user import User


class AuthService:

    @staticmethod
    def register_user(name, email, password):
        """
        Register new user
        """

        if not name or not email or not password:
            return {
                "success": False,
                "message": "All fields required"
            }

        success, result = User.register(name, email, password)

        if success:
            return {
                "success": True,
                "message": "Registration successful"
            }

        return {
            "success": False,
            "message": result
        }


    @staticmethod
    def login_user(email, password):
        """
        Login user
        """

        if not email or not password:
            return {
                "success": False,
                "message": "Email and password required"
            }

        success, result = User.login(email, password)

        if not success:
            return {
                "success": False,
                "message": result
            }

        user = result

        return {
            "success": True,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user.get("role", "user"),
                "status": user.get("status", "active"),
                "created_at": user.get("created_at"),
            }
        }
