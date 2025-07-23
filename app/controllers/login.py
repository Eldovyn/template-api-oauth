from ..databases import (
    UserDatabase,
    AccountActiveDatabase,
    BlacklistTokenDatabase,
)
from flask import jsonify
from email_validator import validate_email
import requests
from ..utils import AuthJwt, TokenEmailAccountActive, TokenWebAccountActive, SendEmail
import datetime
from ..config import provider as PROVIDER, web_short_me
import string
import random
from ..serializers import UserSerializer, TokenSerializer
from ..models import AccessTokenModel
from ..tasks import cancle_deleted_account
import traceback


class LoginController:
    def __init__(self):
        self.user_seliazer = UserSerializer()
        self.token_serializer = TokenSerializer()

    async def user_logout(self, user, token):
        if not (
            user_token := await BlacklistTokenDatabase.insert(user.id, token["iat"])
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        return jsonify({"message": "successfully logout"}), 201

    async def user_login(self, provider, token, email, password, timestamp):
        from ..extensions import bcrypt

        token_web = None
        access_token = None

        try:
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
                    return (
                        jsonify({"errors": errors, "message": "validations error"}),
                        400,
                    )
                url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={token}"
                response = requests.get(url)
                resp = response.json()
                try:
                    email = resp["email"]
                except KeyError:
                    return (
                        jsonify(
                            {
                                "errors": {"token": ["IS_INVALID"]},
                                "message": "validations error",
                            }
                        ),
                        400,
                    )
                if not (user_data := await UserDatabase.get("by_email", email=email)):
                    return (
                        jsonify(
                            {
                                "message": "you are not registered",
                            }
                        ),
                        401,
                    )
                if not user_data.is_active:
                    return (
                        jsonify(
                            {
                                "message": "user is not active",
                            }
                        ),
                        401,
                    )
                if not user_data.provider == "google":
                    return (
                        jsonify(
                            {
                                "message": "you are not registered",
                            }
                        ),
                        401,
                    )
                access_token = await AuthJwt.generate_jwt_async(
                    f"{user_data.id}", int(timestamp.timestamp())
                )
                user_me = self.user_seliazer.serialize(user_data)
            else:
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
                if password is None or (
                    isinstance(password, str) and password.strip() == ""
                ):
                    errors.setdefault("password", []).append("IS_REQUIRED")
                else:
                    if not isinstance(password, str):
                        errors.setdefault("password", []).append("MUST_TEXT")
                if errors:
                    return (
                        jsonify(
                            {
                                "errors": errors,
                                "message": "validations error",
                            }
                        ),
                        400,
                    )
                if not (user_data := await UserDatabase.get("by_email", email=email)):
                    return (
                        jsonify(
                            {
                                "message": "invalid email or password",
                            }
                        ),
                        401,
                    )
                if not bcrypt.check_password_hash(user_data.password, password):
                    return (
                        jsonify(
                            {
                                "message": "invalid email or password",
                            }
                        ),
                        401,
                    )
                if not user_data.is_active:
                    expired_at = timestamp + datetime.timedelta(minutes=5)
                    token_web = await TokenWebAccountActive.insert(
                        f"{user_data.id}", int(timestamp.timestamp())
                    )
                    token_email = await TokenEmailAccountActive.insert(
                        f"{user_data.id}", int(timestamp.timestamp())
                    )
                    karakter = string.ascii_uppercase + string.digits
                    otp = "".join(random.choices(karakter, k=6))
                    await AccountActiveDatabase.insert(
                        email,
                        token_web,
                        token_email,
                        otp,
                        int(timestamp.timestamp()),
                        int(expired_at.timestamp()),
                    )
                    SendEmail.send_email(
                        "Verification Your Account",
                        [user_data.email],
                        f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Active</title>
</head>
<body>
    <p>Hello {user_data.email},</p>
    <p>Someone has requested a link to verify your account, and you can do this through the link below.</p>
    <p>your otp is {otp}.</p>
    <p>
        <a href="{web_short_me}/account-active?token={token_email}">
            Click here to activate your account
        </a>
    </p>
    <p>If you didn't request this, please ignore this email.</p>
</body>
</html>
                """,
                    )
                    user_me = self.user_seliazer.serialize(user_data)
                    token_data = self.token_serializer.serialize(
                        token_web, token_email_is_null=True
                    )
                    return (
                        jsonify(
                            {
                                "message": "user not active",
                                "data": user_me,
                                "token": token_data,
                            }
                        ),
                        403,
                    )
                else:
                    await AccountActiveDatabase.delete(
                        "by_user_id", user_id=user_data.id
                    )
                access_token = await AuthJwt.generate_jwt_async(
                    f"{user_data.id}", int(timestamp.timestamp())
                )
                user_me = self.user_seliazer.serialize(user_data)
            token_model = AccessTokenModel(access_token, int(timestamp.timestamp()))
            token_data = self.token_serializer.serialize(token_model)
            if user_data.deleted_id:
                SendEmail.send_email(
                    "Cancle Deleted Account",
                    [user_data.email],
                    f"""<!DOCTYPE html>
<html lang="en">
<head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cancle Deleted Account</title>
</head>
        <body>
            <p>Hello {user_data.first_name} {user_data.last_name},</p>
            <p>your account has been cancled from deleted account.</p>
        </body>
        </html>
                        """,
                )
                cancle_deleted_account(f"{user_data.deleted_id}")
                await UserDatabase.update(
                    "cancle_deleted_id_by_user_id", user_id=f"{user_data.id}"
                )
            return (
                jsonify(
                    {
                        "message": "user login successfully",
                        "data": user_me,
                        "token": token_data,
                    }
                ),
                201,
            )
        except Exception:
            traceback.print_exc()
            return jsonify({"message": "invalid request"}), 400
