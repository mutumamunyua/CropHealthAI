from flask import Blueprint, request, jsonify, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import uuid
import jwt
import os
from datetime import datetime, timedelta
from config import users_collection, mail, Config, agrovets_collection, extension_workers_collection, geolocation_collection
from pymongo import GEOSPHERE
import logging
from flask_cors import CORS
import random
import string
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import json
from config import Config  # ✅ Add this line

auth_bp = Blueprint("auth", __name__)
CORS(auth_bp)

# Ensure email is uniquely indexed
users_collection.create_index("email", unique=True)

# Ensure geospatial indexes are created in agrovets and extension_workers collections
if agrovets_collection is not None:
    agrovets_collection.create_index([("location", GEOSPHERE)])

if extension_workers_collection is not None:
    extension_workers_collection.create_index([("location", GEOSPHERE)])

if geolocation_collection is not None:
    geolocation_collection.create_index([("location", GEOSPHERE)])

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    first_name = data.get("first_name")  # Added
    last_name = data.get("last_name")    # Added
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not first_name or not last_name or not username or not email or not password:  # Modified
        return jsonify({"error": "Missing fields"}), 400

    # Check if email already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    # Hash password explicitly
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Modified

    # Generate verification token with expiry
    verification_token = str(uuid.uuid4())
    token_expiry = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours

    # Store user in DB (unverified)
    users_collection.insert_one({
        "first_name": first_name,  # Added
        "last_name": last_name,    # Added
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "is_verified": False,
        "verification_token": verification_token,
        "token_expiry": token_expiry
    })

    # Try to dynamically generate absolute URL; fallback to BASE_URL
    try:
        verification_link = url_for("auth.verify_email", token=verification_token, _external=True)
    except:
        verification_link = f"{Config.BASE_URL}/auth/verify/{verification_token}"
    send_verification_email(email, verification_link)

    return jsonify({"message": "User registered. Check email to verify account."}), 201

def send_verification_email(email, link):
    try:
        msg = Message("Verify Your Email", sender=Config.MAIL_DEFAULT_SENDER, recipients=[email])
        msg.body = f"Click the link to verify your email: {link}"
        mail.send(msg)
        logging.info(f"✅ Verification email sent to {email}")
        return {"success": True, "message": "Verification email sent!"}
    except Exception as e:
        logging.error(f"❌ Email sending failed for {email}: {e}")
        return {"success": False, "error": str(e)}

@auth_bp.route("/login", methods=["POST"])
def login():
    # Extract JSON data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract email and password immediately
    email = data.get("email")
    password = data.get("password")

    # Check that both email and password are provided
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find the user in the database
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Verify the password using the hashed version stored in the DB
    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Ensure the user is verified
    if not user.get("is_verified", False):
        return jsonify({"error": "Email not verified. Please check your inbox."}), 403

    # Generate a JWT token with the required claims. Note the 'sub' claim is added.
    token = jwt.encode(
        {
            "email": email,
            "sub": user.get("first_name", ""),  
            "exp": datetime.utcnow() + timedelta(hours=24)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({
        "message": "Login successful", 
        "token": token,
        "first_name": user.get("first_name", "")
        }), 200

@auth_bp.route("/verify/<token>", methods=["GET"])
def verify_email(token):
    user = users_collection.find_one({"verification_token": token})

    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    # Check if token is expired
    if user.get("token_expiry") and datetime.utcnow() > user["token_expiry"]:
        return jsonify({"error": "Verification token expired. Register again."}), 400

    users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"is_verified": True}, "$unset": {"verification_token": "", "token_expiry": ""}}
    )
    return jsonify({"message": "Email verified. You can now log in."}), 200

@auth_bp.route("/test-email", methods=["GET"])
def test_email():
    """Sends a test email to verify Flask-Mail setup."""
    test_recipient = "mutumamunyua@gmail.com"  # Change this to your email
    msg = Message("Test Email from CropHealthAI", sender=mail.default_sender, recipients=[test_recipient])
    msg.body = "Hello! This is a test email to confirm Flask-Mail is working."
    
    try:
        mail.send(msg)
        return jsonify({"message": "Test email sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_bp.route("/request-reset", methods=["POST"])
def request_password_reset():
    """Handles password reset requests."""
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Email not found"}), 404

    # Generate password reset token
    reset_token = str(uuid.uuid4())
    token_expiry = datetime.utcnow() + timedelta(hours=1)  # Expires in 1 hour

    # Store reset token in the database
    users_collection.update_one(
        {"email": email},
        {"$set": {"reset_token": reset_token, "reset_expiry": token_expiry}}
    )

    # Generate reset link
    try:
        reset_link = url_for("auth.reset_password", token=reset_token, _external=True)
    except:
        reset_link = f"{Config.BASE_URL}/reset-password/{reset_token}"

    # Send email
    send_password_reset_email(email, reset_link)

    return jsonify({"message": "Password reset email sent."}), 200

def send_password_reset_email(email, reset_link):
    """Sends password reset email with HTML formatting."""
    try:
        msg = Message("Password Reset Request", sender=Config.MAIL_DEFAULT_SENDER, recipients=[email])
        msg.html = f"""
        <html>
        <head>
            <style>
                .button {{
                    background-color: #28a745;
                    color: white;
                    padding: 12px 20px;
                    text-decoration: none;
                    font-size: 16px;
                    border-radius: 5px;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <h2>Password Reset Request</h2>
            <p>Click the button below to reset your password. This link will expire in 1 hour.</p>
            <a href="{reset_link}" class="button">Reset Password</a>
            <p>If you did not request this, please ignore this email.</p>
        </body>
        </html>
        """
        mail.send(msg)
    except Exception as e:
        print(f"⚠️ Failed to send email: {e}")

@auth_bp.route("/reset-password/<token>", methods=["POST"])
def reset_password(token):
    """Handles password reset after clicking the reset link."""
    data = request.json
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    # Find user by reset token
    user = users_collection.find_one({"reset_token": token})
    if not user:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    # Check if token has expired
    if datetime.utcnow() > user["reset_expiry"]:
        return jsonify({"error": "Reset token expired. Request a new one."}), 400

    # Hash the new password explicitly
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256:150000')  # Modified

    # Update password in database and remove reset token
    users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"password_hash": hashed_password}, "$unset": {"reset_token": "", "reset_expiry": ""}}
    )

    return jsonify({"message": "Password successfully reset. You can now log in."}), 200

# New route for agrovet registration
@auth_bp.route("/register/agrovet", methods=["POST"])
def register_agrovet():
    data = request.json
    name = data.get("name")
    county = data.get("county")
    town = data.get("town")
    contact = data.get("contact")

    if not name or not county or not town or not contact:
        return jsonify({"error": "All fields are required"}), 400

    # Fetch geolocation data for the specified town and county
    geolocation = geolocation_collection.find_one({"county": county, "town": town})
    if not geolocation:
        return jsonify({"error": "Town and county not found in geolocation database"}), 404

    try:
        agrovets_collection.insert_one({
            "name": name,
            "county": county,
            "town": town,
            "location": geolocation["location"],
            "contact": contact
        })
        return jsonify({"message": "Agrovet registered successfully"}), 201
    except Exception as e:
        logging.error(f"⚠️ Error registering agrovet: {e}")
        return jsonify({"error": "Failed to register agrovet"}), 500
    
# New route for extension worker registration
@auth_bp.route("/register/extension-worker", methods=["POST"])
def register_extension_worker():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    services = data.get("services", [])
    county = data.get("county")
    town = data.get("town")
    contact = data.get("contact")

    if not first_name or not last_name or not services or not county or not town or not contact:
        return jsonify({"error": "All fields are required"}), 400

    # Fetch geolocation data for the specified town and county
    geolocation = geolocation_collection.find_one({"county": county, "town": town})
    if not geolocation:
        return jsonify({"error": "Town and county not found in geolocation database"}), 404

    try:
        extension_workers_collection.insert_one({
            "first_name": first_name,
            "last_name": last_name,
            "services": services,
            "county": county,
            "town": town,
            "location": geolocation["location"],
            "contact": contact
        })
        return jsonify({"message": "Extension worker registered successfully"}), 201
    except Exception as e:
        logging.error(f"⚠️ Error registering extension worker: {e}")
        return jsonify({"error": "Failed to register extension worker"}), 500
    
# Initialize Firebase Admin SDK once
if not firebase_admin._apps:
    cred = credentials.Certificate(Config.FIREBASE_ADMIN_CREDENTIAL)
    firebase_admin.initialize_app(cred)

@auth_bp.route('/api/firebase-auth', methods=['POST'])
def firebase_auth_route():
    data = request.get_json()
    id_token = data.get('id_token')
    if not id_token:
        return jsonify({'error': 'Missing token'}), 400

    try:
        decoded = firebase_auth.verify_id_token(id_token)
        phone = decoded.get('phone_number')
        uid = decoded.get('uid')

        # Example: check user in DB and create if doesn't exist
        # You could store this in SQLAlchemy, etc.
        # if not User.query.filter_by(uid=uid).first():
        #     create_user(phone, uid)

        return jsonify({'message': 'User authenticated', 'phone': phone}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 401
    
@auth_bp.route('/firebase-phone-login', methods=['POST'])
def firebase_phone_login():
    """
    Accepts an ID token from Firebase, verifies it, and either registers or logs in the user.
    """
    data = request.json
    id_token = data.get('id_token')

    if not id_token:
        return jsonify({'error': 'Missing Firebase ID token'}), 400

    try:
        # Verify Firebase token
        decoded_token = firebase_auth.verify_id_token(id_token)
        phone_number = decoded_token.get('phone_number')
        uid = decoded_token.get('uid')

        if not phone_number:
            return jsonify({'error': 'Phone number not found in Firebase token'}), 400

        # Check if user exists in MongoDB
        user = users_collection.find_one({"phone": phone_number})
        if not user:
            # First-time login, create user
            user_doc = {
                "phone": phone_number,
                "firebase_uid": uid,
                "is_verified": True,
                "created_at": datetime.utcnow()
            }
            users_collection.insert_one(user_doc)

        # (Optional) Create JWT for app session
        jwt_token = jwt.encode({
            "phone": phone_number,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm="HS256")

        return jsonify({
            "message": "Phone login successful",
            "phone": phone_number,
            "token": jwt_token
        }), 200

    except Exception as e:
        logging.error(f"Firebase phone auth failed: {e}")
        return jsonify({'error': 'Firebase token verification failed'}), 401