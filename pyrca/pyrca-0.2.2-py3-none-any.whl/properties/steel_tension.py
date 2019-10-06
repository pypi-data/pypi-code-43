from ..utils.conversion import *
from .unit import *


class SteelTension:
    _total_area = 0
    _fs = 0
    _strain = 0

    def get_total_area(self, u: Unit = Unit.METRIC):
        """
        Gets the total area of steel.
        :param u: From the Unit class. English or Metric
        :return: Total area of tension steel.
        """
        if u == Unit.ENGLISH:
            return to_square_inches(self._total_area)
        return self._total_area

    def get_fs(self, u: Unit = Unit.METRIC):
        """
        Gets the steel stress.
        :param u: From the Unit class. English or Metric
        :return: Steel stress.
        """
        if u == Unit.ENGLISH:
            return mpa_to_psi(self._fs)
        return self._fs

    def set_total_area(self, total_area: float, u: Unit = Unit.METRIC):
        """
        Set the tension steel area.
        :param total_area: Area in square mm or square inches.
        :param u: From the Unit class. English or Metric
        """
        if u == Unit.ENGLISH:
            self._total_area = to_square_millimeters(total_area)
        else:
            self._total_area = total_area

    def set_fs(self, fs: float, u: Unit = Unit.METRIC):
        """
        Sets the steel stress.
        :param fs: Steel stress in MPa or PSI.
        :param u: From the Unit class. English or Metric
        """
        if u == Unit.ENGLISH:
            self._fs = psi_to_mpa(fs)
        else:
            self._fs = fs
