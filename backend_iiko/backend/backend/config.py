from dotenv import load_dotenv
import os

load_dotenv()

# Database
DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASS = os.environ.get("POSTGRES_PASSWORD")

# Redis
REDIS_URL = os.environ.get("REDIS_URL")

# Email
EMAIL_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EM_PORT = os.environ.get("EMAIL_PORT")
EM_HOST = os.environ.get("EMAIL_HOST")
