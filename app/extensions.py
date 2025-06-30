from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from .configs import celery_url
from .utils import limiter_key

db = MongoEngine()
mail = Mail()
bcrypt = Bcrypt()

limiter = Limiter(
    key_func=limiter_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=celery_url,
)
