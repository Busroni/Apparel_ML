import cv2
import numpy as np
import pandas as pd
from joblib import dump
from rembg import remove
from tkinter import filedialog

from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore

from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

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

# Baca dataset glcm_features.csv menggunakan pandas
data = pd.read_csv('dataset_GLCM_CNN_210.csv')

# Pisahkan fitur (X) dan label (y)
X = data.drop('label', axis=1)
y = data['label']

# Bagi data menjadi data latih dan data uji
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=126)

# Buat model KNN
model = KNeighborsClassifier()

# Definisikan grid hyperparameter yang akan ditelusuri
param_grid = {
        'n_neighbors': [3, 5 , 7, 9, 11, 13],
        'weights': ['uniform', 'distance'],
        'metric': ['euclidean']
    }

# Buat objek KNeighborsClassifier
model = KNeighborsClassifier()

# Buat objek GridSearchCV
grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')

# Latih model dengan data latih
grid_search.fit(X_train, y_train)

# Dapatkan model terbaik setelah hyperparameter tuning
best_model = grid_search.best_estimator_

#joblib penyimpanan model knn
dump(best_model, 'knn_best_model.pkl')

np.save('feature_names.npy', X.columns)

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

# Reshape fitur menjadi satu baris 
# glcm_features = np.array(glcm_features) <<<RGB
# glcm_features = glcm_features.reshape(1, -1)

# CNN Pretrained Feature Extractor dari gambar
CNN_features = extract_cnn_features(equalized_image_rgba).flatten()
# CNN_features = CNN_features.reshape(1, -1)

combined_features = np.concatenate((CNN_features, glcm_features))


print(image_path)

# Set feature names for the input data
feature_names = X.columns
features_df = pd.DataFrame([combined_features], columns=feature_names)


# Lakukan prediksi menggunakan model KNN terbaik
prediction = best_model.predict(features_df)

# Tampilkan parameter terbaik
print("Hyperparameter terbaik:", grid_search.best_params_)

# Evaluasi model terbaik pada data uji
y_pred = best_model.predict(X_test)

 
# Hitung confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Menampilkan confusion matrix menggunakan heatmap
# sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
# plt.xlabel('Predicted')
# plt.ylabel('Actual')
# plt.title('Confusion Matrix')
# plt.show()

accuracy = best_model.score(X_test, y_test)
print("Akurasi model terbaik:", accuracy)


# # Untuk mendapatkan rincian Euclidean dari 10 tetangga terdekat
# distances, indices = best_model.kneighbors(glcm_features_df)

# # Tampilkan hasil prediksi
# print(f"Hasil Klasifikasi: {prediction[0]}")
# print("\nRincian Euclidean dari 10 Tetangga Terdekat dan Label mereka:")

# for i in range(len(glcm_features_df)):
#     print(f"\nData ke-{i+1}:")
#     for j in range(len(indices[i])):
#         # Mengambil indeks tetangga
#         neighbor_idx = indices[i][j]
#         # Mengambil parameter tetangga
#         neighbor_params = X.iloc[neighbor_idx].to_dict()
#         # Mengambil label tetangga
#         neighbor_label = y.iloc[neighbor_idx]
#         print(f"Tetangga {j+1}: Index: {neighbor_idx}, Jarak: {distances[i][j]}")
#         print("Parameter tetangga:", neighbor_params)
#         print("Label tetangga:", neighbor_label)

print("Hasil Klasifikasi:", prediction[0])