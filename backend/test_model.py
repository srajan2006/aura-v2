import numpy as np
import json
from tensorflow import keras
from PIL import Image

# Load model
model = keras.models.load_model("aura_garment_model.h5")

# Load labels
with open("class_names.json", "r") as f:
    labels = json.load(f)

print("Model loaded!")
print(f"Labels: {labels}")
print(f"Model input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")

# Test with a sample image
test_image_path = "uploads/IMG-20250824-WA0016.jpg"

# Try different preprocessing methods
print("\n=== Testing different preprocessing methods ===\n")

# Method 1: Standard normalization (0-1)
img = Image.open(test_image_path).resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0)
pred1 = model.predict(img_array, verbose=0)
print(f"Method 1 (0-1 normalization): {labels[np.argmax(pred1)]} - {pred1}")

# Method 2: No normalization
img_array = np.array(img)
img_array = np.expand_dims(img_array, axis=0)
pred2 = model.predict(img_array, verbose=0)
print(f"Method 2 (No normalization): {labels[np.argmax(pred2)]} - {pred2}")

# Method 3: ImageNet normalization
img_array = np.array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = keras.applications.mobilenet_v2.preprocess_input(img_array)
pred3 = model.predict(img_array, verbose=0)
print(f"Method 3 (ImageNet): {labels[np.argmax(pred3)]} - {pred3}")

# Method 4: -1 to 1 normalization
img_array = (np.array(img) / 127.5) - 1
img_array = np.expand_dims(img_array, axis=0)
pred4 = model.predict(img_array, verbose=0)
print(f"Method 4 (-1 to 1): {labels[np.argmax(pred4)]} - {pred4}")