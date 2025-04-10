import cv2
import numpy as np
import pandas as pd
from joblib import load
from rembg import remove
from tkinter import filedialog

from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore

# Fungsi untuk menghitung GLCM dan mengambil fitur
def extract_glcm_features(image):

    # Konversi ke grayscale <<< GLCM
    gray = cv2.cvtColor(image,cv2.COLOR_RGBA2GRAY)

    # Hitung matriks GLCM dengan semua sudut
    glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=256, symmetric=True, normed=True)

    # Ekstraksi fitur dari matriks GLCM
    contrast = graycoprops(glcm, 'contrast').ravel()
    dissimilarity = graycoprops(glcm, 'dissimilarity').ravel()
    homogeneity = graycoprops(glcm, 'homogeneity').ravel()
    energy = graycoprops(glcm, 'energy').ravel()
    correlation = graycoprops(glcm, 'correlation').ravel()

    # Gabungkan fitur ke dalam satu baris DataFrame
    glcm_features = np.concatenate([contrast,dissimilarity,homogeneity, energy, correlation])

    return glcm_features

# CNN Model
cnn_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_cnn_features(img_array):
    # Pastikan hanya 3 channel (RGB)
    if img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

    # Resize
    img = cv2.resize(img_array, (224, 224))

    # Tambah batch dimension dan preprocess
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)

    # Prediksi fitur
    features = cnn_model.predict(x)
    
    # return features[0]
    return features.flatten()


# Load the saved model
loaded_model = load('knn_best_model.pkl')

# Baca gambar dari direktori menggunakan GUI
image_path = filedialog.askopenfilename(title="Pilih gambar")

# Baca gambar menggunakan OpenCV
image = cv2.imread(image_path)

# Tentukan ukuran yang diinginkan
width = 256
height = 256

# Resize citra dengan ukuran baru
resized_image = cv2.resize(image, (width, height))

#hapus background
output = remove(resized_image)

# --- Load citra dengan latar belakang transparan
gray_image = output

# Ambil saluran alpha (mask) dari citra
alpha = output[:, :, 3]

# Hitung histogram citra sebelum penyejajaran
hist, bins = np.histogram(gray_image.flatten(), 256, [0, 256])

# Hitung fungsi distribusi kumulatif (CDF)
cdf = hist.cumsum()
cdf_normalized = cdf * hist.max() / cdf.max()

# Lakukan penyejajaran histogram pada citra grayscale
# equalized_image = cv2.equalizeHist(gray_image)
equalized_image_red = cv2.equalizeHist(gray_image[:,:,0])
equalized_image_green = cv2.equalizeHist(gray_image[:,:,1])
equalized_image_blue = cv2.equalizeHist(gray_image[:,:,2])

# Gabungkan kembali saluran grayscale dan alpha menjadi citra RGBA
equalized_image_rgba = np.zeros_like(output)
equalized_image_rgba[:, :, 0] = equalized_image_red
equalized_image_rgba[:, :, 1] = equalized_image_green
equalized_image_rgba[:, :, 2] = equalized_image_blue
equalized_image_rgba[:, :, 3] = alpha

# Ekstraksi fitur GLCM dari gambar
glcm_features = extract_glcm_features(equalized_image_rgba).flatten()

# CNN Pretrained Feature Extractor dari gambar
CNN_features = extract_cnn_features(equalized_image_rgba).flatten()

combined_features = np.concatenate((CNN_features, glcm_features))


print(image_path)

# Set feature names for the input data
feature_names = np.load('feature_names.npy', allow_pickle=True)
features_df = pd.DataFrame([combined_features], columns=feature_names)


# Use it for prediction
predictions = loaded_model.predict(features_df)


print("Hasil Klasifikasi:", predictions[0])