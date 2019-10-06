from math import *
from typing import List

"""
A pure python module to convet from Lambert to WGS84 positionning system
Highly inspired by https://github.com/yageek/lambert-java
Thank you Yannick Heinrich !
"""

__version__ = "1.0.0"


class LambertPoint:

    def __init__(self, x: float, y: float, z: float):
        """
        Initialize a Lambert point
        :param x: X component
        :param y: Y component
        :param z: Z component
        """
        self.x = x
        self.y = y
        self.z = z

    def getX(self) -> float:
        """
        Get the X value of the lambert point
        :return: float
        """
        return self.x

    def getY(self) -> float:
        """
        Get the X value of the lambert point
        :return: float
        """

        return self.y

    def getZ(self) -> float:
        """
        Get the Z value of the lambert point
        :return: float
        """
        return self.z

    def setX(self, x):
        """
        Set the X value of the lambert point
        """
        self.x = x

    def setY(self, y):
        """
        Set the Y value of the lambert point
        """
        self.y = y

    def setZ(self, z):
        """
        Set the Z value of the lambert point
        """
        self.z = z

    def translate(self, x: float, y: float, z: float):
        """
        Translate each (X,Y,Z) properties with the given parameters
        :param x: X value to add
        :param y: Y value to add
        :param z: Z value to add
        """
        self.x += x
        self.y += y
        self.z += z

    def toDegree(self):
        """
        Convert each (X,Y,Z) properties to degrees and return the current object
        :return: LambertPoint
        """
        self.x = self.x * 180 / pi
        self.y = self.y * 180 / pi
        self.z = self.z * 180 / pi
        return self


class LambertZone:
    """
    A fex constants for each type of Lambert calculation and zones
    """
    LAMBERT_N: List[float] = [0.7604059656, 0.7289686274, 0.6959127966, 0.6712679322, 0.7289686274, 0.7256077650]
    LAMBERT_C: List[float] = [11603796.98, 11745793.39, 11947992.52, 12136281.99, 11745793.39, 11754255.426]
    LAMBERT_XS: List[float] = [600000.0, 600000.0, 600000.0, 234.358, 600000.0, 700000.0]
    LAMBERT_YS: List[float] = [5657616.674, 6199695.768, 6791905.085, 7239161.542, 8199695.768, 12655612.050]

    M_PI_2: float = pi / 2.0
    DEFAULT_EPS: float = 1e-10
    E_CLARK_IGN: float = 0.08248325676
    E_WGS84: float = 0.08181919106

    A_CLARK_IGN: float = 6378249.2
    A_WGS84: float = 6378137.0
    LON_MERID_PARIS: int = 0
    LON_MERID_GREENWICH: float = 0.04079234433
    LON_MERID_IERS: float = 3.0 * pi / 180.0

    def __init__(self, value: int):
        """
        Initialize a Lambert zone to retrieve corresponding parameters
        :param value: Zone number
        """
        self.lambertZone = value

    def n(self):
        """
        Return N of the current Lambert zone
        :return: float
        """
        return self.LAMBERT_N[self.lambertZone]

    def c(self):
        """
        Return C of the current Lambert zone
        :return: float
        """
        return self.LAMBERT_C[self.lambertZone]

    def xs(self):
        """
        Return XS of the current Lambert zone
        :return: float
        """
        return self.LAMBERT_XS[self.lambertZone]

    def ys(self):
        """
        Return Ys of the current Lambert zone
        :return: float
        """
        return self.LAMBERT_YS[self.lambertZone]


"""
 Give friendly names to each lambert zone stored as predefined LambertZone objects
"""
LambertI = LambertZone(0)
LambertII = LambertZone(1)
LambertIII = LambertZone(2)
LambertIV = LambertZone(3)
LambertIIExtended = LambertZone(4)
Lambert93 = LambertZone(5)


def latitudeISOFromLat(lat: float, e: float):
    """
    Convert Lambert latitude to iso latitude
    :param lat: latitude
    :param e: ?
    :return: float
    """
    elt11 = pi / 4
    elt12 = lat / 2
    elt1 = tan(elt11 + elt12)

    elt21 = e * sin(lat)
    elt2 = pow((1 - elt21) / (1 + elt21), e / 2)

    return log(elt1 * elt2)


def latitudeFromLatitudeISO(latISo: float, e: float, eps: float):
    """
    Convert a ISO latitude to Lambert latitude
    :param latISo: Iso lat
    :param e: ?
    :param eps: ?
    :return: float
    """
    phi0 = 2 * atan(exp(latISo)) - LambertZone.M_PI_2
    phiI = 2 * atan(pow((1 + e * sin(phi0)) / (1 - e * sin(phi0)), e / 2) * exp(latISo)) - LambertZone.M_PI_2
    delta = abs(phiI - phi0)

    while delta > eps:
        phi0 = phiI
        phiI = 2 * atan(pow((1 + e * sin(phi0)) / (1 - e * sin(phi0)), e / 2) * exp(latISo)) - LambertZone.M_PI_2
        delta = abs(phiI - phi0)

    return phiI


def geographicToLambertAlg003(latitude, longitude, zone, lonMeridian, e):
    n = zone.n()
    C = zone.c()
    xs = zone.xs()

    ys = zone.ys()

    latIso = latitudeISOFromLat(latitude, e)

    eLatIso = exp(-n * latIso)

    nLon = n * (longitude - lonMeridian)

    x = xs + C * eLatIso * sin(nLon)
    y = ys - C * eLatIso * cos(nLon)

    return LambertPoint(x, y, 0)


def geographicToLambert(latitude, longitude, zone, lonMeridian, e):
    n = zone.n()
    C = zone.c()
    xs = zone.xs()
    ys = zone.ys()

    sinLat = sin(latitude)
    eSinLat = (e * sinLat)
    elt1 = (1 + sinLat) / (1 - sinLat)
    elt2 = (1 + eSinLat) / (1 - eSinLat)

    latIso = (1 / 2) * log(elt1) - (e / 2) * log(elt2)

    R = C * exp(-(n * latIso))

    LAMBDA = n * (longitude - lonMeridian)

    x = xs + (R * sin(LAMBDA))
    y = ys - (R * cos(LAMBDA))

    return LambertPoint(x, y, 0)


def lambertToGeographic(org, zone, lonMeridian, e, eps):
    n = zone.n()
    C = zone.c()
    xs = zone.xs()
    ys = zone.ys()

    x = org.getX()
    y = org.getY()

    R = sqrt((x - xs) * (x - xs) + (y - ys) * (y - ys))

    gamma = atan((x - xs) / (ys - y))

    lon = lonMeridian + gamma / n

    latIso = -1 / n * log(abs(R / C))

    lat = latitudeFromLatitudeISO(latIso, e, eps)

    return LambertPoint(lon, lat, 0)


def lambertNormal(lat, a, e):
    return a / sqrt(1 - e * e * sin(lat) * sin(lat))


def geographicToCartesian(lon, lat, he, a, e):
    N = lambertNormal(lat, a, e)

    pt = LambertPoint(0, 0, 0)

    pt.setX((N + he) * cos(lat) * cos(lon))
    pt.setY((N + he) * cos(lat) * sin(lon))
    pt.setZ((N * (1 - e * e) + he) * sin(lat))

    return pt


def cartesianToGeographic(org, meridien, a, e, eps):
    x = org.getX()
    y = org.getY()
    z = org.getZ()

    lon = meridien + atan(y / x)

    module = sqrt(x * x + y * y)

    phi0 = atan(z / (module * (1 - (a * e * e) / sqrt(x * x + y * y + z * z))))
    phiI = atan(z / module / (1 - a * e * e * cos(phi0) / (module * sqrt(1 - e * e * sin(phi0) * sin(phi0)))))
    delta = abs(phiI - phi0)
    while delta > eps:
        phi0 = phiI
        phiI = atan(z / module / (1 - a * e * e * cos(phi0) / (module * sqrt(1 - e * e * sin(phi0) * sin(phi0)))))
        delta = abs(phiI - phi0)

    he = module / cos(phiI) - a / sqrt(1 - e * e * sin(phiI) * sin(phiI))

    return LambertPoint(lon, phiI, he)


def convertToWGS84_Pt(org, zone):
    if zone == Lambert93:
        return lambertToGeographic(org, Lambert93, LambertZone.LON_MERID_IERS, LambertZone.E_WGS84,
                                   LambertZone.DEFAULT_EPS)
    else:
        pt1 = lambertToGeographic(org, zone, LambertZone.LON_MERID_PARIS, LambertZone.E_CLARK_IGN,
                                  LambertZone.DEFAULT_EPS)
        pt2 = geographicToCartesian(pt1.getX(), pt1.getY(), pt1.getZ(), LambertZone.A_CLARK_IGN,
                                    LambertZone.E_CLARK_IGN)

        pt2.translate(-168, -60, 320)

        # WGS84    refers    to    greenwich
        return cartesianToGeographic(pt2, LambertZone.LON_MERID_GREENWICH, LambertZone.A_WGS84, LambertZone.E_WGS84,
                                     LambertZone.DEFAULT_EPS)


def convertToLambert(latitude, longitude, zone):
    if zone == Lambert93:
        raise TypeError
    else:
        pt1 = geographicToCartesian(longitude - LambertZone.LON_MERID_GREENWICH, latitude, 0, LambertZone.A_WGS84,
                                    LambertZone.E_WGS84)

        pt1.translate(168, 60, -320)

        pt2 = cartesianToGeographic(pt1, LambertZone.LON_MERID_PARIS, LambertZone.A_WGS84, LambertZone.E_WGS84,
                                    LambertZone.DEFAULT_EPS)

        return geographicToLambert(pt2.getY(), pt2.getX(), zone, LambertZone.LON_MERID_PARIS, LambertZone.E_WGS84)


def convertToLambertByAlg003(latitude, longitude, zone):
    if zone == Lambert93:
        raise TypeError
    else:
        pt1 = geographicToCartesian(longitude - LambertZone.LON_MERID_GREENWICH, latitude, 0, LambertZone.A_WGS84,
                                    LambertZone.E_WGS84)

        pt1.translate(168, 60, -320)

        pt2 = cartesianToGeographic(pt1, LambertZone.LON_MERID_PARIS, LambertZone.A_WGS84, LambertZone.E_WGS84,
                                    LambertZone.DEFAULT_EPS)

        return geographicToLambertAlg003(pt2.getY(), pt2.getX(), zone, LambertZone.LON_MERID_PARIS, LambertZone.E_WGS84)


def convertToWGS84(x, y, zone):
    pt = LambertPoint(x, y, 0)
    return convertToWGS84_Pt(pt, zone)


def convertToWGS84Deg(x, y, zone):
    pt = LambertPoint(x, y, 0)
    return convertToWGS84_Pt(pt, zone).toDegree()

# if __name__ == '__main__':
#     Usage example :
#     print(str(Lambert93.n()))
#     pt = convertToWGS84Deg(780886, 6980743, Lambert93)
#     print("Point latitude:" + str(pt.getY()) + " longitude:" + str(pt.getX()))
