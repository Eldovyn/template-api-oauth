from .database import Database
from ..models import AccountActiveModel, UserModel, OtpAccountActiveModel


class AccountActiveDatabase(Database):
    @staticmethod
    async def insert(email, token_web, token_email, otp, created_at, expired_at):
        if data_user := UserModel.objects(email=email.lower()).first():
            if data_account_active := AccountActiveModel.objects(
                user=data_user
            ).first():
                if data_otp := OtpAccountActiveModel.objects(
                    account_active=data_account_active
                ).first():
                    data_otp.otp = otp
                    data_otp.updated_at = int(created_at)
                    data_otp.save()
                data_account_active.token_web = token_web
                data_account_active.token_email = token_email
                data_account_active.updated_at = int(created_at)
                data_account_active.expired_at = int(expired_at)
                data_account_active.save()
                return data_otp
            account_active_data = AccountActiveModel(
                user=data_user,
                token_web=token_web,
                token_email=token_email,
                created_at=int(created_at),
                updated_at=int(created_at),
                expired_at=int(expired_at),
            )
            account_active_data.save()
            data_otp = OtpAccountActiveModel(
                account_active=account_active_data,
                otp=otp,
                created_at=int(created_at),
                updated_at=int(created_at),
            )
            data_otp.save()
            return data_otp

    @staticmethod
    async def get(category, **kwargs):
        token = kwargs.get("token")
        created_at = kwargs.get("created_at")
        otp = kwargs.get("otp")
        if category == "by_token_web":
            if data_account_active := AccountActiveModel.objects(
                token_web=token
            ).first():
                if data_account_active.expired_at > int(created_at):
                    return data_account_active
                else:
                    data_account_active.user.save()
                    data_account_active.delete()
        if category == "by_token_email":
            if data_account_active := AccountActiveModel.objects(
                token_email=token
            ).first():
                if data_account_active.expired_at > int(created_at):
                    return data_account_active
                else:
                    data_account_active.user.save()
                    data_account_active.delete()
        if category == "by_token_email_otp":
            if data_account_active := AccountActiveModel.objects(
                token_email=token
            ).first():
                if data_otp := OtpAccountActiveModel.objects(
                    account_active=data_account_active, otp=otp
                ).first():
                    if data_account_active.expired_at > int(created_at):
                        return data_account_active
                    else:
                        data_account_active.user.save()
                        data_account_active.delete()

    @staticmethod
    async def delete(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "user_active_by_token_email":
            if user_data := UserModel.objects(id=user_id).first():
                if data_account_active := AccountActiveModel.objects(
                    user=user_data
                ).first():
                    user_data.is_active = True
                    user_data.save()
                    data_account_active.delete()
                    return data_account_active
        if category == "by_user_id":
            if user_data := UserModel.objects(id=user_id).first():
                if data_account_active := AccountActiveModel.objects(
                    user=user_data
                ).first():
                    data_account_active.delete()
                    return data_account_active

    @staticmethod
    async def update(category, **kwargs):
        pass
