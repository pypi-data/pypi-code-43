import cv2
import math
import numpy as np


class Contours:
    @staticmethod
    def area(contour):
        """
        @brief Calculates a contour area

        The function computes a contour area. Similarly to moments , the area is computed using the Green
        formula. The function will most certainly give a wrong
        results for contours with self-intersections.

        :param contour:
        :return:
        """
        return cv2.contourArea(contour)

    @staticmethod
    def perimeter(contour):
        """
        @brief Calculates a contour perimeter

        The function computes a closed contour perimeter.

        :param contour: Input vector of 2D points, stored in std::vector or Mat
        :return:
        """
        return cv2.arcLength(contour, True)

    @staticmethod
    def convex_hull(contour):
        """
        @brief Finds the convex hull of a point set.

        The functions find the convex hull of a 2D point set using the Sklansky's algorithm that has O(N logN)
        complexity in the current implementation on OpenCV.

        :param contour: Input 2D point set, stored in std::vector or Mat
        :return set of points:
        """
        return cv2.convexHull(contour)

    @staticmethod
    def convex_hull_perimeter(contour):
        """
        @brief Finds the perimeter of the convex-hull.

        :param contour:
        :return:
        """
        return Contours.perimeter(Contours.convex_hull(contour))

    @staticmethod
    def convex_hull_area(contour):
        """
        Calculates the area of the convex hull from the contour, using the same function that the area of any object.

        :param contour:
        :return:
        """
        return cv2.contourArea(Contours.convex_hull(contour))

    @staticmethod
    def bounding_box_area(contour):
        """
        @brief Calculates the area of the bounding box of the contour.

        :param contour:
        :return:
        """
        return Contours.major_axis(contour) * Contours.minor_axis(contour)

    @staticmethod
    def rectangularity(contour):
        """
        @brief Calculates the proportion between the real area of the contour and the bounding box

        The bounding box is the minimum rectangle that

        :param contour: 1 channel image
        :return:
        """
        return Contours.area(contour) / Contours.bounding_box_area(contour)

    @staticmethod
    def max_r(contour):
        """
        @brief Calculates the radius of the enclosing circle of the contour

        :param contour:
        :return:
        """
        (_, _), radius = cv2.minEnclosingCircle(contour)
        return radius

    @staticmethod
    def min_r(contour):
        """
        @brief Calculates the radius of the maximum inscribed circle of the contour

        :param contour:
        :return:
        """
        _, _, width, height = cv2.boundingRect(contour)
        width = int(width) * 2
        height = int(height) * 2
        raw_distance = np.empty((width, height), dtype=np.float32)
        for i in range(width):
            for j in range(height):
                raw_distance[i, j] = cv2.pointPolygonTest(contour, (j, i), True)
        _, maxVal, _, _ = cv2.minMaxLoc(raw_distance)
        return abs(maxVal)

    @staticmethod
    def major_axis(contour):
        """
        @brief Calculates the major axis of the enclosing ellipse of the contour

        :param contour:
        :return:
        """
        (_, _), (_, major), _ = cv2.fitEllipse(contour)

        return major

    @staticmethod
    def minor_axis(contour):
        """
        @brief Calculates the minor axis of the ellipse from the contour

        :param contour:
        :return:
        """
        (_, _), (minor, _), _ = cv2.fitEllipse(contour)
        return minor

    @staticmethod
    def orientation(contour):
        """
        @brief Find the angle orientation of the enclosing ellipse

        :param contour:
        :return:
        """

        (_, _), (_, _), angle = cv2.fitEllipse(contour)
        return angle

    @staticmethod
    def roundness(contour):
        """
        Circularity corrected by the aspect ratio

        ref : https://progearthplanetsci.springeropen.com/articles/10.1186/s40645-015-0078-x
        :param contour: 1 channel image
        :return:
        """
        return round(4 * Contours.area(contour) / (math.pi * Contours.major_axis(contour) * Contours.major_axis(contour)), 2)

    @staticmethod
    def circularity(contour):
        """
        @brief Calc the likeliness of an object to a circle

        :param contour:
        :return:
        """
        return round(4 * math.pi * Contours.area(contour) / (Contours.perimeter(contour) * Contours.perimeter(contour)),
                     2)

    @staticmethod
    def solidity(contour):
        """
        @brief Calc the proportion between the area of the contour and the convex-hull

        :param contour:
        :return:
        """

        return round(Contours.area(contour) / Contours.convex_hull_area(contour), 2)

    @staticmethod
    def sphericity(contour):
        """
        @brief Proportion between the major diagonal and the minor diagonal

        :param contour:
        :return:
        """

        return Contours.min_r(contour) / Contours.max_r(contour)

    @staticmethod
    def aspect_ratio(contour):
        """
        @brief Proportional relationship between its width and it's height
        :param contour:
        :return:
        """

        return round(Contours.major_axis(contour) / Contours.minor_axis(contour), 2)

    @staticmethod
    def area_equivalent_diameter(contour):
        """
        @brief The diamater of the real area of the contour
        :param contour:
        :return:
        """

        return math.sqrt((4 / math.pi) * Contours.area(contour))

    @staticmethod
    def perimeter_equivalent_diameter(contour):
        """
        @brief The diameter of the real perimeter of the contour
        ;param contour:
        """

        return Contours.area(contour) / math.pi

    @staticmethod
    def equivalent_ellipse_area(contour):
        """
        @brief The area of the equivalent ellipse
        :param contour:
        :return:
        """
        return math.pi * Contours.major_axis(contour) * Contours.minor_axis(contour)

    @staticmethod
    def compactness(contour):
        """
        @brief Proportion between area and the shape of the ellipse

        :param contour:
        :return:
        """
        return math.sqrt((4 / math.pi * Contours.area(contour)) / Contours.major_axis(contour))

    @staticmethod
    def convexity(contour):
        """
        @brief Calc the convexity of the contour

        The convexity is a measure of the curvature of an object. Is calc by the relation between the perimeter of
        the convex hull and the perimeter of the object.
        :param contour:
        :return:
        """
        return Contours.convex_hull_perimeter(contour) / Contours.perimeter(contour)

    @staticmethod
    def shape(contour):
        """
        Relation between perimeter and area. Calc the elongation of an object
        :param contour:
        :return:
        """
        return math.pow(Contours.perimeter(contour), 2) / Contours.area(contour)

    @staticmethod
    def r_factor(contour):
        return Contours.convex_hull_perimeter(contour) / (Contours.major_axis(contour) * math.pi)

    @staticmethod
    def eccentricity(contour):
        """
        @brief Calc how much the conic section deviates from being circular

        For any point of a conic section, the distance between a fixed point F and a fixed straight line l is always
        equal to a positive constant, the eccentricity. Is calculed by the relation between the two diagonals of the
        elipse.

        :param contour:
        :return:
        """
        ellipse = cv2.fitEllipse(contour)
        D = math.fabs((ellipse[0][0] - ellipse[1][0]))
        d = math.fabs(ellipse[0][1] - ellipse[1][1])

        return round(D / d, 2)

    @staticmethod
    def max_feret(contour):
        """
        The maximum distance between parallel tangents to the projection area of the contour
        :param contour:
        :return:
        """
        feret, _ = Contours._max_min_feret(contour)
        return feret

    @staticmethod
    def min_feret(contour):
        """
        The minimum distance between parallel tangents to the projection area of the contour
        :param contour:
        :return:
        """
        _, feret = Contours._max_min_feret(contour)
        return feret

    @staticmethod
    def elongation(contour):
        """
        Relation between maximum and minimum feret of the contour.
        :param contour:
        :return:
        """
        return Contours.max_feret(contour) / Contours.min_feret(contour)

    @staticmethod
    def hu_moments(contour):
        return cv2.HuMoments(cv2.moments(contour)).flatten()

    @staticmethod
    def center(contour):
        """
        @brief Calculate the centroid of a contour

        The centroid of a plane figure is the arithmetic mean of all the point in the figure. For calculate it we
        use the moments of the image ( see https://en.wikipedia.org/wiki/Image_moment).

        :param contour:
        :return:
        """
        m = cv2.moments(contour)
        cx = int(m['m10'] / m['m00'])
        cy = int(m['m01'] / m['m00'])

        return (cx, cy)

    @staticmethod
    def _max_min_feret(contour):
        """
        Helper method for calculation of maximum and minimum ferets based on convex hull of the contour.
        Based on C++ code: https://www.crisluengo.net/archives/408
        :param contour:
        :return:
        """
        convex_hull_contour = Contours.convex_hull(contour)
        min_feret = 999999
        max_feret = 0
        n = len(convex_hull_contour) - 1
        p0 = n
        p = 0
        q = 1

        while Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                            convex_hull_contour[Contours._next_point(q, n)][0]) > \
                Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                                        convex_hull_contour[q][0]):
            q = Contours._next_point(q, n)

        while p != p0:
            p = Contours._next_point(p, n)
            listq = [q]
            while Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                                          convex_hull_contour[Contours._next_point(q, n)][0]) > \
                    Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                                            convex_hull_contour[q][0]):
                q = Contours._next_point(q, n)
                listq.append(q)

            if Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                                       convex_hull_contour[Contours._next_point(q, n)][0]) == \
                    Contours._triangle_area(convex_hull_contour[p][0], convex_hull_contour[Contours._next_point(p, n)][0],
                                                                                  convex_hull_contour[q][0]):
                listq.append(Contours._next_point(q, n))

            for i in range(len(listq)):
                q = ((listq[i] - 1) % n) + 1
                d = math.sqrt((convex_hull_contour[p][0][0] - convex_hull_contour[q][0][0]) ** 2 +
                              (convex_hull_contour[p][0][1] - convex_hull_contour[q][0][1]) ** 2)
                if d > max_feret:
                    max_feret = d

            p3 = convex_hull_contour[p][0]
            for i in range(len(listq) - 2):
                p1 = convex_hull_contour[listq[i]][0]
                p2 = convex_hull_contour[listq[i + 1]][0]
                height = Contours._triangle_height(p1, p2, p3)

                if height < min_feret:
                    min_feret = height

        return max_feret, min_feret

    @staticmethod
    def _triangle_area(p1, p2, p3):
        """
        Helper method that calculates triangle area based on triangle vertices
        :param p1: First vertex of the triangle
        :param p2: Second vertex of the triangle
        :param p3: Third vertex of the triangle
        :return:
        """
        return ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])) / 2

    @staticmethod
    def _triangle_height(p1, p2, p3):
        """
        Helper method that calculates triangle height based on triangle vertices
        :param p1: First vertex of the triangle
        :param p2: Second vertex of the triangle
        :param p3: Third vertex of the triangle
        :return:
        """
        return ((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])) / \
               math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def _next_point(p, n):
        """
        Helper method that calculates next antipodal point
        :param p: previous point
        :param n: total number of points in a contour
        :return:
        """
        return p % n + 1
