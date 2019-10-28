import cv2
from copy import copy
import numpy as np
from sklearn import cluster


class Color:
    @staticmethod
    def mean_sdv_lab(img, channel=0):
        """
        Calc the mean an the standard desviation of a channel of a CIE-LAB image
        :param img: Image with three channels
        :param channel: 0 => all three, 1 => L , 2 => A, 3 => B
        :return:
        """
        img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

        return Color.mean_sdv(img_lab, channel)

    @staticmethod
    def mean_sdv_rgb(img, channel=0):
        """
        Calc the mean an the standard desviation of a channel of a RGB image
        :param img: Image with three channels
        :param channel: 0 => all three, 1 => L , 2 => A, 3 => B
        :return:
        """
        return Color.mean_sdv(img, channel)

    @staticmethod
    def mean_sdv_hsv(img, channel=0):
        """
        Calc the mean an the standard desviation of a channel of a HSV image
        :param img: Image with three channels
        :param channel: 0 => all three, 1 => L , 2 => A, 3 => B
        :return:
        """
        img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

        return Color.mean_sdv(img_lab, channel)

    @staticmethod
    def mean_sdv(img, channel=0):
        """
        @brief Calculate the mean and the starndard desviation of an image.

        :param img:
        :param channel:
        :return:
        """
        if channel != 0:
            if channel == 1:
                chann, _, _ = cv2.split(img)
            elif channel == 2:
                _, chann, _ = cv2.split(img)
            else:
                _, _, chann = cv2.split(img)

        else:
            chann = copy(img)

        return cv2.meanStdDev(chann)

    @staticmethod
    def dominant_colors(image: np.ndarray, mask: np.ndarray, n_colors: int,
                        random_start: int = 42):
        """
        @brief Get the dominants colors of an image.

        :param image:
        :param mask:
        :param n_colors:
        :param random_start:
        :return:
        """
        hue, saturation, value = cv2.split(image)

        train = []

        for x in range(0, hue.shape[0]):
            for y in range(0, hue.shape[1]):
                if mask[x][y] == 1:
                    if train is None:
                        train = np.array([hue[x][y], saturation[x][y], value[x][y]])
                    else:
                        train.append(np.array([hue[x][y], saturation[x][y], value[x][y]]))

        kmeans = cluster.KMeans(n_clusters=n_colors, random_state=random_start)
        clusters = kmeans.fit_predict(np.array(train))

        _, importance = np.unique(clusters, return_counts=True)

        importance = importance / sum(importance)

        return zip(kmeans.cluster_centers_, importance)

