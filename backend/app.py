from flask import Flask, send_from_directory, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from ai_model import predict_image
from flask_cors import CORS
from config import mail, Config, users_collection, predictions_collection
from pymongo import MongoClient, GEOSPHERE
from routes.auth import auth_bp
from datetime import datetime
from utils.treatments import get_treatment_recommendation  # Added
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

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
    agrovets_collection = db.get_collection("agrovets")
    extension_workers_collection = db.get_collection("extension_workers")
    geolocation_collection = db.get_collection("geolocation")
else:
    predictions_collection = None
    agrovets_collection = None
    extension_workers_collection = None
    geolocation_collection = None

# Ensure geospatial indexes are created
if agrovets_collection is not None:
    agrovets_collection.create_index([("location", GEOSPHERE)])
    
if extension_workers_collection is not None:
    extension_workers_collection.create_index([("location", GEOSPHERE)])

if geolocation_collection is not None:
    geolocation_collection.create_index([("location", GEOSPHERE)])

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

@app.route('/auth/register-phone', methods=['POST'])
def register_with_phone():
    data = request.json
    phone = data.get('phone')

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    try:
        existing_user = users_collection.find_one({"phone": phone})
        if existing_user:
            return jsonify({"message": "User already registered"}), 200

        users_collection.insert_one({
            "phone": phone,
            "created_at": datetime.utcnow()
        })
        return jsonify({"message": "Phone user registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500

# Serve treatment images (unchanged)
@app.route('/treatments/<path:filename>')
def serve_treatment_images(filename):
    return send_from_directory(TREATMENTS_DIR, filename)

@app.route('/utils/treatments/<path:disease>', methods=["GET"])
def serve_treatment(disease):
    try:
        treatment = get_treatment_recommendation(disease)
        base_url = Config.BASE_URL.rstrip("/")
        image_urls = [f"{base_url}/treatments/{img}" for img in treatment.get("images", [])]

        latitude = request.args.get("latitude")
        longitude = request.args.get("longitude")

        if latitude and longitude:
            nearby_agrovets = fetch_nearby_agrovets(latitude, longitude)
            nearby_extension_workers = fetch_nearby_extension_workers(latitude, longitude, treatment.get("services", []))
        else:
            nearby_agrovets = []
            nearby_extension_workers = []

        return jsonify({
            "treatment": treatment["text"],
            "treatment_images": image_urls,
            "agrovets": nearby_agrovets,
            "extension_workers": nearby_extension_workers
        }), 200

    except Exception as e:
        print(f"⚠️ Error fetching treatment for {disease}: {e}")
        return jsonify({"error": "Failed to fetch treatment"}), 500

@app.route("/upload", methods=["POST"])
def upload_files():
    if "files" not in request.files:
        logging.error("⚠️ No files received in request")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")
    if not files or files[0].filename == '':
        logging.error("⚠️ No files selected")
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

            logging.info(f"✅ Image Saved: {file_path}")

            try:
                logging.info(f"🔍 Running AI Model on: {file_path}")
                result = predict_image(file_path)
                logging.info(f"📡 AI API Response: {result}")

                # Correctly extract prediction details based on your API response.
                prediction_result = result.get("disease", "Unknown")
                confidence_score_str = result.get("confidence", "0%").replace('%', '')
                confidence_score = float(confidence_score_str)

                # Get treatment recommendation (if applicable).
                treatment = get_treatment_recommendation(prediction_result)

                # Fetch nearby agrovet shops and extension workers
                nearby_agrovets = fetch_nearby_agrovets(latitude, longitude)
                nearby_extension_workers = fetch_nearby_extension_workers(latitude, longitude, treatment.get("services", []))

                # Convert _id to string for JSON serialization
                nearby_agrovets = [{**agrovet, "_id": str(agrovet["_id"])} for agrovet in nearby_agrovets]
                nearby_extension_workers = [{**worker, "_id": str(worker["_id"])} for worker in nearby_extension_workers]

                results.append({
                    "disease": prediction_result,
                    "confidence": confidence_score,
                    "treatment": treatment,
                    "nearby_agrovets": nearby_agrovets,
                    "nearby_extension_workers": nearby_extension_workers
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
                        "nearby_agrovets": nearby_agrovets,
                        "nearby_extension_workers": nearby_extension_workers,
                        "timestamp": datetime.utcnow()
                    })
                except Exception as db_error:
                    logging.error(f"⚠️ MongoDB Insert Error: {db_error}")

            except Exception as e:
                logging.error(f"⚠️ AI Model Error: {e}")
                results.append({
                    "disease": "Prediction Failed",
                    "confidence": 0,
                    "treatment": {
                        "text": "No specific treatment recommendation available.",
                        "images": []
                    },
                    "nearby_agrovets": [],
                    "nearby_extension_workers": []
                })

    logging.info("🔥 Final API Response: %s", results)
    return jsonify({"results": results})

@app.route('/geolocation/counties', methods=["GET"])
def get_counties():
    try:
        counties = geolocation_collection.distinct("county")
        return jsonify(counties), 200
    except Exception as e:
        logging.error(f"⚠️ Error fetching counties: {e}")
        return jsonify({"error": "Failed to fetch counties"}), 500

@app.route('/geolocation/towns/<path:county>', methods=["GET"])
def get_towns(county):
    try:
        towns = geolocation_collection.find({"county": county}).distinct("town")
        return jsonify(towns), 200
    except Exception as e:
        logging.error(f"⚠️ Error fetching towns for county {county}: {e}")
        return jsonify({"error": "Failed to fetch towns"}), 500

@app.route('/register/agrovet', methods=['POST'])
def register_agrovet():
    data = request.json
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
        print(f"⚠️ Error registering agrovet: {e}")
        return jsonify({"error": "Failed to register agrovet"}), 500

@app.route('/register/extension-worker', methods=['POST'])
def register_extension_worker():
    data = request.json
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    services = data.get("services")
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
            "services": [service.strip().lower() for service in services],
            "county": county,
            "town": town,
            "location": geolocation["location"],
            "contact": contact
        })
        return jsonify({"message": "Extension worker registered successfully"}), 201
    except Exception as e:
        print(f"⚠️ Error registering extension worker: {e}")
        return jsonify({"error": "Failed to register extension worker"}), 500

def fetch_nearby_agrovets(latitude, longitude):
    if latitude is None or longitude is None:
        return []
    try:
        nearby_agrovets = agrovets_collection.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(longitude), float(latitude)]
                    },
                    "$maxDistance": 10000  # 10 km radius
                }
            }
        }).limit(5)  # Limit to 5 nearby agrovets

        # Convert ObjectId to string and format results
        formatted_agrovets = [
            {
                "_id": str(agrovet["_id"]),  # Convert ObjectId to string
                "name": agrovet.get("name", "N/A"),
                "county": agrovet.get("county", "N/A"),
                "town": agrovet.get("town", "N/A"),
                "location": agrovet.get("location", {}),
                "contact": agrovet.get("contact", "N/A")
            }
            for agrovet in nearby_agrovets
        ]
        return formatted_agrovets
    except Exception as e:
        print(f"⚠️ Error fetching nearby agrovets: {e}")
        return []

def fetch_nearby_extension_workers(latitude, longitude, services):
    if latitude is None or longitude is None:
        return []
    try:
        nearby_extension_workers = extension_workers_collection.find({
            "location": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(longitude), float(latitude)]
                    },
                    "$maxDistance": 10000  # 10 km radius
                }
            }    
        }).limit(5)  # Limit to 5 nearby extension workers

        formatted_workers = [
            {
                "_id": str(worker["_id"]),  # Convert ObjectId to string
                "first_name": worker.get("first_name", "N/A"),
                "last_name": worker.get("last_name", "N/A"),
                "services": worker.get("services", []),
                "county": worker.get("county", "N/A"),
                "town": worker.get("town", "N/A"),
                "location": worker.get("location", {}),
                "contact": worker.get("contact", "N/A")
            }
            for worker in nearby_extension_workers
        ]
        return formatted_workers
    except Exception as e:
        print(f"⚠️ Error fetching nearby extension workers: {e}")
        return []
    
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# Existing code...
# Your app = Flask(__name__) and routes are already defined

# New route to serve treatment page
@app.route('/treatment_page/<disease_name>')
def treatment_page(disease_name):
    return render_template("treatment.html", disease_name=disease_name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)