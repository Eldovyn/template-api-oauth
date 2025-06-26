from ..databases import UserDatabase, AccountActiveDatabase
from flask import jsonify, url_for
from email_validator import validate_email
import requests
import re
from ..utils import TokenEmailAccountActive, TokenWebAccountActive, SendEmail, AuthJwt
import datetime
from ..config import provider as PROVIDER
import random
import string
from ..serializers import UserSerializer, TokenSerializer
from ..models import AccessTokenModel


class RegisterController:
    def __init__(self):
        self.user_serializer = UserSerializer()
        self.token_serializer = TokenSerializer()

    async def user_register(
        self, provider, token, username, email, password, confirm_password, timestamp
    ):
        from ..bcrypt import bcrypt

        access_token = None
        token_web = None

        try:
            created_at = int(timestamp.timestamp())
            errors = {}
            if provider is None or (
                isinstance(provider, str) and provider.strip() == ""
            ):
                errors.setdefault("provider", []).append("IS_REQUIRED")
            else:
                if not isinstance(provider, str):
                    errors.setdefault("provider", []).append("MUST_TEXT")
                if provider not in PROVIDER.split(", "):
                    errors.setdefault("provider", []).append("IS_INVALID")
            if provider == "google":
                if token is None or (isinstance(token, str) and token.strip() == ""):
                    errors.setdefault("token", []).append("IS_REQUIRED")
                else:
                    if not isinstance(token, str):
                        errors.setdefault("token", []).append("MUST_TEXT")
                if errors:
                    return jsonify({"errors": errors, "message": "invalid data"}), 400
                url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
                response = requests.get(url)
                resp = response.json()
                try:
                    username = resp["name"]
                    email = resp["email"]
                    avatar = resp["picture"]
                except KeyError:
                    return (
                        jsonify(
                            {
                                "errors": {"token": ["IS_INVALID"]},
                                "message": "invalid data",
                            }
                        ),
                        400,
                    )
                if user_data := await UserDatabase.get("by_email", email=email):
                    return (
                        jsonify(
                            {
                                "errors": {"user": ["USER_ALREADY_EXISTS"]},
                                "message": "the user already exists",
                            }
                        ),
                        409,
                    )
                user_data = await UserDatabase.insert(
                    provider, f"{avatar}", username, email, None, created_at
                )
                access_token = await AuthJwt.generate_jwt(user_data.id, created_at)
                token_model = AccessTokenModel(access_token, int(timestamp.timestamp()))
                token_serializer = self.token_serializer.serialize(token_model)
                user_serializer = self.user_serializer.serialize(user_data)
            else:
                if username is None or (
                    isinstance(username, str) and username.strip() == ""
                ):
                    errors.setdefault("username", []).append("IS_REQUIRED")
                else:
                    if not isinstance(username, str):
                        errors.setdefault("username", []).append("MUST_TEXT")
                    if isinstance(username, str) and len(username) < 5:
                        errors.setdefault("username", []).append("TOO_SHORT")
                    if isinstance(username, str) and len(username) > 15:
                        errors.setdefault("username", []).append("TOO_LONG")
                if email is None or (isinstance(email, str) and email.strip() == ""):
                    errors.setdefault("email", []).append("IS_REQUIRED")
                else:
                    if not isinstance(email, str):
                        errors.setdefault("email", []).append("MUST_TEXT")
                    if isinstance(email, str) and len(email) < 6:
                        errors.setdefault("email", []).append("TOO_SHORT")
                    if isinstance(email, str) and len(email) > 50:
                        errors.setdefault("email", []).append("TOO_LONG")
                    try:
                        valid = validate_email(email)
                        email = valid.email
                    except:
                        errors.setdefault("email", []).append("IS_INVALID")
                if password is None or (
                    isinstance(password, str) and password.strip() == ""
                ):
                    errors.setdefault("password", []).append("IS_REQUIRED")
                else:
                    if not isinstance(password, str):
                        errors.setdefault("password", []).append("MUST_TEXT")
                if not confirm_password or (
                    isinstance(confirm_password, str) and confirm_password.isspace()
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
                        errors.setdefault("password_security", []).append(
                            "NO_LOWERCASE"
                        )
                    if not re.search(r"[0-9]", password):
                        errors.setdefault("password_security", []).append("NO_NUMBER")
                    if not re.search(
                        r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password
                    ):
                        errors.setdefault("password_security", []).append("NO_SYMBOL")
                    if not re.search(r"[A-Za-z]", password):
                        errors.setdefault("password_security", []).append("NO_LETTER")
                if errors:
                    return jsonify({"errors": errors, "message": "invalid data"}), 400
                result_password = bcrypt.generate_password_hash(password).decode(
                    "utf-8"
                )
                avatar = url_for(
                    "static", filename="images/default-avatar.webp", _external=True
                )
                if user_data := await UserDatabase.get("by_email", email=email):
                    return (
                        jsonify(
                            {
                                "errors": {"user": ["IS_ALREADY"]},
                                "message": "the user already exists",
                            }
                        ),
                        409,
                    )
            if provider != "google":
                user_data = await UserDatabase.insert(
                    provider, f"{avatar}", username, email, result_password, created_at
                )
                expired_at = timestamp + datetime.timedelta(minutes=5)
                token_web = await TokenWebAccountActive.insert(
                    f"{user_data.id}", int(timestamp.timestamp())
                )
                token_email = await TokenEmailAccountActive.insert(
                    f"{user_data.id}", int(timestamp.timestamp())
                )
                karakter = string.ascii_uppercase + string.digits
                otp = "".join(random.choices(karakter, k=6))
                token_account_active = await AccountActiveDatabase.insert(
                    email,
                    token_web,
                    token_email,
                    otp,
                    int(timestamp.timestamp()),
                    int(expired_at.timestamp()),
                )
                SendEmail.send_email_verification(user_data, token_email, otp)
                token_serializer = self.token_serializer.serialize(token_account_active)
                user_serializer = self.user_serializer.serialize(user_data)
            return (
                jsonify(
                    {
                        "message": "user registered successfully",
                        "data": user_serializer,
                        "token": token_serializer,
                    }
                ),
                201,
            )
        except Exception as e:
            return jsonify({"message": f"{e}"}), 400
