import cv2
import numpy as np
import os
import pandas as pd

from rembg import remove

from skimage.feature import graycomatrix, graycoprops
from tensorflow.keras.applications import ResNet50 # type: ignore
from tensorflow.keras.preprocessing import image # type: ignore
from tensorflow.keras.applications.resnet50 import preprocess_input # type: ignore

from tkinter import Tk, filedialog

# Fungsi untuk menghitung GLCM dan mengambil fitur
def compute_glcm_features(image):
    
    # GLCM <<<
    gray = cv2.cvtColor(image,cv2.COLOR_RGBA2GRAY) 

    # Hitung matriks GLCM dengan semua sudut
    glcm = graycomatrix(gray, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4], levels=256, symmetric=True, normed=True)

    # Ekstraksi fitur dari matriks GLCM
    contrast = graycoprops(glcm, 'contrast').ravel()
    dissimilarity = graycoprops(glcm, 'dissimilarity').ravel()
    homogeneity = graycoprops(glcm, 'homogeneity').ravel()
    energy = graycoprops(glcm, 'energy').ravel()
    correlation = graycoprops(glcm, 'correlation').ravel()

    return np.concatenate([contrast, dissimilarity, homogeneity, energy, correlation])

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

# Fungsi untuk crop gambar berdasarkan objek
def crop_image(image, alpha):
    # Mencari koordinat batas objek pada citra
    y_min, x_min = np.min(np.where(alpha > 0), axis=1)
    y_max, x_max = np.max(np.where(alpha > 0), axis=1)

    # Crop objek dari citra
    cropped_image = image[y_min:y_max, x_min:x_max]

    # tes save file -------------------------
    nameFile = 'G:/ML PAN/DATASET/TES/CROP/' + filename + 'CROP.png'

    cv2.imwrite(nameFile, cropped_image)
    #---------------------------------------
    return cropped_image

# Memasukkan jumlah jenis data
num_classes = 3

# Dictionary untuk menyimpan folder dan label
class_data = {}

# Loop melalui setiap jenis data
for class_idx in range(num_classes):
    # Memilih folder menggunakan GUI dialog
    Tk().withdraw()
    folder_path = filedialog.askdirectory(title=f"Pilih folder untuk jenis data {class_idx+1}")
    class_data[folder_path] = ''

# Loop melalui setiap folder jenis data
for folder_path in class_data.keys():
    class_name = input(f"Masukkan label untuk folder {folder_path}: ")
    class_data[folder_path] = class_name

# List untuk menyimpan fitur dan label
features = []
labels = []

progress = 0

# Loop melalui setiap folder jenis data
for folder_path, class_name in class_data.items():
    # Loop melalui setiap file gambar dalam folder jenis data
    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg')):
            image_path = os.path.join(folder_path, filename)
            original_image = cv2.imread(image_path)

            target_size=256
            background_color=(255, 255, 255)
            
            # # Tentukan ukuran yang diinginkan
            # width = 512
            # height = 512

            # # Resize citra dengan ukuran baru
            # resized_image = cv2.resize(image, (width, height))
            # ...............................

                # Periksa apakah gambar sudah berbentuk persegi
            if original_image.shape[0] != original_image.shape[1]:
                # Jika tidak berbentuk persegi, ubah menjadi persegi
                square_size = max(original_image.shape[0], original_image.shape[1])
                square_image = np.ones((square_size, square_size, 3), dtype=np.uint8) * np.array(background_color)
                
                left = (square_size - original_image.shape[1]) // 2
                top = (square_size - original_image.shape[0]) // 2

                square_image[top:top + original_image.shape[0], left:left + original_image.shape[1]] = original_image
                original_image = square_image
            else:
                # Jika sudah berbentuk persegi, copy gambar agar tidak merubah gambar asli
                original_image = original_image.copy()

            # Ubah gambar ke format 8-bit unsigned integer (CV_8U)
            original_image = cv2.convertScaleAbs(original_image)

            # Resize citra dengan rasio aspek yang benar
            aspect_ratio = target_size / max(original_image.shape[0], original_image.shape[1])
            
            # Ubah gambar ke format RGB
            original_image_rgb = original_image

            # Resize gambar
            resized_image = cv2.resize(original_image_rgb, (int(target_size), int(target_size)), interpolation=cv2.INTER_AREA)

                        
            # ................................

            #hapus background
            output = remove(resized_image)

            # tes save file REMOVE BG ----------------
            nameFile = 'G:/ML PAN/DATASET/TES/rembg-' + filename
            cv2.imwrite(nameFile, output)
            # #---------------------------------------

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
            equalized_image_red = cv2.equalizeHist(gray_image[:,:,0])
            equalized_image_green = cv2.equalizeHist(gray_image[:,:,1])
            equalized_image_blue = cv2.equalizeHist(gray_image[:,:,2])

            # # Atur nilai gama /////////////////////////////////////////////////////////////////////////
            # gama = 0.7

            # Gabungkan kembali saluran grayscale dan alpha menjadi citra RGBA
            equalized_image_rgba = np.zeros_like(output)
            equalized_image_rgba[:, :, 0] = equalized_image_red
            equalized_image_rgba[:, :, 1] = equalized_image_green
            equalized_image_rgba[:, :, 2] = equalized_image_blue
            equalized_image_rgba[:, :, 3] = alpha

            # tes save file HE -----------------------
            nameFile = 'G:/ML PAN/DATASET/TES/HE-' + filename + 'finalHE.png'

            cv2.imwrite(nameFile, equalized_image_rgba)
            # #---------------------------------------

            # Ekstraksi fitur GLCM dari gambar
            glcm_features = compute_glcm_features(equalized_image_rgba)

            # CNN Pretrained Feature Extractor dari gambar
            CNN_features = extract_cnn_features(equalized_image_rgba)

            # Tambahkan fitur dan label ke list
            combined_features = np.concatenate((CNN_features, glcm_features))
            features.append(combined_features)
            labels.append(class_name)

            progress = progress+1
            print(progress/3, '%')


cnn_feat = CNN_features  # vektor panjang (512,)
glcm_feat = glcm_features  # vektor 20 nilai
combined_feat = np.concatenate((cnn_feat, glcm_feat))


# Buat DataFrame dari fitur dan label <<<
cnn_column_names = [f'cnn_feat_{i}' for i in range(len(cnn_feat))]
glcm_column_names = ['contrast_0', 'contrast_45', 'contrast_90', 'contrast_135',
                'dissimilarity_0', 'dissimilarity_45', 'dissimilarity_90', 'dissimilarity_135',
                'homogeneity_0', 'homogeneity_45', 'homogeneity_90', 'homogeneity_135',
                'energy_0', 'energy_45', 'energy_90', 'energy_135',
                'correlation_0', 'correlation_45', 'correlation_90', 'correlation_135',
                ]

all_column_names = cnn_column_names + glcm_column_names
data = pd.DataFrame(features, columns=all_column_names)
data['label'] = labels


# Tampilkan daftar direktori yang dipilih beserta labelnya
print("Direktori jenis yang dipilih:")
for folder_path, class_name in class_data.items():
    print(f"Folder: {folder_path}, Label: {class_name}")

# Simpan data dalam file CSV
data.to_csv('dataset_GLCM_CNN.csv', index=False)
