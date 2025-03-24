from inference_sdk import InferenceHTTPClient

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key="RXTncMUBhY7fRFBzS888"  # Your API key
)

def predict_image(img_path):
    """Runs inference on an image using the Roboflow model."""
    try:
        result = CLIENT.infer(img_path, model_id="corn-maize-leaf-disease/1")
        
        # Ensure result contains expected keys before accessing
        if "top" in result and "confidence" in result:
            return {
                "prediction": result["top"],  # Get the top predicted class
                "confidence": result["confidence"]
            }
        else:
            return {"error": "Unexpected API response format: " + str(result)}

    except Exception as e:
        return {"error": f"Inference error: {str(e)}"}