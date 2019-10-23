import os

import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from keras.optimizers import SGD
from imutils import paths

from clearviewai.processing.monitor import TrainingMonitor
from clearviewai.utils.utils import check_point

from clearviewai.config import EPOCHS, BATCH_SIZE, LEARNING_RATE, VALIDATION_RATIO
from clearviewai.processing.aspectresize import AspectAwareResize
from clearviewai.processing.simple_processor import SimplePreprocessor, ImageToArray
from clearviewai.processing.image_loader import SimpleDataSetLoader
from keras.preprocessing.image import ImageDataGenerator


class Train:
    def __init__(self, data_dir, batch_size=BATCH_SIZE, nepochs=EPOCHS):
        self.image_paths = list(paths.list_images(data_dir))
        class_names = [pt.split(os.path.sep)[-2] for pt in self.image_paths]
        self.names = [str(x) for x in np.unique(class_names)]
        self.preprocessor = None
        self.iap = None
        self.data = None
        self.sdl = None
        self.trainX = None
        self.trainY = None
        self.valX = None
        self.valY = None
        self.model = None
        self.H = None
        self.bs = batch_size
        self.nepochs = nepochs
        self.labels = None

    def image_preprocessor(self, preprocessor_idx, image_size):
        if preprocessor_idx == 0:
            self.preprocessor = SimplePreprocessor(image_size, image_size)
        elif preprocessor_idx == 1:
            self.preprocessor = AspectAwareResize(image_size, image_size)

        if self.preprocessor is not None:
            self.iap = ImageToArray()
        self.sdl = sdl = SimpleDataSetLoader(preprocessors=[self.preprocessor, self.iap])

    def prepare_data(self, verbose=500, val_size=VALIDATION_RATIO):
        if self.sdl is not None:
            (data, self.labels) = self.sdl.load(self.image_paths, verbose)
            self.data = data.astype("float") / 255.0
            (self.trainX, self.valX, train_y, val_y) = \
                train_test_split(self.data, self.labels, test_size=val_size, random_state=42)
            self.trainY = LabelBinarizer().fit_transform(train_y)
            self.valY = LabelBinarizer().fit_transform(val_y)

    def compile_model(self, model, rate=LEARNING_RATE):
        print("[INFO] compiling model")
        opt = SGD(lr=rate)
        self.model = model
        self.model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])

    def train(self, vrbse=1, aug=False, cp=False, cp_dir=None, cp_best=False, live_monitor=False):
        print("[INFO] training the network")
        if cp:
            call_back = check_point(cp_dir, cp_best)
        else:
            call_back = None

        if live_monitor:
            # construct the set of callbacks
            figPath = os.path.sep.join([cp_dir, "{}.png".format( os.getpid())])
            jsonPath = os.path.sep.join([cp_dir, "{}.json".format(os.getpid())])
            call_back = [TrainingMonitor(figPath, jsonPath=jsonPath)]

        if aug:
            # construct the image generator for data augmentation
            data_aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1, height_shift_range=0.1,
                                          shear_range=0.2,
                                          zoom_range=0.2, horizontal_flip=True, fill_mode="nearest")
            self.H = self.model.fit_generator(aug.flow(self.trainX, self.trainY, batch_size=self.bs),
                                              validation_data=(self.valX, self.valY),
                                              steps_per_epoch=len(self.trainX) // self.bs, epochs=self.nepochs,
                                              verbose=vrbse, callbacks=call_back)

        else:
            self.H = self.model.fit(self.trainX, self.trainY,
                                    validation_data=(self.valX, self.valY), batch_size=self.bs, epochs=self.nepochs,
                                    callbacks=call_back, verbose=vrbse)

    def save_model(self, model_dir):
        print("[INFO] saving model")
        self.model.save(model_dir)

    def evaluate_model(self, filename):
        print("[INFO] evauating network")
        predictions = self.model.predict(self.valX, batch_size=self.bs)

        print(classification_report(self.valY.argmax(axis=1), predictions.argmax(axis=1), target_names=self.names))

        # plot the training loss and accuracy

        plt.style.use("ggplot")
        plt.figure()
        plt.plot(np.arange(0, self.nepochs), self.H.history["loss"], label="train_loss")
        plt.plot(np.arange(0, self.nepochs), self.H.history["val_loss"], label="val_loss")
        plt.plot(np.arange(0, self.nepochs), self.H.history["acc"], label="train_acc")
        plt.plot(np.arange(0, self.nepochs), self.H.history["val_acc"], label="val_acc")
        plt.title("Training Loss and Accuracy on DATASET")
        plt.xlabel("Epoch #")
        plt.ylabel("Loss/Accuracy")
        plt.legend()
        plt.savefig(filename)
