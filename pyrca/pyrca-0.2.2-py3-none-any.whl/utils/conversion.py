import math
from .constants import *
from pyrca.properties.unit import Unit


def psi_to_mpa(psi):
    """
    Converts pressure from PSI to MPa.
    :param psi: The pressure in PSI
    :return: Pressure in MPa.
    """
    psi = psi / POUND_PER_KILOGRAM
    psi = psi * GRAVITY_METRIC
    psi = psi / math.pow(MILLIMETER_PER_INCH, 2)
    return psi


def mpa_to_psi(mpa):
    """
    Converts pressure from MPa to PSI
    :param mpa: Pressure in MPa
    :return: Pressure in PSI
    """
    mpa = mpa * POUND_PER_KILOGRAM
    mpa = mpa / GRAVITY_METRIC
    mpa = mpa * math.pow(MILLIMETER_PER_INCH, 2)
    return mpa


def mm_to_in(mm):
    """
    Converts length in millimeter to inches.
    :param mm: Length in millimeter
    :return: Length in inches
    """
    return mm / MILLIMETER_PER_INCH


def in_to_mm(inch):
    """
    Convertes length in inches to millimeter
    :param inch: Length in inches
    :return: Length in millimeter
    """
    return inch * MILLIMETER_PER_INCH


def linear_convert(distance: float, unit: Unit):
    """
    Converts a metric linear measurement automatically based on the unit given.
    :param distance: Distance in either mm
    :param unit: Unit set by the application
    :return: The converted distance.
    """
    if unit == Unit.ENGLISH:
        return mm_to_in(distance)
    else:
        return distance


def pressure_convert(pressure: float, unit: Unit):
    """
    Converts a metric pressure measurement automatically based on the unit given
    :param pressure: Pressure in MPa
    :param unit: Unit set by the application
    :return: The converted pressure.
    """
    if unit == Unit.ENGLISH:
        return mpa_to_psi(pressure)
    return pressure


def to_square_inches(area: float):
    """
    Converts area from square millimeter to square inches.
    :param area: Area in square millimeter.
    :return: Area in square inches.
    """
    return area / math.pow(MILLIMETER_PER_INCH, 2)


def to_square_millimeters(area: float):
    """
    Converts area from square inches to square millimeters.
    :param area: Area in square inches.
    :return: Area in square millimeters.
    """
    return area * math.pow(MILLIMETER_PER_INCH, 2)


def to_english_moment(moment_in_metric: float):
    """
    Converts N-mm to lb-ft.
    :param moment_in_metric: Moment in N-mm
    :return: Moment in lb-ft.
    """
    return moment_in_metric * POUND_PER_KILOGRAM / GRAVITY_METRIC / MILLIMETER_PER_INCH / 12
