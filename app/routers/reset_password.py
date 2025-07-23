from flask import Blueprint, request
from ..controllers import ResetPasswordController

reset_password_router = Blueprint("reset_password_router", __name__)
reset_password_controller = ResetPasswordController()


@reset_password_router.post("/sludgify/auth/reset-password/request")
async def send_reset_password_email():
    data = request.json
    timestamp = request.timestamp
    email = data.get("email", "")
    return await reset_password_controller.send_reset_password_email(email, timestamp)


@reset_password_router.get("/sludgify/auth/reset-password/status/<string:token>")
async def user_reset_password_information(token):
    timestamp = request.timestamp
    return await reset_password_controller.user_reset_password_information(
        token, timestamp
    )


@reset_password_router.get(
    "/sludgify/auth/reset-password/password-changed/<string:token>"
)
async def get_user_reset_password_verification(token):
    timestamp = request.timestamp
    return await reset_password_controller.get_user_reset_password_verification(
        token, timestamp
    )


@reset_password_router.patch(
    "/sludgify/auth/reset-password/password-changed/<string:token>"
)
async def user_reset_password_verification(token):
    timestamp = request.timestamp
    json = request.json
    confirm_password = json.get("confirm_password", "")
    new_password = json.get("new_password", "")
    return await reset_password_controller.user_reset_password_verification(
        token, new_password, confirm_password, timestamp
    )
