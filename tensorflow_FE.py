import numpy as np
from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore
import cv2

# CNN Model
cnn_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_cnn_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = cnn_model.predict(x)
    return features[0]

def extract_glcm_features(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    glcm = graycomatrix(img, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast')[0][0]
    dissimilarity = graycoprops(glcm, 'dissimilarity')[0][0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0][0]
    ASM = graycoprops(glcm, 'ASM')[0][0]
    energy = graycoprops(glcm, 'energy')[0][0]
    correlation = graycoprops(glcm, 'correlation')[0][0]
    return np.array([contrast, dissimilarity, homogeneity, ASM, energy, correlation])

# Gabungkan dua fitur
cnn_feat = extract_cnn_features('gambar_baju.jpg')
glcm_feat = extract_glcm_features('gambar_baju.jpg')
combined_feat = np.concatenate((cnn_feat, glcm_feat))
