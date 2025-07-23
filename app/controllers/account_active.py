from ..databases import UserDatabase, AccountActiveDatabase
from flask import jsonify
from email_validator import validate_email
from ..utils import TokenWebAccountActive, TokenEmailAccountActive, SendEmail
import datetime
import string
import random
from ..serializers import UserSerializer, TokenSerializer
from ..config import web_short_me


class AccountActiveController:
    def __init__(self):
        self.user_seliazer = UserSerializer()
        self.token_serializer = TokenSerializer()

    async def get_user_account_active_verification(self, token, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if token is None or (isinstance(token, str) and token.strip() == ""):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        token_email = await TokenEmailAccountActive.get(token)
        if not token_email:
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_token := await AccountActiveDatabase.get(
                "by_token_email", token=token, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_data := await AccountActiveDatabase.get(
                "by_token_email", token=token, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        user_me = self.user_seliazer.serialize(user_data.user)
        token_data = self.token_serializer.serialize(user_token)
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": token_data,
                    "user": user_me,
                }
            ),
            200,
        )

    async def user_account_active_verification(self, token, otp, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if token is None or (isinstance(token, str) and token.strip() == ""):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if otp is None or (isinstance(otp, str) and otp.strip() == ""):
            errors.setdefault("otp", []).append("IS_REQUIRED")
        else:
            if not isinstance(otp, str):
                errors.setdefault("otp", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        token_email = await TokenEmailAccountActive.get(token)
        if not token_email:
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_token := await AccountActiveDatabase.get(
                "by_token_email", token=token, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_data := await AccountActiveDatabase.get(
                "by_token_email_otp", token=token, otp=otp, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "you have entered an invalid OTP",
                    }
                ),
                404,
            )
        await AccountActiveDatabase.delete(
            "user_active_by_token_email",
            token=user_data.token_email,
            user_id=token_email["user_id"],
        )
        user_me = self.user_seliazer.serialize(user_data.user)
        token_data = self.token_serializer.serialize(user_token)
        return (
            jsonify(
                {
                    "message": "successfully verify user account",
                    "data": token_data,
                    "user": user_me,
                }
            ),
            201,
        )

    async def user_account_active_information(self, token, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if token is None or (isinstance(token, str) and token.strip() == ""):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        token_web = await TokenWebAccountActive.get(token)
        if not token_web:
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_token := await AccountActiveDatabase.get(
                "by_token_web", token=token, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        if not (
            user_data := await AccountActiveDatabase.get(
                "by_token_web", token=token, created_at=created_at
            )
        ):
            return (
                jsonify(
                    {
                        "message": "token invalid",
                    }
                ),
                404,
            )
        user_me = self.user_seliazer.serialize(user_data.user)
        token_data = self.token_serializer.serialize(
            user_token, token_email_is_null=True
        )
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": token_data,
                    "user": user_me,
                }
            ),
            200,
        )

    async def send_account_active_email(self, email, timestamp):
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
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (user_data := await UserDatabase.get("by_email", email=email)):
            return (
                jsonify({"message": "email not found"}),
                404,
            )
        if user_data.provider != "auth_internal":
            return (
                jsonify(
                    {
                        "message": "email not found",
                    }
                ),
                404,
            )
        if user_data.is_active:
            return (
                jsonify(
                    {
                        "message": "your account is active",
                    }
                ),
                409,
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
        account_active_data = await AccountActiveDatabase.insert(
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
        user_me = self.user_seliazer.serialize(account_active_data.account_active.user)
        token_data = self.token_serializer.serialize(
            account_active_data.account_active, token_email_is_null=True
        )
        return (
            jsonify(
                {
                    "message": "successfully send account active email",
                    "data": token_data,
                    "user": user_me,
                }
            ),
            201,
        )
