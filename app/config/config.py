from dotenv import load_dotenv
import os

load_dotenv()

database_mongodb = os.getenv("DATABASE_MONGODB")
database_mongodb_url = os.getenv("DATABASE_MONGODB_URL")
salt_account_active_email = os.getenv("SALT_ACCOUNT_ACTIVE_EMAIL")
secret_key_account_active_email = os.getenv("SECRET_KEY_ACCOUNT_ACTIVE_EMAIL")
salt_account_active_web = os.getenv("SALT_ACCOUNT_ACTIVE_WEB")
secret_key_account_active_web = os.getenv("SECRET_KEY_ACCOUNT_ACTIVE_WEB")
salt_reset_password_email = os.getenv("SALT_RESET_PASSWORD_EMAIL")
secret_key_reset_password_email = os.getenv("SECRET_KEY_RESET_PASSWORD_EMAIL")
salt_reset_password_web = os.getenv("SALT_RESET_PASSWORD_WEB")
secret_key_reset_password_web = os.getenv("SECRET_KEY_RESET_PASSWORD_WEB")
api_key_google_trends = os.getenv("API_KEY_GOOGLE_TRENDS")
smtp_host = os.getenv("SMTP_HOST")
smtp_port = os.getenv("SMTP_PORT")
smtp_email = os.getenv("SMTP_EMAIL")
smtp_password = os.getenv("SMTP_PASSWORD")
celery_broker_url = os.getenv("CELERY_BROKER_URL")
celery_result_backend = os.getenv("CELERY_RESULT_BACKEND")
web_short_me = os.getenv("WEB_SHORT_ME")
provider = os.getenv("PROVIDER")
