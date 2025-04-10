import cv2
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from joblib import load
from rembg import remove
from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore

app = Flask(__name__)

# Load model dan data
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

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['image']
    in_memory_file = np.frombuffer(file.read(), dtype=np.uint8)
    image = cv2.imdecode(in_memory_file, cv2.IMREAD_UNCHANGED)

    resized_image = cv2.resize(image, (256, 256))
    output = remove(resized_image)

    alpha = output[:, :, 3]
    red = cv2.equalizeHist(output[:, :, 0])
    green = cv2.equalizeHist(output[:, :, 1])
    blue = cv2.equalizeHist(output[:, :, 2])

    equalized_image = np.zeros_like(output)
    equalized_image[:, :, 0] = red
    equalized_image[:, :, 1] = green
    equalized_image[:, :, 2] = blue
    equalized_image[:, :, 3] = alpha

    glcm_features = extract_glcm_features(equalized_image)
    cnn_features = extract_cnn_features(equalized_image)
    combined = np.concatenate((cnn_features, glcm_features))

    features_df = pd.DataFrame([combined], columns=feature_names)
    prediction = loaded_model.predict(features_df)

    return jsonify({
        'prediction': prediction[0]
    })

if __name__ == '__main__':
    app.run(debug=True)
