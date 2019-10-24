# import the necessary packages
import glob

import h5py
from keras.models import load_model
from keras.utils import plot_model
from keras.callbacks import ModelCheckpoint
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from sklearn.preprocessing import LabelEncoder
import progressbar
import random
from clearviewai.primary.serialize.hd5f_writer import HDF5DatasetWriter
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from clearviewai.primary.processing.simple_processor import ImageToArray
from clearviewai.primary.processing.aspectresize import AspectAwareResize
from clearviewai.primary.processing.image_loader import SimpleDataSetLoader
from clearviewai.primary.architectures.fcheadnet import FCHeadNet
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import RMSprop
from keras.optimizers import SGD
from keras.applications import VGG16
from keras.layers import Input
from keras.models import Model
from imutils import paths
import numpy as np
import os


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


def extract_features(out_dir, image_paths,  bs=32, buffer_size=1000, arch='vgg16'):
    print("[INFO] loading images")
    imagePaths = list(paths.list_images(image_paths))
    random.shuffle(imagePaths)

    # extract the class labels from the image paths then encode the
    # labels
    labels = [p.split(os.path.sep)[-2] for p in imagePaths]
    le = LabelEncoder()
    labels = le.fit_transform(labels)

    print("[INFO] loading network...")
    if arch == 'vgg16':
        model = VGG16(weights="imagenet", include_top=False)
        fs = 512 * 7 * 7
    else:
        pass
    # initialize the HDF5 dataset writer, then store the class label
    # names in the dataset
    dataset = HDF5DatasetWriter((len(imagePaths), fs),
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


def ensemble(models_dir):
    # construct the path used to collect the models then initialize the
    # models list
    modelPaths = os.path.sep.join([models_dir, "*.h5"])
    modelPaths = list(glob.glob(modelPaths))
    models = []

    # loop over the model paths, loading the model, and adding it to
    # the list of models
    for (i, modelPath) in enumerate(modelPaths):
        print("[INFO] loading model {}/{}".format(i + 1,
        len(modelPaths)))
        models.append(load_model(modelPath))

    return models


def process_feature_vectors(vec_dir, train_ratio):
    """load feature vec file and return features"""
    db = h5py.File(vec_dir, "r")
    i = int(db["labels"].shape[0] * train_ratio)
    return db["features"][:i], db["labels"][:i]


def disp_net_layers(model):
    for (i, layer) in enumerate(model.layers):
        print("[INFO] {}\t{}".format(i, layer.__class__.__name__))


def transfer_learn(input_dir, out_dir, img_size, test_ratio,  basepochs=25,train_epochs=100, lrate=0.001, bs=32,  aug=False, arch='vgg16'):
    if aug:
        # construct the image generator for data augmentation
        aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1, height_shift_range=0.1,
                                 shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode="nearest")
    print("[INFO] loading images")
    imagePaths = list(paths.list_images(input_dir))

    classNames = [pt.split(os.path.sep)[-2] for pt in imagePaths]
    classNames = [str(x) for x in np.unique(classNames)]

    # grab the list of images in the dataset then randomly sample
    # indexes into the image paths list
    print("[INFO] sampling images...")
    imagePaths = np.array(list(paths.list_images(input_dir)))
    idxs = np.random.randint(0, len(imagePaths), size=(img_size,))
    imagePaths = imagePaths[idxs]

    s = AspectAwareResize(img_size, img_size)
    iap = ImageToArray()

    sdl = SimpleDataSetLoader(preprocessors=[s, iap])
    (data, labels) = sdl.load(imagePaths, verbose=500)
    data = data.astype("float") / 255.0

    # partition the data into training and testing splits using 75% of
    # the data for training and the remaining 25% for testing
    (trainX, testX, trainY, testY) = train_test_split(data, labels,
                                                        test_size=test_ratio, random_state=42)
    # convert the labels from integers to vectors
    trainY = LabelBinarizer().fit_transform(trainY)
    testY = LabelBinarizer().fit_transform(testY)

    # load the network, ensuring the head FC layer sets are left
    # off
    if arch == 'vgg16':
        baseModel = VGG16(weights="imagenet", include_top=False, input_tensor = Input(shape=(img_size, img_size, 3)))
        start_layer = 15
    # initialize the new head of the network, a set of FC layers
    # followed by a softmax classifier
    headModel = FCHeadNet.build(baseModel, len(classNames), 256)
    # place the head FC model on top of the base model -- this will
    # become the actual model we will train
    model = Model(inputs=baseModel.input, outputs=headModel)
    # loop over all layers in the base model and freeze them so they
    # will *not* be updated during the training process
    for layer in baseModel.layers:
        layer.trainable = False
    # compile our model (this needs to be done after our setting our
    # layers to being non-trainable
    print("[INFO] compiling model...")
    opt = RMSprop(lr=lrate)
    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics = ["accuracy"])
    # train the head of the network for a few epochs (all other
    # layers are frozen) -- this will allow the new FC layers to
    # start to become initialized with actual "learned" values
    # versus pure random
    print("[INFO] training head...")
    if aug:
        model.fit_generator(aug.flow(trainX, trainY, batch_size=bs), validation_data = (testX, testY), epochs=basepochs,
                            steps_per_epoch = len(trainX) // bs, verbose=1)
    else:
        model.fit(trainX, trainY, batch_size=bs, validation_data=(testX, testY), epochs=basepochs,
                            steps_per_epoch=len(trainX) // bs, verbose=1)
    # evaluate the network after initialization
    print("[INFO] evaluating after initialization...")
    predictions = model.predict(testX, batch_size=bs)
    print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1), target_names = classNames))
    # now that the head FC layers have been trained/initialized, lets
    # unfreeze the final set of CONV layers and make them trainable
    for layer in baseModel.layers[start_layer:]:
        layer.trainable = True

    # for the changes to the model to take affect we need to recompile
    # the model, this time using SGD with a *very* small learning rate
    print("[INFO] re-compiling model...")
    opt = SGD(lr=lrate)
    model.compile(loss="categorical_crossentropy", optimizer=opt, metrics = ["accuracy"])
    # train the model again, this time fine-tuning *both* the final set
    # of CONV layers along with our set of FC layers
    print("[INFO] fine-tuning model...")
    if aug:
        model.fit_generator(aug.flow(trainX, trainY, batch_size=bs), validation_data = (testX, testY), epochs = train_epochs,
                            steps_per_epoch = len(trainX) // bs, verbose = 1)
    else:
        model.fit(trainX, trainY, batch_size=bs, validation_data=(testX, testY),
                            epochs=train_epochs,
                            steps_per_epoch=len(trainX) // bs, verbose=1)
    # evaluate the network on the fine-tuned model
    print("[INFO] evaluating after fine-tuning...")
    predictions = model.predict(testX, batch_size=bs)
    print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1), target_names = classNames))
    # save the model to disk
    print("[INFO] serializing model...")
    model.save(out_dir)

