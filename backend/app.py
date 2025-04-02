from flask import Flask, send_from_directory, request, jsonify
import os
from werkzeug.utils import secure_filename
from ai_model import predict_image
from flask_cors import CORS
from config import mail, Config, users_collection
from pymongo import MongoClient
from routes.auth import auth_bp
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Load email settings
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

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def home():
    return "Flask server is running!"

@app.route('/')
def serve_index():
    """Serve the main index.html from the frontend folder."""
    return send_from_directory('../frontend', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve all static files (JS, CSS) from the frontend/static folder."""
    return send_from_directory('../frontend/static', path)

@app.route("/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        print("⚠️ No files received in request")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files or files[0].filename == '':
        print("⚠️ No files selected")
        return jsonify({"error": "No selected files"}), 400

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

                # Correct extraction based on your actual AI response
                prediction_result = result.get("disease", "Unknown")
                confidence_score_str = result.get("confidence", "0%").replace('%', '')
                confidence_score = float(confidence_score_str)

                results.append({
                    "disease": prediction_result,
                    "confidence": confidence_score
                })

                # Save prediction correctly to MongoDB
                try:
                    db.predictions.insert_one({
                        "filename": filename,
                        "prediction_result": prediction_result,
                        "confidence_score": confidence_score,
                        "timestamp": datetime.utcnow()
                    })
                except Exception as db_error:
                    print(f"⚠️ MongoDB Insert Error: {db_error}")

            except Exception as e:
                print(f"⚠️ AI Model Error: {e}")
                results.append({
                    "disease": "Prediction Failed",
                    "confidence": 0
                })

    print("🔥 Final API Response:", results)

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)