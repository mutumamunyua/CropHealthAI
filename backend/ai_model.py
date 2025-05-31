from inference_sdk import InferenceHTTPClient

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key="RXTncMUBhY7fRFBzS888"  # Your API key
)

def predict_image(img_path):
    """Runs inference on an image using the Roboflow model."""
    try:
        print(f"🔍 Running AI Model on: {img_path}")  # Debugging log
        
        # Call the AI Model
        result = CLIENT.infer(img_path, model_id="corn-maize-leaf-disease/1")
        print(f"📡 AI API Response: {result}")  # Log response from API

        # Validate response
        if "predictions" in result and len(result["predictions"]) > 0:
            prediction = result["predictions"][0]  # Get top prediction
            
            return {
                "filename": img_path.split("/")[-1],  # Extract filename
                "disease": prediction["class"],  # Disease name
                "confidence": f"{prediction['confidence'] * 100:.2f}%"  # Convert to %
            }
        else:
            return {"error": "No disease detected"}

    except Exception as e:
        print(f"⚠️ AI Model Error: {str(e)}")  # Debugging log
        return {"error": f"Inference error: {str(e)}"}