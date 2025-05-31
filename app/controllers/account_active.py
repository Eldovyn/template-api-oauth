from ..databases import UserDatabase, AccountActiveDatabase
from flask import jsonify
from email_validator import validate_email
from ..utils import TokenWebAccountActive, TokenEmailAccountActive, SendEmail
import datetime
import string
import random


class AccountActiveController:
    @staticmethod
    async def get_user_account_active_verification(token, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if not token or (isinstance(token, str) and token.isspace()):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
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
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": {
                        "id": user_data.id,
                        "token_web": user_data.token_web,
                        "created_at": user_data.created_at,
                        "updated_at": user_data.updated_at,
                        "expired_at": user_data.expired_at,
                    },
                    "user": {
                        "id": user_data.user.id,
                        "username": user_data.user.username,
                        "email": user_data.user.email,
                        "created_at": user_data.user.created_at,
                        "updated_at": user_data.user.updated_at,
                        "is_active": user_data.user.is_active,
                        "provider": user_data.user.provider,
                    },
                }
            ),
            200,
        )

    @staticmethod
    async def user_account_active_verification(token, otp, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if not token or (isinstance(token, str) and token.isspace()):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if not otp or (isinstance(otp, str) and otp.isspace()):
            errors.setdefault("otp", []).append("IS_REQUIRED")
        else:
            if not isinstance(otp, str):
                errors.setdefault("otp", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        token_web = await TokenEmailAccountActive.get(token)
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
            user_id=token_web["user_id"],
        )
        return (
            jsonify(
                {
                    "message": "successfully verify user account",
                    "data": {
                        "id": user_data.id,
                        "token_web": user_data.token_web,
                        "created_at": user_data.created_at,
                        "updated_at": user_data.updated_at,
                        "expired_at": user_data.expired_at,
                    },
                    "user": {
                        "id": user_data.user.id,
                        "username": user_data.user.username,
                        "created_at": user_data.user.created_at,
                        "updated_at": user_data.user.updated_at,
                        "is_active": user_data.user.is_active,
                        "provider": user_data.user.provider,
                        "email": user_data.user.email,
                    },
                }
            ),
            201,
        )

    @staticmethod
    async def user_account_active_information(token, timestamp):
        created_at = int(timestamp.timestamp())
        errors = {}
        if not token or (isinstance(token, str) and token.isspace()):
            errors.setdefault("token", []).append("IS_REQUIRED")
        else:
            if not isinstance(token, str):
                errors.setdefault("token", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "invalid data"}), 400
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
        return (
            jsonify(
                {
                    "message": "successfully get account active information",
                    "data": {
                        "id": user_data.id,
                        "token_web": user_data.token_web,
                        "created_at": user_data.created_at,
                        "updated_at": user_data.updated_at,
                        "expired_at": user_data.expired_at,
                    },
                    "user": {
                        "id": user_data.user.id,
                        "email": user_data.user.email,
                        "username": user_data.user.username,
                        "created_at": user_data.user.created_at,
                        "updated_at": user_data.user.updated_at,
                        "is_active": user_data.user.is_active,
                        "provider": user_data.user.provider,
                    },
                }
            ),
            200,
        )

    @staticmethod
    async def send_account_active_email(email, timestamp):
        errors = {}
        if not email or (isinstance(email, str) and email.isspace()):
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
        return (
            jsonify(
                {
                    "message": "successfully send account active email",
                    "data": {
                        "id": account_active_data.id,
                        "token_web": account_active_data.account_active.token_web,
                        "created_at": account_active_data.account_active.created_at,
                        "updated_at": account_active_data.account_active.updated_at,
                        "expired_at": account_active_data.account_active.expired_at,
                    },
                    "user": {
                        "id": account_active_data.account_active.user.id,
                        "username": account_active_data.account_active.user.username,
                        "created_at": account_active_data.account_active.user.created_at,
                        "updated_at": account_active_data.account_active.user.updated_at,
                        "is_active": account_active_data.account_active.user.is_active,
                        "provider": account_active_data.account_active.user.provider,
                    },
                }
            ),
            201,
        )
