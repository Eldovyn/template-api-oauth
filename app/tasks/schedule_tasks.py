import datetime
from ..models import AccountActiveModel, ResetPasswordModel, OtpEmailModel
from celery.schedules import crontab


def register_tasks(celery_app):
    @celery_app.task(name="update_data_every_5_minutes")
    def update_data_every_5_minutes():
        expired_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        for model, name in [
            (AccountActiveModel, "account active"),
            (ResetPasswordModel, "reset password"),
            (OtpEmailModel, "otp email"),
        ]:
            for data in model.objects.all():
                if getattr(data, "expired_at", 0) <= expired_at or getattr(
                    data.user, "is_active", False
                ):
                    data.delete()
                    print(f"success delete token {name} {data.user.email}")

        return "clear data"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "update_data_every_5_minutes",
            "schedule": crontab(minute="*/5"),
        },
    }
