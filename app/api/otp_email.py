from flask import Blueprint, request
from ..controllers import OtpEmailController
from ..utils import jwt_required

otp_email_router = Blueprint("otp_email_router", __name__)


@otp_email_router.post("/short.me/otp/email")
async def user_login():
    user = request.user
    timestamp = request.timestamp
    return await OtpEmailController.otp_email(user, timestamp)
