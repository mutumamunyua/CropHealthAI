from flask import Flask, send_from_directory, request, jsonify
import os
from werkzeug.utils import secure_filename
from ai_model import predict_image
from flask_cors import CORS
from config import mail, Config, users_collection, predictions_collection
from pymongo import MongoClient
from routes.auth import auth_bp
from datetime import datetime
from utils.treatments import get_treatment_recommendation  # Added

# [MODIFIED] Define absolute paths for frontend directories based on current working directory.
# When deployed (or with Docker where WORKDIR is /app), your project root should contain the 'frontend' folder.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
FRONTEND_STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TREATMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'treatments')

# Create Flask app using absolute paths for static and template folders.
app = Flask(__name__, static_folder=FRONTEND_STATIC_DIR, template_folder=FRONTEND_DIR)
CORS(app)

# Load email settings and configuration
app.config.from_object(Config)
mail.init_app(app)

# Register authentication routes
app.register_blueprint(auth_bp, url_prefix="/auth")

# MongoDB Connection
try:
    client = MongoClient(Config.MONGO_URI)
    db = client.get_database()
    print("✅ MongoDB Connected Successfully")
except Exception as e:
    print(f"⚠️ MongoDB Connection Error: {e}")
    db = None

# Define predictions collection if db is available (not shown in your snippet but assumed to be handled in your config)
if db is not None:
    predictions_collection = db.get_collection("predictions")
else:
    predictions_collection = None

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Serve the frontend index.html using the absolute path.
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# Serve static assets from the absolute static folder.
@app.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_STATIC_DIR, path)

# Serve treatment images (unchanged)
@app.route('/treatments/<path:filename>')
def serve_treatment_images(filename):
    return send_from_directory(TREATMENTS_DIR, filename)

@app.route('/utils/treatments/<path:disease>', methods=["GET"])
def serve_treatment(disease):
    """
    Serve treatment recommendations based on the disease name.
    """
    try:
        # Use the centralized treatment logic
        treatment = get_treatment_recommendation(disease)

        # Construct full image URLs
        base_url = request.host_url.rstrip("/")  # Get the base URL of the server
        image_urls = [f"{base_url}/treatments/{img}" for img in treatment.get("images", [])]

        return jsonify({
            "treatment": treatment["text"],
            "treatment_images": image_urls
            }), 200

    except Exception as e:
        print(f"⚠️ Error fetching treatment for {disease}: {e}")
        return jsonify({"error": "Failed to fetch treatment"}), 500

@app.route("/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        print("⚠️ No files received in request")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files or files[0].filename == '':
        print("⚠️ No files selected")
        return jsonify({"error": "No selected files"}), 400

    # Get latitude and longitude from form data, if provided.
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    results = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            print(f"✅ Image Saved: {file_path}")

            try:
                print(f"🔍 Running AI Model on: {file_path}")
                result = predict_image(file_path)
                print(f"📡 AI API Response: {result}")

                # Correctly extract prediction details based on your API response.
                prediction_result = result.get("disease", "Unknown")
                confidence_score_str = result.get("confidence", "0%").replace('%', '')
                confidence_score = float(confidence_score_str)

                # Get treatment recommendation (if applicable).
                treatment = get_treatment_recommendation(prediction_result)

                results.append({
                    "disease": prediction_result,
                    "confidence": confidence_score,
                    "treatment": treatment
                })

                # Save prediction to MongoDB.
                try:
                    predictions_collection.insert_one({
                        "filename": filename,
                        "prediction_result": prediction_result,
                        "confidence_score": confidence_score,
                        "latitude": latitude,
                        "longitude": longitude,
                        "treatment": treatment,
                        "timestamp": datetime.utcnow()
                    })
                except Exception as db_error:
                    print(f"⚠️ MongoDB Insert Error: {db_error}")

            except Exception as e:
                print(f"⚠️ AI Model Error: {e}")
                results.append({
                    "disease": "Prediction Failed",
                    "confidence": 0,
                    "treatment": {
                        "text": "No specific treatment recommendation available.",
                        "images": []
                    }
                })

    print("🔥 Final API Response:", results)
    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)