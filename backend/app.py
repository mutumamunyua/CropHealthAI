from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from ai_model import predict_image
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    """Checks if the uploaded file is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def home():
    return "Flask server is running!"

@app.route("/upload", methods=["POST"])
def upload_files():
    """Handles file uploads and AI model predictions."""
    if "files" not in request.files:
        print("⚠️ No files received in request")
        return jsonify({"error": "No files uploaded"}), 400

    files = request.files.getlist("files")  # Get all uploaded files
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

            # Run AI Model on Uploaded Image
            result = predict_image(file_path)
            results.append(result)

    print("🔥 Final API Response:", results)  # Debugging

    return jsonify({"results": results})

if __name__ == "__main__":
    app.run(debug=True)