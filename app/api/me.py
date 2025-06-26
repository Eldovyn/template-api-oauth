from flask import Blueprint, request
from ..controllers import ProfileController
from ..utils import jwt_required

me_router = Blueprint("me_router", __name__)
me_controller = ProfileController()


@me_router.get("/short.me/@me")
@jwt_required()
async def user_login():
    user = request.user
    return await me_controller.user_me(user)
