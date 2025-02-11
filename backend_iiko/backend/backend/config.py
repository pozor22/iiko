from dotenv import load_dotenv
import os

load_dotenv()

# Database
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

# Redis
REDIS_URL = os.environ.get("REDIS_URL")

# Email
EMAIL_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EM_PORT = os.environ.get("EMAIL_PORT")
EM_HOST = os.environ.get("EMAIL_HOST")

# Django
FRONTEND_URL = os.environ.get("FRONTEND_URL")
DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
