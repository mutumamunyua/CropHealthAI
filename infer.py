from inference_sdk import InferenceHTTPClient

# Initialize client
CLIENT = InferenceHTTPClient(
    api_url="https://classify.roboflow.com",
    api_key="RXTncMUBhY7fRFBzS888"
)

# Path to the image
image_path = "/Users/philipmunyua/Documents/CropHealthAI/images/maize1.jpeg"

# Run inference
result = CLIENT.infer(image_path, model_id="corn-maize-leaf-disease/1")

# Print results
print(result)