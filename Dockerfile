# 1) Use a lightweight Python base image
FROM python:3.10-slim

# Install system packages needed by OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
 && apt-get clean  \
 && rm -rf /var/lib/apt/lists/*

# 2) Set the working directory
WORKDIR /app

# 3) Copy only your requirements first (for efficient Docker caching)
COPY backend/requirements.txt ./requirements.txt

# 4) Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy the entire project into /app
COPY . . 

# 6) Expose the port your Flask app runs on
EXPOSE 5001

# 7) Set environment variables (pointing to your MongoDB Atlas, etc.)
#    You can also set these in the hosting platform's dashboard.
ENV MONGO_URI="mongodb+srv://mutumamunyua:Jenna2019@crophealthai.e1qpyqe.mongodb.net/crophealthai?retryWrites=true&w=majority&appName=CropHealthAI"
# 8) Launch the Flask app
CMD ["python", "backend/app.py"]