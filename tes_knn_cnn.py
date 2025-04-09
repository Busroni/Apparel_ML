import cv2
import numpy as np
import pandas as pd
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

# Fungsi untuk menghitung GLCM dan mengambil fitur
def extract_glcm_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
    glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4],
                        levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast').ravel()
    dissimilarity = graycoprops(glcm, 'dissimilarity').ravel()
    homogeneity = graycoprops(glcm, 'homogeneity').ravel()
    energy = graycoprops(glcm, 'energy').ravel()
    correlation = graycoprops(glcm, 'correlation').ravel()
    glcm_features = np.concatenate([contrast, dissimilarity, homogeneity, energy, correlation])
    return glcm_features

# CNN Model
cnn_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_cnn_features(img_array):
    if img_array.shape[-1] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    img = cv2.resize(img_array, (224, 224))
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)
    features = cnn_model.predict(x)
    return features.flatten()

# Baca dataset dan pisahkan fitur serta label
data = pd.read_csv('dataset_GLCM_CNN.csv')
X = data.drop('label', axis=1)
y = data['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=18)

# Grid search dan training model
param_grid = {
    'n_neighbors': [3, 5, 7, 9, 11, 13],
    'weights': ['uniform', 'distance'],
    'metric': ['euclidean']
}
grid_search = GridSearchCV(KNeighborsClassifier(), param_grid, cv=5, scoring='accuracy')
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_

# Proses input gambar
image_path = filedialog.askopenfilename(title="Pilih gambar")
image = cv2.imread(image_path)
resized_image = cv2.resize(image, (256, 256))
output = remove(resized_image)
gray_image = output
alpha = output[:, :, 3]

# Equalisasi saluran warna
equalized_image_rgba = np.zeros_like(output)
equalized_image_rgba[:, :, 0] = cv2.equalizeHist(gray_image[:, :, 0])
equalized_image_rgba[:, :, 1] = cv2.equalizeHist(gray_image[:, :, 1])
equalized_image_rgba[:, :, 2] = cv2.equalizeHist(gray_image[:, :, 2])
equalized_image_rgba[:, :, 3] = alpha

# Ekstraksi fitur GLCM dan CNN
glcm_features = extract_glcm_features(equalized_image_rgba).flatten()
CNN_features = extract_cnn_features(equalized_image_rgba).flatten()
combined_features = np.concatenate((CNN_features, glcm_features))

print("Shape GLCM:", glcm_features.shape)
print("Shape CNN:", CNN_features.shape)
print("Combined features shape:", combined_features.shape)
print(image_path)

# Buat DataFrame tanpa kolom (biarkan auto-index)
features_df = pd.DataFrame([combined_features])

# Prediksi
prediction = best_model.predict(features_df)

# Evaluasi model
print("Hyperparameter terbaik:", grid_search.best_params_)
y_pred = best_model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

accuracy = best_model.score(X_test, y_test)
print("Akurasi model terbaik:", accuracy)

# Akurasi per kelas
n_classes = len(np.unique(y_test))
class_labels = sorted(np.unique(y_test))
accuracies_per_class = []
for i in range(n_classes):
    correct_predictions = cm[i, i]
    total_predictions = np.sum(cm[i, :])
    accuracy = correct_predictions / total_predictions
    accuracies_per_class.append(accuracy)

print("\nAkurasi per Kelas:")
for label, acc in zip(class_labels, accuracies_per_class):
    print(f"Kelas {label}: {acc:.4f}")

print("Hasil Klasifikasi:", prediction[0])