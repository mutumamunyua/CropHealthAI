from flask_mail import Mail
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file (if exists)
load_dotenv()

class Config:
    """Configuration class for environment variables, MongoDB, and email settings."""

    UPLOAD_FOLDER = os.path.join(os.getcwd(), "images")  # Stores uploaded images
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/crophealthai")

    # Email Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").strip().lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)  # Use MAIL_USERNAME if sender is missing
    SECRET_KEY = os.environ.get("SECRET_KEY", "cfa1d0aa7ac3ff07b0c1d51292170ad8")
# Initialize Flask-Mail
mail = Mail()

# Initialize MongoDB
try:
    client = MongoClient(Config.MONGO_URI)
    db = client.get_database()  # Ensure the connection is established
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"⚠️ MongoDB Connection Error: {e}")
    db = None  # Set db to None if connection fails

# Ensure collections exist before use
if db is not None:
    users_collection = db.get_collection("users")  # Define users collection
    db["users"].create_index("email", unique=True)  # Ensure email uniqueness
else:
    users_collection = None  # Prevent errors if the DB is unavailable