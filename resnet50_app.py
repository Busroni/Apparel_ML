from flask import Flask, request, jsonify
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import io
from rembg import remove

# Flask app
app = Flask(__name__)

# Define device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Class names
CLASSES = ['dress', 'pants', 'shirts', 'shoes']

# Background removal transform
class RemoveBackground:
    def __call__(self, img):
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        output = remove(img_byte_arr)
        return Image.open(io.BytesIO(output)).convert('RGB')

# Preprocessing pipeline
preprocess = transforms.Compose([
    RemoveBackground(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load model
def load_model(path):
    model = models.resnet50(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    state_dict = torch.load(path, map_location=torch.device('cpu'), weights_only=True)
    model.load_state_dict(state_dict)
    model.eval().to(device)
    return model

model = load_model('resnet50_clothing_classifier.pth')

# Image classification route
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    try:
        file = request.files['image']
        image = Image.open(file.stream).convert('RGB')
        image_tensor = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image_tensor)
            probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            predicted_idx = np.argmax(probs)
            predicted_class = CLASSES[predicted_idx]
            confidence = {CLASSES[i]: float(probs[i]) for i in range(len(CLASSES))}

        return jsonify({
            'prediction': predicted_class,
            'confidence_scores': confidence
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run Flask
if __name__ == '__main__':
    app.run(debug=True)
