# import the necessary packages
from keras.utils import plot_model
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint
from keras.applications import VGG16
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from sklearn.preprocessing import LabelEncoder
from imutils import paths
import numpy as np
import progressbar
import random
import os

from clearviewai.serialize.hd5f_writer import HDF5DatasetWriter


def net_architecture(model, out_dir, filename):
    """Write the network architecture
    visualization graph to disk"""
    plot_model(model, to_file=filename, show_shapes=True)


def generate_images(file, out_dir, n=200):
    """generate images to output dir"""
    print("[INFO] loading image")
    image = load_img(file)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)

    aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1, height_shift_range=0.1, shear_range=0.1,
                             zoom_range=0.2,
                             horizontal_flip=True, fill_mode="nearest")

    total = 0

    print("[INFO] generating images")
    image_gen = aug.flow(image, batch_size=1, save_to_dir="./output", save_prefix="image", save_format="png")

    for image in image_gen:
        total += 1
        if total == n:
            break


def check_point(out_dir, best=False):
    # construct the callback to save only the *best* model to disk
    # based on the validation loss
    fname = os.path.sep.join([out_dir, "weights-{epoch:03d}-{val_loss:.4f}.hdf5"])
    if best:
        checkpoint = ModelCheckpoint(fname, monitor="val_loss", save_best_only=True, verbose=1)
    else:
        checkpoint = ModelCheckpoint(fname, monitor="val_loss", mode="min", save_best_only=True, verbose=1)
    return [checkpoint]


def extract_features(out_dir, image_paths,  bs=32, buffer_size=1000):
    print("[INFO] loading images")
    imagePaths = list(paths.list_images(image_paths))
    random.shuffle(imagePaths)

    # extract the class labels from the image paths then encode the
    # labels
    labels = [p.split(os.path.sep)[-2] for p in imagePaths]
    le = LabelEncoder()
    labels = le.fit_transform(labels)

    print("[INFO] loading network...")
    model = VGG16(weights="imagenet", include_top=False)
    # initialize the HDF5 dataset writer, then store the class label
    # names in the dataset
    dataset = HDF5DatasetWriter((len(imagePaths), 512 * 7 * 7),
                                out_dir, dataKey="features", bufSize=buffer_size)
    dataset.storeClassLabels(le.classes_)

    # initialize the progress bar
    widgets = ["Extracting Features: ", progressbar.Percentage(), " ",
               progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval=len(imagePaths),
                                   widgets=widgets).start()
    # loop over the images in patches
    for i in np.arange(0, len(imagePaths), bs):
        # extract the batch of images and labels, then initialize the
        # list of actual images that will be passed through the network
        # for feature extraction
        batchPaths = imagePaths[i:i + bs]
        batchLabels = labels[i:i + bs]
        batchImages = []
        # loop over the images and labels in the current batch
        for (j, imagePath) in enumerate(batchPaths):
            # load the input image using the Keras helper utility
            # while ensuring the image is resized to 224x224 pixels
            image = load_img(imagePath, target_size=(224, 224))
            image = img_to_array(image)
            # preprocess the image by (1) expanding the dimensions and
            # (2) subtracting the mean RGB pixel intensity from the
            # ImageNet dataset
            image = np.expand_dims(image, axis=0)
            image = imagenet_utils.preprocess_input(image)
            # add the image to the batch
            batchImages.append(image)
        # pass the images through the network and use the outputs as
        # our actual features
        batchImages = np.vstack(batchImages)
        features = model.predict(batchImages, batch_size=bs)
        # reshape the features so that each image is represented by
        # a flattened feature vector of the ‘MaxPooling2D‘ outputs
        features = features.reshape((features.shape[0], 512 * 7 * 7))
        # add the features and labels to our HDF5 dataset
        dataset.add(features, batchLabels)
        pbar.update(i)
    # close the dataset
    dataset.close()
    pbar.finish()




