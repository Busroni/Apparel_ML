# predict.py

import sys
import cv2
import numpy as np
import pandas as pd
from joblib import load
from rembg import remove
from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore

# Load model dan info fitur
cnn_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
loaded_model = load('knn_best_model.pkl')
feature_names = np.load('feature_names.npy', allow_pickle=True)

def extract_glcm_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
    glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                        levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast').ravel()
    dissimilarity = graycoprops(glcm, 'dissimilarity').ravel()
    homogeneity = graycoprops(glcm, 'homogeneity').ravel()
    energy = graycoprops(glcm, 'energy').ravel()
    correlation = graycoprops(glcm, 'correlation').ravel()
    return np.concatenate([contrast, dissimilarity, homogeneity, energy, correlation])

def extract_cnn_features(img_array):
    if img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    img = cv2.resize(img_array, (224, 224))
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)
    features = cnn_model.predict(x)
    return features.flatten()

# Ambil path dari command-line argument
image_path = sys.argv[1]

# Proses gambar
image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

if image is None:
    print(f"❌ Gagal membaca gambar dari path: {image_path}")
    sys.exit(1)
    
resized_image = cv2.resize(image, (256, 256))
output = remove(resized_image)

alpha = output[:, :, 3]
r = cv2.equalizeHist(output[:, :, 0])
g = cv2.equalizeHist(output[:, :, 1])
b = cv2.equalizeHist(output[:, :, 2])
equalized_image = np.zeros_like(output)
equalized_image[:, :, 0] = r
equalized_image[:, :, 1] = g
equalized_image[:, :, 2] = b
equalized_image[:, :, 3] = alpha

glcm = extract_glcm_features(equalized_image)
cnn = extract_cnn_features(equalized_image)
combined = np.concatenate((cnn, glcm))

features_df = pd.DataFrame([combined], columns=feature_names)
prediction = loaded_model.predict(features_df)

# Cetak hasil ke stdout
print(prediction[0])
