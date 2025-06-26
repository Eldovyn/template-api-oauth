from ..models import AccountActiveModel, ResetPasswordModel, AccessTokenModel
from .interfaces import SerializerInterface
from typing import Union


class TokenSerializer(SerializerInterface):
    def serialize(
        self,
        token_data: Union[AccountActiveModel, ResetPasswordModel, AccessTokenModel],
        id_is_null: bool = False,
        access_token_is_null: bool = False,
        token_web_is_null: bool = False,
        token_email_is_null: bool = False,
        created_at_is_null: bool = False,
        updated_at_is_null: bool = False,
        expired_at_is_null: bool = False,
    ) -> dict:
        data = {}
        if isinstance(token_data, (AccountActiveModel, ResetPasswordModel)):
            if not id_is_null:
                data["id"] = str(token_data.id) if token_data.id else None
            if not token_web_is_null:
                data["token_web"] = token_data.token_web
            if not token_email_is_null:
                data["token_email"] = token_data.token_email
            if not created_at_is_null:
                data["created_at"] = token_data.created_at
            if not updated_at_is_null:
                data["updated_at"] = token_data.updated_at
            if not expired_at_is_null:
                data["expired_at"] = token_data.expired_at
        if isinstance(token_data, AccessTokenModel):
            if not access_token_is_null:
                data["access_token"] = token_data.access_token
            if not created_at_is_null:
                data["created_at"] = token_data.created_at
        return data
