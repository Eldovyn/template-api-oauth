from flask import request, jsonify
from ..utils import AuthJwt
from ..models import UserModel, BlacklistTokenModel


def jwt_required_request():
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.lower().startswith("bearer "):
        return (
            jsonify(
                {
                    "message": "invalid authorization header",
                    "errors": {"authorization": ["IS_INVALID"]},
                }
            ),
            401,
        )

    token = auth_header.split()[1]
    payload = AuthJwt.verify_token(token)

    if payload is None:
        return (
            jsonify(
                {
                    "message": "invalid or expired token",
                    "errors": {"token": ["IS_INVALID"]},
                }
            ),
            401,
        )

    user_id = payload.get("sub")
    iat = payload.get("iat")

    if not user_id:
        return (
            jsonify(
                {
                    "message": "invalid or expired token",
                    "errors": {"token": ["IS_INVALID"]},
                }
            ),
            401,
        )

    if not (user_data := UserModel.objects(id=user_id).first()):
        return (
            jsonify(
                {
                    "message": "invalid or expired token",
                    "errors": {"token": ["IS_INVALID"]},
                }
            ),
            401,
        )

    if not iat > user_data.updated_at:
        return (
            jsonify(
                {
                    "message": "invalid or expired token",
                    "errors": {"token": ["IS_INVALID"]},
                }
            ),
            401,
        )

    if BlacklistTokenModel.objects(created_at=iat).first():
        return (
            jsonify(
                {
                    "message": "invalid or expired token",
                    "errors": {"token": ["IS_INVALID"]},
                }
            ),
            401,
        )

    if not user_data.is_active:
        return (
            jsonify(
                {
                    "message": "user is not active",
                    "errors": {"user": ["NOT_ACTIVE"]},
                }
            ),
            401,
        )

    request.user = user_data
    request.token = payload
