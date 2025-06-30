from flask import Flask
from .celery_app import celery_init_app


def create_app(test_config=None):
    import os
    from .config import Config

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

    from .extensions import db, mail, bcrypt, limiter

    bcrypt.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    from .tasks import register_tasks

    register_tasks(celery_app)

    from .routers import register_blueprints
    from .error_handlers import register_error_handlers
    from .middlewares import register_middlewares

    register_blueprints(app)
    register_error_handlers(app)
    register_middlewares(app)

    return app
