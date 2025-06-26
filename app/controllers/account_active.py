from ..databases import UserDatabase, AccountActiveDatabase
from flask import jsonify
from email_validator import validate_email
from ..utils import TokenWebAccountActive, TokenEmailAccountActive, SendEmail
import datetime
import string
import random
from ..serializers import UserSerializer, TokenSerializer


class AccountActiveController:
    def __init__(self):
        self.token_serializer = TokenSerializer()
        self.user_serializer = UserSerializer()

    async def get_user_account_active_verification(self, token, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if token is None or (isinstance(token, str) and token.strip() == ""):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        token_email = await TokenEmailAccountActive.get(token)
        if not token_email:
            return (
                jsonify(
                    {
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"token": ["IS_INVALID"]},
                        "message": "token invalid",
                    }
                ),
                404,
            )
        user_serializer = self.user_serializer.serialize(user_data.user)
        token_serializer = self.token_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": token_serializer,
                    "user": user_serializer,
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
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        token_email = await TokenEmailAccountActive.get(token)
        if not token_email:
            return (
                jsonify(
                    {
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"otp": ["IS_INVALID"]},
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
        token_serializer = self.token_serializer.serialize(
            user_data, token_email_is_null=True
        )
        user_serializer = self.user_serializer.serialize(user_data.user)
        return (
            jsonify(
                {
                    "message": "successfully verify user account",
                    "data": token_serializer,
                    "user": user_serializer,
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
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        token_web = await TokenWebAccountActive.get(token)
        if not token_web:
            return (
                jsonify(
                    {
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"token": ["IS_INVALID"]},
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
                        "errors": {"token": ["IS_INVALID"]},
                        "message": "token invalid",
                    }
                ),
                404,
            )
        token_serializer = self.token_serializer.serialize(
            user_data, token_email_is_null=True
        )
        user_serializer = self.user_serializer.serialize(user_data.user)
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": token_serializer,
                    "user": user_serializer,
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
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        if not (user_data := await UserDatabase.get("by_email", email=email)):
            return (
                jsonify(
                    {"errors": {"user": ["NOT_FOUND"]}, "message": "email not found"}
                ),
                404,
            )
        if user_data.provider != "auth_internal":
            return (
                jsonify(
                    {
                        "errors": {"user": ["NOT_FOUND"]},
                        "message": "email not found",
                    }
                ),
                404,
            )
        if user_data.is_active:
            return (
                jsonify(
                    {
                        "errors": {"user": ["IS_ACTIVE"]},
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
        SendEmail.send_email_verification(user_data, token_email, otp)
        token_serializer = self.token_serializer.serialize(
            account_active_data.account_active, token_email_is_null=True
        )
        user_serializer = self.user_serializer.serialize(account_active_data.user)
        return (
            jsonify(
                {
                    "message": "successfully send account active email",
                    "data": token_serializer,
                    "user": user_serializer,
                }
            ),
            201,
        )
