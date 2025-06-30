from flask import Flask
import os
from .database import db
from .mail import mail
from .config import Config
from .bcrypt import bcrypt
from .extensions import limiter
from .middlewares import register_middlewares
from .error_handlers import register_error_handlers
from .routers import register_blueprints
from .celery_app import celery_init_app
import datetime
from celery.schedules import crontab
from .models import AccountActiveModel, ResetPasswordModel, OtpEmailModel


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    private_key_path = os.path.join(BASE_DIR, "keys", "private.pem")
    public_key_path = os.path.join(BASE_DIR, "keys", "public.pem")

    app.config.from_object(Config)

    with open(private_key_path, "rb") as f:
        app.config["PRIVATE_KEY"] = f.read()

    with open(public_key_path, "rb") as f:
        app.config["PUBLIC_KEY"] = f.read()

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    global celery_app
    celery_app = celery_init_app(app)
    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)

    @celery_app.task(name="update_data_every_5_minutes")
    def update_data_every_5_minutes():
        expired_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        if data_account_active := AccountActiveModel.objects.all():
            for account_active_data in data_account_active:
                if (
                    account_active_data.expired_at <= expired_at
                    or account_active_data.user.is_active
                ):
                    account_active_data.delete()
                    print(
                        f"success delete token account active {account_active_data.user.email}"
                    )
        if data_reset_password := ResetPasswordModel.objects.all():
            for reset_password_data in data_reset_password:
                if (
                    reset_password_data.expired_at <= expired_at
                    or reset_password_data.user.is_active
                ):
                    reset_password_data.delete()
                    print(
                        f"success delete token reset password {reset_password_data.user.email}"
                    )
        if data_otp_email := OtpEmailModel.objects.all():
            for otp_email_data in data_otp_email:
                if otp_email_data.expired_at <= expired_at:
                    otp_email_data.delete()
                    print(f"success delete token otp email {otp_email_data.user.email}")
        return "clear data"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "update_data_every_5_minutes",
            "schedule": crontab(minute="*/5"),
        },
    }

    register_blueprints(app)
    register_middlewares(app)
    register_error_handlers(app)

    return app
