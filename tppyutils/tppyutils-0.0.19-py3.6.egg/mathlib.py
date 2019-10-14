#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions and class related with maths
"""

from __future__ import print_function, division, absolute_import

import math


class BaseVector(object):
    pass


class Vector2D(object):
    def __init__(self, x=1.0, y=1.0):
        self.x = None
        self.y = None

        if type(x) == list or type(x) == tuple:
            self.x = x[0]
            self.y = x[1]

        if type(x) == float or type(x) == int:
            self.x = x
            self.y = y

        self.magnitude = None

    def _add(self, value):
        if type(value) == float or type(value) == int:
            return Vector2D(self.x + value, self.y + value)

        if type(self) == type(value):
            return Vector2D(value.x + self.x, value.y + self.y)

        if type(value) == list:
            return Vector2D(self.x + value[0], self.y + value[1])

    def _sub(self, value):
        if type(value) == float or type(value) == int:
            return Vector2D(self.x - value, self.y - value)

        if type(self) == type(value):
            return Vector2D(self.x - value.x, self.y - value.y)

        if type(value) == list:
            return Vector2D(self.x - value[0], self.y - value[1])

    def _rsub(self, value):
        if type(value) == float or type(value) == int:
            return Vector2D(value - self.x, value - self.y - value)

        if type(self) == type(value):
            return Vector2D(value.x - self.x, value.y - self.y)

        if type(value) == list:
            return Vector2D(value[0] - self.x, value[1] - self.y)

    def _mult(self, value):
        if type(value) == float or type(value) == int:
            return Vector2D(self.x * value, self.y * value)

        if type(self) == type(value):
            return Vector2D(value.x * self.x, value.y * self.y)

        if type(value) == list:
            return Vector2D(self.x * value[0], self.y * value[1])

    def _divide(self, value):
        if type(value) == float or type(value) == int:
            return Vector2D(self.x / value, self.y / value)

        if type(self) == type(value):
            return Vector2D(value.x / self.x, value.y / self.y)

        if type(value) == list:
            return Vector2D(self.x / value[0], self.y / value[1])

    def __add__(self, value):
        return self._add(value)

    def __radd__(self, value):
        return self._add(value)

    def __sub__(self, value):
        return self._sub(value)

    def __rsub__(self, value):
        return self._sub(value)

    def __mul__(self, value):
        return self._mult(value)

    def __rmul__(self, value):
        return self._mult(value)

    def __call__(self):
        return [self.x, self.y]

    def __div__(self, value):
        return self._divide(value)

    def _reset_data(self):
        self.magnitude = None

    def normalize(self, in_place=False):
        if not self.magnitude:
            self.magnitude()

        vector = self._divide(self.magnitude)

        if in_place:
            self.x = vector.x
            self.y = vector.y
            self._reset_data()

        if not in_place:
            return vector

    def get_vector(self):
        return [self.x, self.y]

    def get_magnitude(self):
        self.magnitude = math.sqrt((self.x * self.x) + (self.y * self.y))
        return self.magnitude

    def get_distance(self, x=0.0, y=0.0):
        other = Vector2D(x, y)

        offset = self - other

        return offset.get_magnitude()


class Vector(object):
    def __init__(self, x=1.0, y=1.0, z=1.0):

        self.x = None
        self.y = None
        self.z = None

        x_test = x

        if type(x_test) == list or type(x_test) == tuple:
            self.x = x[0]
            self.y = x[1]
            self.z = x[2]

        if type(x_test) == float or type(x_test) == int:
            self.x = x
            self.y = y
            self.z = z

    def _add(self, value):
        if type(value) == float or type(value) == int:
            return Vector(self.x + value, self.y + value, self.z + value)

        if type(self) == type(value):
            return Vector(value.x + self.x, value.y + self.y, value.z + self.z)

        if type(value) == list:
            return Vector(self.x + value[0], self.y + value[1], self.z + value[2])

    def _sub(self, value):
        if type(value) == float or type(value) == int:
            return Vector(self.x - value, self.y - value, self.z - value)

        if type(self) == type(value):
            return Vector(self.x - value.x, self.y - value.y, self.z - value.z)

        if type(value) == list:
            return Vector(self.x - value[0], self.y - value[1], self.z - value[2])

    def _rsub(self, value):
        if type(value) == float or type(value) == int:
            return Vector(value - self.x, value - self.y - value, value - self.z)

        if type(self) == type(value):
            return Vector(value.x - self.x, value.y - self.y, value.z - self.z)

        if type(value) == list:
            return Vector(value[0] - self.x, value[1] - self.y, value[2] - self.z)

    def _mult(self, value):
        if type(value) == float or type(value) == int:
            return Vector(self.x * value, self.y * value, self.z * value)

        if type(self) == type(value):
            return Vector(value.x * self.x, value.y * self.y, value.z * self.z)

        if type(value) == list:
            return Vector(self.x * value[0], self.y * value[1], self.z * value[2])

    def __add__(self, value):
        return self._add(value)

    def __radd__(self, value):
        return self._add(value)

    def __sub__(self, value):
        return self._sub(value)

    def __rsub__(self, value):
        return self._sub(value)

    def __mul__(self, value):
        return self._mult(value)

    def __rmul__(self, value):
        return self._mult(value)

    def __call__(self):
        return [self.x, self.y, self.z]

    def get_vector(self):
        return [self.x, self.y, self.z]

    def list(self):
        return self.get_vector()


class BoundingBox(object):
    """
    Util class to work with bounding box
    """

    def __init__(self, bottom_corner_list=None, top_corner_list=None):
        """
        Constructor
        :param bottom_corner_list: list<float, float, float>, vector of bounding box bottom corner
        :param top_corner_list: list<float, float, float>, vector of bounding box top corner
        """

        self._create_bounding_box(bottom_corner_list, top_corner_list)

    def _create_bounding_box(self, bottom_corner_list, top_corner_list):
        """
        Initializes bounding box
        :param bottom_corner_list: list<float, float, float>, vector of bounding box bottom corner
        :param top_corner_list: list<float, float, float>, vector of bounding box top corner
        """

        self.min_vector = [bottom_corner_list[0], bottom_corner_list[1], bottom_corner_list[2]]
        self.max_vector = [top_corner_list[0], top_corner_list[1], top_corner_list[2]]
        self.opposite_min_vector = [top_corner_list[0], bottom_corner_list[1], top_corner_list[2]]
        self.opposite_max_vector = [bottom_corner_list[0], top_corner_list[1], bottom_corner_list[2]]

    def get_center(self):
        """
        Returns the center of the bounding box in a list
        :return: list<float, float, float>
        """

        return get_mid_point(self.min_vector, self.max_vector)

    def get_ymax_center(self):
        """
        Returns the top center of the bounding box in a list
        :return: list<float, float, float>
        """

        return get_mid_point(self.max_vector, self.opposite_max_vector)

    def get_ymin_center(self):
        """
        Returns the bottom center of the bounding box in a list
        :return: list<float, float, float>
        """

        return get_mid_point(self.min_vector, self.opposite_min_vector)

    def get_size(self):
        """
        Returns the size of the bounding box
        :return: float
        """

        return get_distance(self.min_vector, self.max_vector)


def is_equal(x, y, tolerance=0.000001):
    """
    Checks if 2 float values are equal withing a given tolerance
    :param x: float, first float value to compare
    :param y: float, second float value to compare
    :param tolerance: float, comparison tolerance
    :return: bool
    """

    return abs(x-y) < tolerance


def lerp(start, end, alpha):
    """
    Computes a linear interpolation between two values
    :param start: start value to interpolate from
    :param end:  end value to interpolate to
    :param alpha: how far we want to interpolate (0=start, 1=end)
    :return: float, result of the linear interpolation
    """

    return start + alpha * (end - start)


def clamp(number, min_value, max_value):
    """
    Clamps a number between two values
    :param number: number, value to clamp
    :param min_value: number, maximum value of the number
    :param max_value: number, minimum value of the number
    :return: variant, int || float
    """

    return max(min(number, max_value), min_value)


def roundup(number, to):
    """
    Round up a number
    :param number: number to roundup
    :param to: number, mas value to roundup
    :return: variant, int || float
    """

    return int(math.ceil(number / to)) * to


def sign(value):
    """
    Returns the sign of the given value
    :param value: float
    :return: -1 of the value is negative; 1 if the value is positive; 0 if the value is zero
    """

    return value and (1, -1)[value < 0]


def get_range_percentage(min_value, max_value, value):
    """
    Returns the percentage value along a line from min_vlaue to max_value that value is
    :param min_value: float, minimum value
    :param max_value: float, maximum value
    :param value: float, input value
    :return: Percentage (from 0.0 to 1.0) between the two values where input value is
    """

    return (value - min_value) / (max_value - min_value)


def map_range_clamped(value, in_range_a, in_range_b, out_range_a, out_range_b):
    """
    Returns value mapped from one range into another where the value is clamped to the input range
    For example, 0.5 normalized from the range 0:1 to 0:50 would result in 25
    :param value: float
    :param in_range_a: float
    :param in_range_b: float
    :param out_range_a: float
    :param out_range_b: float
    :return: float
    """

    clamped_percentage = clamp(get_range_percentage(in_range_a, in_range_b, value), 0.0, 1.0)
    return lerp(out_range_a, out_range_b, clamped_percentage)


def map_range_unclamped(value, in_range_a, in_range_b, out_range_a, out_range_b):
    """
    Returns value mapped from one range into another where the value
    For example, 0.5 normalized from the range 0:1 to 0:50 would result in 25
    :param value: float
    :param in_range_a: float
    :param in_range_b: float
    :param out_range_a: float
    :param out_range_b: float
    :return: float
    """

    clamped_percentage = get_range_percentage(in_range_a, in_range_b, value)
    return lerp(out_range_a, out_range_b, clamped_percentage)


def bounding_box_half_values(bbox_min, bbox_max):
    """
    Returns the values half way between max and min XYZ given tuples
    :param bbox_min: tuple, contains the minimum X,Y,Z values of the mesh bounding box
    :param bbox_max: tuple, contains the maximum X,Y,Z values of the mesh bounding box
    :return: tuple(int, int, int)
    """

    min_x, min_y, min_z = bbox_min
    max_x, max_y, max_z = bbox_max
    half_x = (min_x + max_x) * 0.5
    half_y = (min_y + max_y) * 0.5
    half_z = (min_z + max_z) * 0.5

    return half_x, half_y, half_z


def snap_value(input, snap_value):
    """
    Returns snap value given an input and a base snap value
    :param input: float
    :param snap_value: float
    :return: float
    """

    return round((float(input)/snap_value)) * snap_value


def check_vector(vector):
    """
    Returns new Vector object from the given vector
    :param vector: variant, list<float, float, float> || Vector
    :return: Vector
    """

    if isinstance(vector, Vector):
        return vector

    return Vector(vector[0], vector[1], vector[2])


def check_vector_2d(vector):
    """
    Returns new Vector2D object from the given vector
    :param vector: variant, list<float, float> || Vector
    :return: Vector
    """

    if isinstance(vector, Vector2D):
        return vector

    return Vector(vector[0], vector[1])


def get_distance(vector1, vector2):
    """
    Returns the distance between two vectors
    :param vector1: list<float, float, float>, vector
    :param vector2: list<float, float, float>, vector
    :return: float
    """

    v1 = check_vector(vector1)
    v2 = check_vector(vector2)
    v = v1 - v2
    dst = v()

    return math.sqrt((dst[0] * dst[0]) + (dst[1] * dst[1]) + (dst[2] * dst[2]))


def get_distance_2d(vector1_2d, vector2_2d):
    """
    Returns the distance between two 2D vectors
    :param vector1_2d: Vector2D
    :param vector2_2d: Vector2D
    :return: float, distance between the two 2D vectors
    """

    v1 = check_vector_2d(vector1_2d)
    v2 = check_vector_2d(vector2_2d)

    v = v1 - v2
    dst = v()

    return math.sqrt(dst[0] * dst[0]) + (dst[1] * dst[1])


def get_dot_product(vector1, vector2):
    """
    Returns the dot product of the two vectors
    :param vector1: Vector
    :param vector2: Vector
    :return: float, dot product between the two vectors
    """

    v1 = check_vector(vector1)
    v2 = check_vector(vector2)
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)


def get_dot_product_2d(vector1_2d, vector2_2d):
    """
    Returns the dot product of the two vectors
    :param vector1_2d: Vector2D
    :param vector2_2d: Vector2D
    :return: float, dot product between the two vectors
    """

    v1 = check_vector(vector1_2d)
    v2 = check_vector(vector2_2d)

    return (v1.x * v2.x) + (v1.y * v2.y)


def get_mid_point(vector1, vector2):
    """
    Get the mid vector between 2 vectors
    :param vector1: list<float, float, float>
    :param vector2: list<float, float, float>
    :return: list<float, float, float>, midpoint vector between vector1 and vector2
    """

    values = list()
    for i in range(0, 3):
        values.append(get_average([vector1[i], vector2[i]]))

    return values


def get_average(numbers):
    """
    Returns the average value of the given numbers list
    :param numbers: list<float>, list of the floats to get average from
    :return: float, average of the floats in numbers list
    """

    total = 0.0
    for num in numbers:
        total += num

    return total / len(numbers)


def get_axis_vector(axis_name, offset=1):
    """
    Returns axis vector from its name
    :param axis_name: name of the axis ('X', 'Y' or 'Z')
    :param offset: float, offset to the axis, by default is 1
    :return: list (1, 0, 0) = X | (0, 1, 0) = Y | (0, 0, 1) = Z
    """

    if axis_name in ['X', 'x']:
        return offset, 0, 0
    elif axis_name in ['Y', 'y']:
        return 0, offset, 0
    elif axis_name in ['Z', 'z']:
        return 0, 0, 1


def fade_sine(percent_value):
    input_value = math.pi * percent_value

    return math.sin(input_value)


def ade_cosine(percent_value):
    percent_value = math.pi * percent_value

    return (1 - math.cos(percent_value)) * 0.5


def fade_smoothstep(percent_value):
    return percent_value * percent_value * (3 - 2 * percent_value)


def fade_sigmoid(percent_value):
    if percent_value == 0:
        return 0

    if percent_value == 1:
        return 1

    input_value = percent_value * 10 + 1

    return (2 / (1 + (math.e**(-0.70258 * input_value)))) - 1
