from flask import Flask, request, jsonify
import os
from .database import db
from .celery_app import celery_init_app
from .mail import mail
import datetime
from .models import AccountActiveModel, ResetPasswordModel, OtpEmailModel
from celery.schedules import crontab
from .config import (
    database_mongodb,
    database_mongodb_url,
    celery_broker_url,
    celery_result_backend,
    smtp_email,
    smtp_password,
    smtp_host,
    smtp_port,
)
from werkzeug.exceptions import BadRequest
from .bcrypt import bcrypt


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    private_key_path = os.path.join(BASE_DIR, "keys", "private.pem")
    public_key_path = os.path.join(BASE_DIR, "keys", "public.pem")

    app.config.from_mapping(
        CELERY={
            "broker_url": celery_broker_url,
            "result_backend": celery_result_backend,
            "task_ignore_result": True,
        },
        MONGODB_SETTINGS={
            "db": database_mongodb,
            "host": database_mongodb_url,
            "connect": False,
        },
        MAIL_SERVER=smtp_host,
        MAIL_PORT=smtp_port,
        MAIL_USE_TLS=True,
        MAIL_USE_SSL=False,
        MAIL_USERNAME=smtp_email,
        MAIL_PASSWORD=smtp_password,
        MAIL_DEFAULT_SENDER=smtp_email,
    )

    global PRIVATE_KEY, PUBLIC_KEY
    with open(private_key_path, "rb") as f:
        PRIVATE_KEY = f.read()

    with open(public_key_path, "rb") as f:
        PUBLIC_KEY = f.read()

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
    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)

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
                    print(f"success delete token {account_active_data.user.email}")
        if data_reset_password := ResetPasswordModel.objects.all():
            for reset_password_data in data_reset_password:
                if (
                    reset_password_data.expired_at <= expired_at
                    or reset_password_data.user.is_active
                ):
                    reset_password_data.delete()
                    print(f"success delete token {reset_password_data.user.email}")
        if data_otp_email := OtpEmailModel.objects.all():
            for otp_email_data in data_otp_email:
                if otp_email_data.expired_at <= expired_at:
                    otp_email_data.delete()
                    print(f"success delete token {otp_email_data.user.email}")
        return "clear data"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "update_data_every_5_minutes",
            "schedule": crontab(minute="*/5"),
        },
    }

    with app.app_context():
        from .utils import jwt_required_request
        from .api.register import register_router
        from .api.login import login_router
        from .api.account_active import account_active_router
        from .api.reset_password import reset_password_router
        from .api.me import me_router
        from .api.profile import profile_router
        from .api.otp_email import otp_email_router

        app.register_blueprint(login_router)
        app.register_blueprint(register_router)
        app.register_blueprint(account_active_router)
        app.register_blueprint(reset_password_router)
        app.register_blueprint(me_router)
        app.register_blueprint(profile_router)
        app.register_blueprint(otp_email_router)

        app.before_request_funcs = {"me_router": [jwt_required_request]}

    @app.after_request
    async def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.before_request
    async def before_request():
        request.timestamp = datetime.datetime.now(datetime.timezone.utc)

    @app.errorhandler(BadRequest)
    async def handle_bad_request(e):
        return (
            jsonify(
                {
                    "message": str(e.description),
                }
            ),
            400,
        )

    return app
