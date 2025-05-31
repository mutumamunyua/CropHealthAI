import os

# Define a dictionary for treatment recommendations and images
DEMO_TREATMENTS = {
    "Corn - Cercospora Leaf Spot (Gray Leaf Spot)": {
        "text": "Rotate crops annually, apply fungicides like strobilurins or triazoles, and ensure good field drainage and proper plant spacing.",
        "image": "gray_leaf_spot.jpg"
    },
    "Corn - Common Rust": {
        "text": "Apply fungicides containing propiconazole or azoxystrobin, plant resistant corn varieties, and avoid overhead irrigation.",
        "image": "common_rust.jpg"
    },
    "Corn - Northern Leaf Blight": {
        "text": "Rotate crops, plant resistant varieties, and apply fungicides like mancozeb or strobilurin when symptoms first appear.",
        "image": "northern_leaf_blight.jpg"
    },
    "Corn - Healthy": {
        "text": "Your corn plant looks healthy! Continue to monitor for any signs of disease and ensure proper spacing for airflow.",
        "image": "healthy.jpg"
    }
}

def get_treatment_recommendation(diagnosis):
    # Check if the diagnosis is in the DEMO_TREATMENTS dictionary
    if diagnosis in DEMO_TREATMENTS:
        return DEMO_TREATMENTS[diagnosis]
    else:
        return {
            "text": "No specific treatment recommendation available.",
            "image": "default.jpg"  # Default image if no treatment is found
        }