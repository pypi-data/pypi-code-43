from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
import numpy as np

print("[INFO] loading image")
image = load_img("d.png")
image = img_to_array(image)
image = np.expand_dims(image,axis=0)

aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1, height_shift_range=0.1, shear_range=0.1, zoom_range=0.2,
                         horizontal_flip=True,fill_mode="nearest")

total = 0

print("[INFO] generating images")
imageGen = aug.flow(image, batch_size=1, save_to_dir="./output", save_prefix="image", save_format="png")

for image in imageGen:
    total += 1
    if total == 2000:
        break