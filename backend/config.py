import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), "images")  # Stores uploaded images
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS