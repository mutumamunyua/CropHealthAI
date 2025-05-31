🌱 CropHealthAI

AI-Powered Crop Health Diagnosis for Smarter Farming

⸻

Author:
Philip Munyua, PhD
🌍 Global Executive Leader in AI, ML, Data Science & Cloud | AI & Data Strategist | Driving Business Growth Through Intelligent Automation & Real-Time Decision-Making
📧 Email: mutumamunyua@gmail.com
🔗 LinkedIn | 🔗 GitHub

⸻

📌 Overview

CropHealthAI is an AI-powered web application that enables farmers and agronomists to quickly detect maize leaf diseases using cutting-edge machine learning and deep learning models. By uploading a photo of a maize leaf, users receive an instant disease classification with confidence scores, helping them make informed decisions to protect crop health and yields.

⸻

⚙️ Features
	•	✅ Real-Time Disease Detection: Upload an image and get instant predictions with confidence levels.
	•	✅ Pre-Trained ML Models: Powered by Roboflow Inference API and advanced deep learning.
	•	✅ Multi-File Upload: Analyze multiple leaves at once.
	•	✅ Mobile-Responsive: Designed to work seamlessly on desktops and smartphones.
	•	✅ User-Friendly Interface: Intuitive and easy to navigate for all users.

⸻

🛠️ Tech Stack

Frontend:
	•	HTML, CSS, JavaScript
	•	Bootstrap (Responsive Design)

Backend:
	•	Python (Flask Framework)
	•	Roboflow Inference API (Computer Vision Inference)

AI Models:
	•	Pre-trained Deep Learning Model (Maize Leaf Disease Dataset)
	•	Large Language Models (LLMs) for enhanced AI interactions

⸻

📂 Project Structure

CropHealthAI/
├── backend/         # Flask backend (API and inference logic)
├── frontend/        # Frontend (HTML, CSS, JavaScript)
│   ├── static/      # Assets (CSS, JS, images)
│   └── index.html   # Main page
├── images/          # Sample maize leaf images
├── infer.py         # Inference script
├── venv/            # Virtual environment (dependencies)
├── README.md        # Documentation



⸻

🚀 How to Run Locally
	1.	Clone the Repository

git clone https://github.com/mutumamunyua/CropHealthAI.git
cd CropHealthAI


	2.	Create and Activate Virtual Environment

python3 -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows


	3.	Install Dependencies

pip install -r requirements.txt


	4.	Run the Flask Server

cd backend
python app.py

Server will start at http://127.0.0.1:5000/.

	5.	Serve the Frontend

cd frontend
python3 -m http.server 8000

Access the app at http://127.0.0.1:8000/index.html.

⸻

📷 How to Use
	1.	Upload an image of a maize leaf.
	2.	Click Analyze.
	3.	View the disease prediction and confidence score.

⸻

🔮 Future Enhancements
	•	🌾 Expand to other crops and plant diseases.
	•	📩 Enable SMS/WhatsApp real-time alerts for farmers.
	•	📱 Build a native mobile app version.
	•	☁️ Integrate weather APIs for context-based risk warnings.

⸻

📝 License

This project is licensed under the MIT License.

⸻

🤝 Contribute & Support

Interested in contributing?
	•	Fork the repo, create a branch, and submit a pull request!
	•	Feedback and collaboration are welcome.

📩 Email: mutumamunyua@gmail.com
🚀 Let’s revolutionize agriculture with AI!

⸻

🌟 Star the repository if you find it helpful!

<!-- Trigger redeploy - May 30, 2025 -->
