import numpy as np
import os
import cv2


class SimpleDataSetLoader:
    def __init__(self, preprocessors=None):
        self.preprocessors = preprocessors

        if self.preprocessors is None:
            self.preprocessors = []

    def load(self, image_paths, verbose=1):
        data = []
        labels = []

        for (i, imagePath) in enumerate(image_paths):

            image = cv2.imread(imagePath)
            label = imagePath.split(os.path.sep)[-2]
            print("[INFO]{}".format(label))

            if self.preprocessors is not None:
                for p in self.preprocessors:
                    image = p.preprocess(image)
            data.append(image)
            labels.append(label)
            if verbose > 0 and i > 0 and (i + 1) % verbose == 0:
                print("[INFO] processed{}/{}".format(i + 1, len(image_paths)))
        return np.array(data), np.array(labels)
