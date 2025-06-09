from ..databases import UserDatabase
from flask import jsonify
from ..utils import SendEmail
import re
from email_validator import validate_email


class ProfileController:
    @staticmethod
    async def update_email(user, email, otp, timestamp):
        errors = {}
        if email is None or (isinstance(email, str) and email.strip() == ""):
            errors.setdefault("email", []).append("IS_REQUIRED")
        else:
            if not isinstance(email, str):
                errors.setdefault("email", []).append("MUST_TEXT")
            try:
                valid = validate_email(email)
                email = valid.email
            except:
                errors.setdefault("email", []).append("IS_INVALID")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        if not (
            user_data := await UserDatabase.update(
                "email",
                user_id=user.id,
                created_at=int(timestamp.timestamp()),
                email=email,
                otp=otp,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid otp",
                        "errors": {"token": ["IS_INVALID"]},
                    }
                ),
                409,
            )
        SendEmail.send_email_update_email(user_data.user, user.email)
        return (
            jsonify(
                {
                    "message": "success update email",
                    "data": {
                        "id": user_data.user.id,
                        "email": user_data.user.email,
                        "username": user_data.user.username,
                        "created_at": user_data.user.created_at,
                        "updated_at": user_data.user.updated_at,
                        "is_active": user_data.user.is_active,
                    },
                }
            ),
            201,
        )

    @staticmethod
    async def update_password(user, password, confirm_password, timestamp):
        from ..bcrypt import bcrypt

        errors = {}
        if password is None or (isinstance(password, str) and password.strip() == ""):
            errors.setdefault("password", []).append("IS_REQUIRED")
        else:
            if not isinstance(password, str):
                errors.setdefault("password", []).append("MUST_TEXT")
        if confirm_password is None or (
            isinstance(confirm_password, str) and confirm_password.strip() == ""
        ):
            errors.setdefault("confirm_password", []).append("IS_REQUIRED")
        else:
            if not isinstance(confirm_password, str):
                errors.setdefault("confirm_password", []).append("MUST_TEXT")
        if password != confirm_password and (
            password or (isinstance(password, str) and not password.isspace())
        ):
            errors.setdefault("password_match", []).append("IS_MISMATCH")
        if isinstance(password, str) and password == confirm_password:
            if len(password) > 64:
                errors.setdefault("password_security", []).append("TOO_LONG")
            if len(password) < 8:
                errors.setdefault("password_security", []).append("TOO_SHORT")
            if not re.search(r"[A-Z]", password):
                errors.setdefault("password_security", []).append("NO_CAPITAL")
            if not re.search(r"[a-z]", password):
                errors.setdefault("password_security", []).append("NO_LOWERCASE")
            if not re.search(r"[0-9]", password):
                errors.setdefault("password_security", []).append("NO_NUMBER")
            if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
                errors.setdefault("password_security", []).append("NO_SYMBOL")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        result_password = bcrypt.generate_password_hash(password).decode("utf-8")
        if not (
            user_data := await UserDatabase.update(
                "password",
                user_id=user.id,
                created_at=int(timestamp.timestamp()),
                password=result_password,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                        "errors": {"token": ["IS_INVALID"]},
                    }
                ),
                401,
            )
        SendEmail.send_email_update_password(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update password",
                    "data": {
                        "id": user_data.id,
                        "email": user_data.email,
                        "username": user_data.username,
                        "created_at": user_data.created_at,
                        "updated_at": user_data.updated_at,
                        "is_active": user_data.is_active,
                    },
                }
            ),
            201,
        )

    @staticmethod
    async def update_username(user, username):
        errors = {}
        if username is None or (isinstance(username, str) and username.strip() == ""):
            errors.setdefault("username", []).append("IS_REQUIRED")
        else:
            if not isinstance(username, str):
                errors.setdefault("username", []).append("MUST_TEXT")
            if isinstance(username, str) and len(username) < 5:
                errors.setdefault("username", []).append("TOO_SHORT")
            if isinstance(username, str) and len(username) > 15:
                errors.setdefault("username", []).append("TOO_LONG")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        if not (
            user_data := await UserDatabase.update(
                "username",
                user_id=user.id,
                username=username,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                        "errors": {"token": ["IS_INVALID"]},
                    }
                ),
                401,
            )
        SendEmail.send_email_update_username(user_data, username)
        return (
            jsonify(
                {
                    "message": "successfully update username",
                    "data": {
                        "id": user_data.id,
                        "email": user_data.email,
                        "username": user_data.username,
                        "created_at": user_data.created_at,
                        "updated_at": user_data.updated_at,
                        "is_active": user_data.is_active,
                    },
                }
            ),
            201,
        )

    @staticmethod
    async def user_me(user):
        return (
            jsonify(
                {
                    "message": "successfully get user",
                    "data": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "is_active": user.is_active,
                    },
                }
            ),
            200,
        )
