from flask import Blueprint, request
from ..controllers import ProfileController

me_router = Blueprint("me_router", __name__)


@me_router.get("/short.me/@me")
async def user_login():
    user = request.user
    return await ProfileController.user_me(user)
