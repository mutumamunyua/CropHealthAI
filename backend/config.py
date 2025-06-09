from flask_mail import Mail
import os
import json
from dotenv import load_dotenv
from pymongo import MongoClient, GEOSPHERE


# Load environment variables from .env file (if exists)
load_dotenv()

class Config:
    """Configuration class for environment variables, MongoDB, and email settings."""

    # Base URL logic
    ENV = os.getenv("FLASK_ENV", "development")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5001")  # 👈 Used in email links
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

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
    

    # Security + AI Keys
    SECRET_KEY = os.environ.get("SECRET_KEY", "cfa1d0aa7ac3ff07b0c1d51292170ad8")
    HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Added
    
    # Firebase Admin SDK
    FIREBASE_ADMIN_CREDENTIAL = os.getenv(
        "FIREBASE_ADMIN_CREDENTIAL",
        "/Users/philipmunyua/Documents/CropHealthAI/backend/secrets/firebase-adminsdk.json"
)
    FIREBASE_ADMIN_CREDENTIAL = os.getenv("FIREBASE_ADMIN_CREDENTIAL")
    

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
    predictions_collection = db.get_collection("predictions")
    agrovets_collection = db.get_collection("agrovets")
    extension_workers_collection = db.get_collection("extension_workers")
    geolocation_collection = db.get_collection("geolocation")

    # Ensure geospatial indexes are created
    if agrovets_collection is not None:
        agrovets_collection.create_index([("location", GEOSPHERE)])
    if extension_workers_collection is not None:
        extension_workers_collection.create_index([("location", GEOSPHERE)])
    if geolocation_collection is not None:  # Added
        geolocation_collection.create_index([("location", GEOSPHERE)])
else:
    users_collection = None  # Prevent errors if the DB is unavailable
    predictions_collection = None
    agrovets_collection = None
    extension_workers_collection = None
    geolocation_collection   = None