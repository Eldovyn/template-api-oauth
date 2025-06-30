from .register import register_router
from .login import login_router
from .account_active import account_active_router
from .reset_password import reset_password_router
from .me import me_router
from .profile import profile_router
from .otp_email import otp_email_router


def register_blueprints(app):
    app.register_blueprint(register_router)
    app.register_blueprint(login_router)
    app.register_blueprint(account_active_router)
    app.register_blueprint(reset_password_router)
    app.register_blueprint(me_router)
    app.register_blueprint(profile_router)
    app.register_blueprint(otp_email_router)
