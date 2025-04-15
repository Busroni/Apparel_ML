import cv2
import os
from rembg import remove
from tkinter import Tk, filedialog

# Memasukkan jumlah jenis data
num_classes = 1

# Dictionary untuk menyimpan folder dan label
class_data = {}

# Loop melalui setiap jenis data
for class_idx in range(num_classes):
    # Memilih folder menggunakan GUI dialog
    Tk().withdraw()
    folder_path = filedialog.askdirectory(title=f"Pilih folder untuk jenis data {class_idx+1}")
    class_data[folder_path] = ''

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

            #hapus background
            output = remove(original_image)

            # tes save file REMOVE BG ----------------
            nameFile = 'G:/AI_PAN/DATASET/dataset_removebg/pants/' + filename
            cv2.imwrite(nameFile, output)
            # #---------------------------------------

            progress = progress+1
            print(progress/21, '%')

