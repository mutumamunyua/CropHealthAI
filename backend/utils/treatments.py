DEMO_TREATMENTS = {
    "Gray_Leaf_Spot": {
        "text": "Rotate crops annually, apply fungicides like strobilurins or triazoles, and ensure good field drainage and proper plant spacing.",
        "images": ["Gray_Leaf_Spot_Fungicide.jpeg"]
    },
    "Common_Rust": {
        "text": "Apply fungicides containing propiconazole or azoxystrobin, plant resistant corn varieties, and avoid overhead irrigation.",
        "images": ["Common_Rust_Fungicide.jpeg"]
    },
    "Blight": {
        "text": "Rotate crops, plant resistant varieties, and apply fungicides like mancozeb or strobilurin when symptoms first appear.",
        "images": ["NL_Blight_Fungicide.jpeg"]
    },
    "Healthy": {
        "text": "Your corn plant looks healthy! Continue to monitor for any signs of disease and ensure proper spacing for airflow.",
        "images": ["Healthy.jpeg"]
    },
    # Add more diseases and treatments as needed
}

def get_treatment_recommendation(diagnosis):
    return DEMO_TREATMENTS.get(diagnosis, {
        "text": "No specific treatment recommendation available.",
        "images": []
    })