import os
import cv2
import xml.etree.ElementTree as ET
import albumentations as A
from tqdm import tqdm

# Folder input
IMAGE_DIR = 'dataset/images'
ANNOT_DIR = 'dataset/annotations'

# Folder output
OUTPUT_IMAGE_DIR = 'augmented/images'
OUTPUT_ANNOT_DIR = 'augmented/annotations'

# Buat folder output kalau belum ada
os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_ANNOT_DIR, exist_ok=True)

# Augmentasi (untuk objek kecil)
transform = A.Compose([
    A.RandomScale(scale_limit=0.2, p=0.5),
    A.RandomCrop(width=224, height=224, p=0.5),
    A.HorizontalFlip(p=0.5),
    A.Rotate(limit=20, p=0.5),
    A.RandomBrightnessContrast(p=0.4),
    A.MotionBlur(p=0.2),
], bbox_params=A.BboxParams(format='pascal_voc', label_fields=['labels']))


#----------------------------------

def parse_pascal_voc(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    boxes = []
    labels = []

    for obj in root.findall('object'):
        name = obj.find('name').text
        labels.append(name)
        bbox = obj.find('bndbox')
        box = [
            int(bbox.find('xmin').text),
            int(bbox.find('ymin').text),
            int(bbox.find('xmax').text),
            int(bbox.find('ymax').text)
        ]
        boxes.append(box)
    
    return boxes, labels, root


def save_augmented_xml(original_root, boxes, labels, filename, width, height):
    for obj in original_root.findall('object'):
        original_root.remove(obj)

    for box, label in zip(boxes, labels):
        obj = ET.SubElement(original_root, 'object')
        ET.SubElement(obj, 'name').text = label
        bndbox = ET.SubElement(obj, 'bndbox')
        ET.SubElement(bndbox, 'xmin').text = str(int(box[0]))
        ET.SubElement(bndbox, 'ymin').text = str(int(box[1]))
        ET.SubElement(bndbox, 'xmax').text = str(int(box[2]))
        ET.SubElement(bndbox, 'ymax').text = str(int(box[3]))

    size = original_root.find('size')
    size.find('width').text = str(width)
    size.find('height').text = str(height)

    tree = ET.ElementTree(original_root)
    tree.write(os.path.join(OUTPUT_ANNOT_DIR, filename))


#----------------------------------

for img_name in tqdm(os.listdir(IMAGE_DIR)):
    if not img_name.endswith('.jpg'):
        continue

    img_path = os.path.join(IMAGE_DIR, img_name)
    annot_path = os.path.join(ANNOT_DIR, img_name.replace('.jpg', '.xml'))

    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    boxes, labels, xml_root = parse_pascal_voc(annot_path)

    try:
        transformed = transform(image=img, bboxes=boxes, labels=labels)
        transformed_img = transformed['image']
        transformed_boxes = transformed['bboxes']
        transformed_labels = transformed['labels']

        # Save image
        output_img_path = os.path.join(OUTPUT_IMAGE_DIR, f'aug_{img_name}')
        cv2.imwrite(output_img_path, transformed_img)

        # Save XML
        save_augmented_xml(xml_root, transformed_boxes, transformed_labels, f'aug_{img_name.replace(".jpg", ".xml")}', 224, 224)

    except Exception as e:
        print(f"❌ Failed on {img_name}: {e}")

#----------------------------------