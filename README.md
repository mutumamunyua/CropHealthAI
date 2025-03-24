CropHealthAI 🌱💡

AI-Powered Crop Health Diagnosis

Author:

Philip Munyua, PhD
🌍 Global Executive Leader in AI, ML, Data Science & Cloud | AI & Data Strategist | Driving Business Growth Through Intelligent Automation & Real-Time Decision-Making

📧 Email: mutumamunyua@gmail.com
🔗 LinkedIn: https://www.linkedin.com/in/philmunyua/
🔗 GitHub: https://github.com/mutumamunyua

⸻

📌 Overview

CropHealthAI is an AI-powered web application that enables farmers and agronomists to detect maize leaf diseases using machine learning and deep learning models. The app utilizes a pre-trained Large Language Model (LLM) and computer vision models to classify diseases from uploaded leaf images, helping farmers make informed decisions and improve crop health.

⸻

⚙️ Features

✅ Real-time disease detection: Upload an image of a maize leaf, and the AI model predicts the disease with confidence scores.
✅ Pre-trained ML models: Uses Roboflow Inference API and state-of-the-art deep learning models for high-accuracy predictions.
✅ Multi-file handling: Supports multiple image uploads for batch processing.
✅ User-friendly Interface: A simple web UI for easy interaction.
✅ Mobile Responsive: Works across devices, including smartphones.

⸻

🛠️ Tech Stack

Frontend:
	•	HTML, CSS, JavaScript (User Interface)
	•	Bootstrap (Responsive design)

Backend:
	•	Python (Flask framework) (Handles requests and ML inference)
	•	Roboflow Inference API (For disease classification)

Machine Learning Models Used:
	•	Pre-trained Deep Learning Model (Trained on maize leaf diseases dataset)
	•	Large Language Models (LLMs) for AI-powered assistance

⸻

📂 Project Structure

CropHealthAI/
│── backend/            # Python Flask backend (API, ML processing)
│── frontend/           # Frontend UI (HTML, CSS, JavaScript)
│   │── static/         # CSS, JavaScript, images
│   │── index.html      # Main webpage
│── images/             # Sample maize leaf images
│── infer.py            # AI model inference script
│── venv/               # Virtual environment for dependencies
│── README.md           # Project documentation



⸻

🚀 How to Run the App Locally

1️⃣ Clone the Repository

git clone https://github.com/mutumamunyua/CropHealthAI.git
cd CropHealthAI

2️⃣ Create a Virtual Environment (Recommended)

python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

3️⃣ Install Dependencies

pip install -r requirements.txt

4️⃣ Run the Flask Server

cd backend
python app.py

The server will run at http://127.0.0.1:5000/.

5️⃣ Start the Frontend

cd frontend
python3 -m http.server 8000

Now, open http://127.0.0.1:8000/index.html in your browser.

⸻

📷 How to Use

1️⃣ Upload an image of a maize leaf.
2️⃣ Click “Analyze” to run the AI model.
3️⃣ View results, including disease classification and confidence score.

⸻

🔗 Future Enhancements

🔹 Integrate more crop diseases for broader analysis.
🔹 Implement real-time notifications for farmers via SMS/WhatsApp.
🔹 Develop a mobile app version for on-the-go usage.
🔹 Connect with weather APIs to provide contextual insights on disease risks.

⸻

📝 License

This project is open-source under the MIT License.

⸻

🌱 Contribute & Support

If you’re interested in contributing, feel free to fork this repository, create a branch, and submit a pull request!

📩 Contact: mutumamunyua@gmail.com
🚀 Let’s revolutionize agriculture with AI!
