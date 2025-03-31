from flask import Blueprint, request, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import uuid
import jwt
import os
from datetime import datetime, timedelta
from config import users_collection, mail, Config
import logging

auth_bp = Blueprint("auth", __name__)

# Ensure email is uniquely indexed
users_collection.create_index("email", unique=True)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # Check if email already exists
    if users_collection.find_one({"email": email}):
        return jsonify({"error": "Email already registered"}), 409

    # Hash password
    hashed_password = generate_password_hash(password)

    # Generate verification token with expiry
    verification_token = str(uuid.uuid4())
    token_expiry = datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours

    # Store user in DB (unverified)
    users_collection.insert_one({
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "is_verified": False,
        "verification_token": verification_token,
        "token_expiry": token_expiry
    })

    # Send verification email
    verification_link = url_for("auth.verify_email", token=verification_token, _external=True)
    send_verification_email(email, verification_link)

    return jsonify({"message": "User registered. Check email to verify account."}), 201
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    """Handles user login and returns a JWT token."""
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Find user in database
    user = users_collection.find_one({"email": email})
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401

    # Check if password is correct
    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Check if the account is verified
    if not user.get("is_verified", False):
        return jsonify({"error": "Email not verified. Please check your inbox."}), 403

    # Generate a JWT token
    token = jwt.encode(
        {
            "email": email, 
            "sub": email,
            "exp": datetime.utcnow() + timedelta(hours=24)
        },
        Config.SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token}), 200


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
    reset_link = url_for("auth.reset_password", token=reset_token, _external=True)

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

    # Hash the new password
    hashed_password = generate_password_hash(new_password)

    # Update password in database and remove reset token
    users_collection.update_one(
        {"email": user["email"]},
        {"$set": {"password_hash": hashed_password}, "$unset": {"reset_token": "", "reset_expiry": ""}}
    )

    return jsonify({"message": "Password successfully reset. You can now log in."}), 200