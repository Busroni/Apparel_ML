import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import io

from rembg import remove

# Define device (use GPU if available, else CPU)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Define class names (as per the notebook)
CLASSES = ['dress', 'pants', 'shoes', 'shirts'] 

# Define the image preprocessing pipeline (same as notebook)
# Remove Background
class RemoveBackground:
    def __init__(self):
        pass
    
    def __call__(self, img):
        # Convert PIL image to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Remove background
        output = remove(img_byte_arr)
        
        # Convert back to PIL Image
        return Image.open(io.BytesIO(output)).convert('RGB')

preprocess = transforms.Compose([
    RemoveBackground(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model(model_path):
    """
    Load the trained ResNet-50 model from the specified path.
    
    Args:
        model_path (str): Path to the saved model weights (e.g., 'resnet50_clothing_classifier.pth')
    
    Returns:
        model: Loaded ResNet-50 model ready for inference
    """
    try:
        # Define the ResNet50 architecture with weights=None
        model = models.resnet50(weights=None)  # No pretrained weights, we’ll load custom weights

        # Modify the fully connected layer to match the checkpoint (5 classes)
        num_classes = 4
        model.fc = torch.nn.Linear(model.fc.in_features, num_classes)

        # Load the .pth file with weights_only=True for safety
        state_dict = torch.load('resnet50_clothing_classifier.pth', map_location=torch.device('cpu'), weights_only=True)

        # Load weights into the model
        model.load_state_dict(state_dict)

        # Set model to evaluation mode for inference
        model.eval()
        model.to(device)
        
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

def classify_image(image_path, model):
    """
    Classify a single image using the provided model.
    
    Args:
        image_path (str): Path to the input image
        model: Loaded PyTorch model for inference
    
    Returns:
        tuple: (predicted_class, confidence_scores)
            - predicted_class (str): Name of the predicted class
            - confidence_scores (dict): Dictionary mapping class names to their probabilities
    """
    try:
        # Load and preprocess the image
        image = Image.open(image_path).convert('RGB')
        image_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension
        image_tensor = image_tensor.to(device)
        
        # Perform inference
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1).cpu().numpy()[0]
            predicted_idx = np.argmax(probabilities)
        
        # Map probabilities to class names
        confidence_scores = {CLASSES[i]: float(probabilities[i]) for i in range(len(CLASSES))}
        predicted_class = CLASSES[predicted_idx]
        
        return predicted_class, confidence_scores
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None

def main():
    """
    Example usage of the classification script.
    """
    # Path to the saved model
    model_path = 'resnet50_clothing_classifier.pth'
    
    # Example image path (replace with your image path)
    image_path = 'pn2.jpg'

    
    # Load the model
    model = load_model(model_path)
    if model is None:
        print("Failed to load model. Exiting.")
        return
    
    # Classify the image
    predicted_class, confidence_scores = classify_image(image_path, model)
    
    if predicted_class is not None:
        print(f"\nPredicted Class: {predicted_class}")
        print("File Name : ", image_path)
        print("Confidence Scores:")
        for class_name, score in confidence_scores.items():
            print(f"  {class_name}: {score:.4f}")
    else:
        print("Failed to classify image.")

if __name__ == "__main__":
    main()