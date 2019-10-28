from matplotlib import pyplot as plt
from copy import copy
import cv2
from uib_vfeatures.contours import Contours
import numpy as np


class Masks:

    @staticmethod
    def solidity(mask, screen=False):
        """
        Calculates the proportion between the area of the object in the mask and the convex-hull
        :param mask: 1 channel image
        :param screen:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        if screen:
            hull = cv2.convexHull(cnt, returnPoints=False)
            defects = cv2.convexityDefects(cnt, hull)
            mask_cp = copy(mask)
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                cv2.line(mask_cp, start, end, [100, 100, 100], 10)

            plt.imshow(mask_cp)
            plt.show()

        return Contours.solidity(cnt)

    @staticmethod
    def convex_hull_perimeter(mask):
        """
        @brief Finds the perimeter of the convex-hull.

        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.convex_hull_perimeter(cnt)

    @staticmethod
    def convex_hull_area(mask):
        """
        Calculates the area of the convex hull from the contour, using the same function that the area of any object.

        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.convex_hull_area(cnt)

    @staticmethod
    def bounding_box_area(mask, screen=False):
        """
        @brief Calculates the area of the bounding box of the contour.

        :param mask: 1 channel image
        :param screen: Boolean
        :return:
        """

        cnt = Masks.extract_contour(mask)

        if screen:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            mask_cp = copy(mask)
            cv2.drawContours(mask_cp, [box], -1, (100, 100, 100), 20)

            plt.imshow(mask_cp)
            plt.show()

        return Contours.bounding_box_area(cnt)

    @staticmethod
    def rectangularity(mask):
        """
        @brief Calculates the area of the bounding box of the contour.

        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.bounding_box_area(cnt)

    @staticmethod
    def min_r(mask):
        """
        @brief Calculates the minor radius of the ellipse from the contour
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.min_r(cnt)

    @staticmethod
    def max_r(mask):
        """
        @brief Calculates the radius of the enclosing circle of the contour
        :param mask:
        :return:
        """

        cnt = Masks.extract_contour(mask)

        return Contours.max_r(cnt)

    @staticmethod
    def feret(mask):
        """
        @brief Calculates the major diagonal of the enclosing ellipse of the contour
        :param mask:
        :return:
        """

        cnt = Masks.extract_contour(mask)

        return Contours.major_axis(cnt)

    @staticmethod
    def breadth(mask):
        """
        @brief Calculates the minor diagonal of the ellipse from the contour
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.minor_axis(cnt)

    @staticmethod
    def circularity(mask):
        """
        @brief Calc the likeliness of an object to a circle
        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.circularity(cnt)

    @staticmethod
    def roundness(mask):
        """
        Circularity corrected by the aspect ratio
        ref : https://progearthplanetsci.springeropen.com/articles/10.1186/s40645-015-0078-x
        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.roundness(cnt)

    @staticmethod
    def feret_angle(mask):
        """
        @brief Return the angle between the feret and the horizontal
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.orientation(cnt)

    @staticmethod
    def eccentricity(mask, screen=False):
        """
        @brief Calc how much the conic section deviates from being circular

        For any point of a conic section, the distance between a fixed point F and a fixed straight line l is always
        equal to a positive constant, the eccentricity. Is calculed by the relation between the two diagonals of the
        elipse.

        :param mask: 1 channel image
        :param screen:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        if screen:
            mask_cp = copy(mask)
            ellipse = cv2.fitEllipse(cnt)
            cv2.ellipse(mask_cp, ellipse, (100, 100, 100), 7)
            plt.imshow(mask_cp)
            plt.show()

        return Contours.eccentricity(cnt)

    @staticmethod
    def center(mask):
        """
        @brief Calculate the centroid of a contour

        The centroid of a plane figure is the arithmetic mean of all the point in the figure.

        :param mask:  1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.center(cnt)

    @staticmethod
    def sphericity(mask):
        """
        Proportion between the major and the minor feret

        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.sphericity(cnt)

    @staticmethod
    def aspect_ratio(mask):
        """
        @brief Proportional relationship between its width and it's height
        :param mask: 2D Vector, 1 channel image
        :return:
        """

        cnt = Masks.extract_contour(mask)

        return Contours.aspect_ratio(cnt)

    @staticmethod
    def area_equivalent_diameter(mask):
        """
        @brief The diamater of the real area of the contour

        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.area_equivalent_diameter(cnt)

    @staticmethod
    def perimeter_equivalent_diameter(mask):
        """
        @brief The diameter of the real perimeter of the contour

        :param mask: 2D Vector, 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.perimeter_equivalent_diameter(cnt)

    @staticmethod
    def equivalent_ellipse_area(mask):
        """
        The area of the equivalent ellipse
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.equivalent_ellipse_area(cnt)

    @staticmethod
    def compactness(mask):
        """
        Proportion between area and the shape of the ellipse
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.compactness(cnt)

    @staticmethod
    def area(mask):
        """
        Calc the area of the object of the mask

        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return cv2.contourArea(cnt)

    @staticmethod
    def convexity(mask):
        """
        @brief Calc the convexity of the contour

        The convexity is a measure of the curvature of an object. Is calc by the relation between the perimeter of
        the convex hull and the perimeter of the object.
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.convexity(cnt)

    @staticmethod
    def shape(mask):
        """
        Relation between perimeter and area. Calc the elongation of an object
        :param mask:
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.shape(cnt)

    @staticmethod
    def perimeter(mask):
        """
        Calc the perimeter of the object in the mask

        :param mask: 1 channel image
        :return:
        """
        cnt = Masks.extract_contour(mask)

        return Contours.perimeter(cnt)

    @staticmethod
    def extract_contour(mask):
        """
        @brief Finds contours in a binary image.

        The function retrieves contours from the binary image using the algorithm @cite Suzuki85 . The contours
        are a useful tool for shape analysis and object detection and recognition.

        @note Source image is not modified by this function.

        :param mask:
        :return:
        """
        if len(mask.shape) != 2:
            raise ValueError('Image is not a maks, multiples channels of color')

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 10:
            raise ValueError('Too many contours, image is not of a only object mask')

        if len(contours) == 0:
            raise ValueError("0 contours found: the image doesn't have any object")

        return contours[0]