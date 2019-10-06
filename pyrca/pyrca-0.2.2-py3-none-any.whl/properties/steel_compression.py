from ..utils.conversion import *
from .unit import *

"""
Definition of the SteelCompression class.
"""


class SteelCompression:
    """
    Class for handling the compression steel reinforcement.
    """
    _total_area = 0  # Total area of steel in compression in square millimeters.
    _fs = 0  # Steel stress in MPa.
    _d_prime = 0  # Distance of centroid of compression steel to compression-most fiber of concrete.

    def get_d_prime(self, u: Unit = Unit.METRIC):
        """
        Gets distance between centroid of compression steel and
        compression most fiber.
        :param u: Unit
        :return: d'
        """
        if u == Unit.ENGLISH:
            return mm_to_in(self._d_prime)
        return self._d_prime

    def get_total_area(self, u: Unit = Unit.METRIC):
        """
        Gets the total compression steel area.
        :param u: Unit
        :return:
        """
        if u == Unit.ENGLISH:
            return to_square_inches(self._total_area)
        return self._total_area

    def get_fs(self, u: Unit = Unit.METRIC):
        """
        Gets the steel stress.
        :param u: Unit
        :return:
        """
        if u == Unit.ENGLISH:
            return mpa_to_psi(self._fs)
        return self._fs

    def set_d_prime(self, d_prime: float, u: Unit = Unit.METRIC):
        """
        Sets the distance between centroid of compression steel and compression most fiber.
        :param d_prime:
        :param u:
        :return:
        """
        if u == Unit.ENGLISH:
            self._d_prime = in_to_mm(d_prime)
        else:
            self._d_prime = d_prime

    def set_total_area(self, total_area: float, u: Unit = Unit.METRIC):
        """
        Sets the total area of compression steel.
        :param total_area:
        :param u:
        :return:
        """
        if u == Unit.ENGLISH:
            self._total_area = to_square_millimeters(total_area)
        else:
            self._total_area = total_area

    def set_fs(self, fs: float, u: Unit.METRIC):
        """
        Sets the compression steel stress.
        :param fs:
        :param u:
        :return:
        """
        if u == Unit.ENGLISH:
            self._fs = psi_to_mpa(fs)
        else:
            self._fs = fs
