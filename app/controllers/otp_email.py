from ..databases import OtpEmailDatabase
from ..utils import SendEmail
from flask import jsonify
import string
import datetime
import random


class OtpEmailController:
    def __init__(self):
        pass

    async def otp_email(self, user, timestamp):
        karakter = string.ascii_uppercase + string.digits
        expired_at = timestamp + datetime.timedelta(minutes=5)
        otp = "".join(random.choices(karakter, k=6))
        if not (
            data_otp := await OtpEmailDatabase.insert(
                user.id, otp, int(timestamp.timestamp()), int(expired_at.timestamp())
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
        SendEmail.send_email_otp(user, otp)
        return (
            jsonify(
                {
                    "message": "successfully send otp",
                    "data": {
                        "id": f"{data_otp.id}",
                        "created_at": data_otp.created_at,
                        "expired_at": data_otp.expired_at,
                    },
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "is_active": user.is_active,
                        "avatar": user.avatar,
                        "provider": user.provider,
                    },
                }
            ),
            201,
        )
