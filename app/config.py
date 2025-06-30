from .configs import (
    database_mongodb,
    database_mongodb_url,
    celery_broker_url,
    celery_result_backend,
    smtp_email,
    smtp_password,
    smtp_host,
    smtp_port,
    celery_url,
)


class Config:
    CELERY = {
        "broker_url": celery_broker_url,
        "result_backend": celery_result_backend,
        "task_ignore_result": True,
    }

    MONGODB_SETTINGS = {
        "db": database_mongodb,
        "host": database_mongodb_url,
        "connect": False,
    }

    MAIL_SERVER = smtp_host
    MAIL_PORT = smtp_port
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = smtp_email
    MAIL_PASSWORD = smtp_password
    MAIL_DEFAULT_SENDER = smtp_email

    CORS_SUPPORTS_CREDENTIALS = True
    CELERY_URL = celery_url
