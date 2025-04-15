import torch
import torchvision.models as models

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

print("ResNet50 model with 5 classes loaded successfully!")