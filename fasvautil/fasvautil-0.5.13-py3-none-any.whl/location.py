# -*- coding: utf-8 -*-
# Copyright (c) 2019 by Lars Klitzke, Lars.Klitzke@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import logging
import os
import ssl
import subprocess
import time
import xml
from decimal import Decimal
from urllib.parse import urlencode

import numpy as np
import utm
from fastcache import lru_cache
from numba import njit
from overpy import Overpass
from overpy.exception import OverpassGatewayTimeout
from utm import OutOfRangeError
from utm.conversion import K0, M1, R, P2, P3, P4, P5, _E, E, E_P2, zone_number_to_central_longitude


class UnknownWayException(BaseException):
    pass


def format_float(value, decimals):
    """
    Format the given float value as str with the specified number of decimal places.
    Args:
        value (float|list[float]|tuple[float, ...]):  The value to format as string
        decimals (int): The number of decimal places

    Returns:
        str: The float value was string.
    """
    if not isinstance(value, (list, tuple, np.ndarray)):
        value = [value]

    return [format(v, ".{}f".format(decimals)) if v is not None else None for v in value]


def to_latlon(easting, northing, zone_number, zone_letter=None, northern=None, strict=True):
    """
    This function convert a list of UTM coordinates into Latitude and Longitude

    Args:

        easting (list[float]): Easting value of UTM coordinate
        northing (list[float]): Northing value of UTM coordinate
        zone number (int): Zone Number is represented with global map numbers of an UTM Zone Numbers Map.
                           More information see utmzones [1]_
        zone_letter (str): Zone Letter can be represented as string values. Where UTM Zone Designators
                           can be accessed in [1]_

        northern (bool): You can set True or False to set this parameter. Default is None


   .. _[1]: http://www.jaworski.ca/utmzones.htm

    """
    if not zone_letter and northern is None:
        raise ValueError('either zone_letter or northern needs to be set')

    elif zone_letter and northern is not None:
        raise ValueError('set either zone_letter or northern, but not both')

    if strict:
        valid_coordinates = np.all((easting > 100000, easting < 1000000, northing >= 0, northing <= 10000000), axis=0)

        easting = easting[valid_coordinates]
        northing = northing[valid_coordinates]

    if not 1 <= zone_number <= 60:
        raise OutOfRangeError('zone number out of range (must be between 1 and 60)')

    if zone_letter:
        zone_letter = zone_letter.upper()

        if not 'C' <= zone_letter <= 'X' or zone_letter in ['I', 'O']:
            raise OutOfRangeError('zone letter out of range (must be between C and X)')

        northern = (zone_letter >= 'N')

    x = easting - 500000
    y = northing

    if not northern:
        y -= 10000000

    m = y / K0
    mu = m / (R * M1)

    p_rad = (mu +
             P2 * np.sin(2 * mu) +
             P3 * np.sin(4 * mu) +
             P4 * np.sin(6 * mu) +
             P5 * np.sin(8 * mu))

    p_sin = np.sin(p_rad)
    p_sin2 = p_sin * p_sin

    p_cos = np.cos(p_rad)

    p_tan = p_sin / p_cos
    p_tan2 = p_tan * p_tan
    p_tan4 = p_tan2 * p_tan2

    ep_sin = 1 - E * p_sin2
    ep_sin_sqrt = np.sqrt(1 - E * p_sin2)

    n = R / ep_sin_sqrt
    r = (1 - E) / ep_sin

    c = np.power(_E * p_cos, 2)
    c2 = c * c

    d = x / (n * K0)
    d2 = d * d
    d3 = d2 * d
    d4 = d3 * d
    d5 = d4 * d
    d6 = d5 * d

    latitude = (p_rad - (p_tan / r) *
                (d2 / 2 -
                 d4 / 24 * (5 + 3 * p_tan2 + 10 * c - 4 * c2 - 9 * E_P2)) +
                d6 / 720 * (61 + 90 * p_tan2 + 298 * c + 45 * p_tan4 - 252 * E_P2 - 3 * c2))

    longitude = (d -
                 d3 / 6 * (1 + 2 * p_tan2 + c) +
                 d5 / 120 * (5 - 2 * c + 28 * p_tan2 - 3 * c2 + 8 * E_P2 + 24 * p_tan4)) / p_cos

    return (np.degrees(latitude),
            np.degrees(longitude) + zone_number_to_central_longitude(zone_number))


class OSM(object):
    """
    An abstraction layer for road information determination.

    It will either use the `overpy` package to query the Overpass server or use the local interface if this software
    runs on host with an Overpass server.

    """
    CONFIG_SECTION = "Overpass"

    CONFIG_OPTION_BIN_DIR = "bin-dir"

    CONFIG_OPTION_URL = "url"

    def __init__(self, **kwargs):

        self.__cmd = None

        if self.CONFIG_OPTION_URL in kwargs:
            # the user wants to connect to an external server
            if 'context' in kwargs:
                self.Overpass = Overpass(url=kwargs[self.CONFIG_OPTION_URL], context=kwargs['context'])
            else:
                self.Overpass = Overpass(url=kwargs[self.CONFIG_OPTION_URL])

        elif self.CONFIG_OPTION_BIN_DIR in kwargs:
            # the user wants to query a local osm instance
            self.__cmd = os.path.join(kwargs[self.CONFIG_OPTION_BIN_DIR], "osm3s_query")

            self.Overpass = Overpass()
        else:
            raise RuntimeError('Option {} or {} missing in Section {} is missing'.format(self.CONFIG_OPTION_URL,
                                                                                         self.CONFIG_OPTION_BIN_DIR,
                                                                                         self.CONFIG_SECTION))

    def _query_osm(self, request):
        """
        Query the OSM instance

        Args:
            request (str): Request to send

        Returns:

            The result of the OSM server

        Note:
            If you have passed the OSM_OPTION_URL on initialization, the external
            server will be queried. Otherwise you have to define the option
            CONFIG_OPTION_BIN_DIR in the configuration. Then, it is assumed that
            that a local osm instance is available which will be queried instead.

        """

        if not self.__cmd:
            while True:
                try:
                    # query the external server
                    return self.Overpass.query(urlencode({'data': request}))
                except (TimeoutError, OverpassGatewayTimeout):
                    logging.warning('A Timeout occurred - retry query')
                    time.sleep(1)
                except xml.sax._exceptions.SAXParseException:
                    return None

        else:

            encoded_request = request.encode('utf-8')

            # query the local server
            with open(os.devnull, 'w') as devnull:
                process = subprocess.run('{cmd}'.format(cmd=self.__cmd), input=encoded_request,
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

            # get the stdout of the subprocess
            result = process.stdout

            # take care that the osm server send a reply
            if result:
                if "out:json" in request:
                    return self.Overpass.parse_json(result, 'utf-8')
                else:
                    return self.Overpass.parse_xml(result, 'utf-8')

    @lru_cache(maxsize=None, typed=False)
    def query(self, request):

        if request:
            return self._query_osm(request)


class Location(object):
    """
    Represents a location with a deviation
    """

    def __init__(self, position, deviation=(0,0)):
        """

        Args:
            position (tuple[float, float]): The position
            deviation (tuple[float, float]): The position error
        """

        self.position = position
        self.deviation = deviation

    def __repr__(self):
        return "{}, ({})".format(",".join(format_float(self.position, 6)),
                                 ",".join(format_float(self.deviation, 2)))

    def valid(self):
        """
        Checks if the location is valid.

        Returns:
            bool: Whether the location is valid or not.
        """
        return self.position[0] is not None and self.position[1] is not None


class GPSLocation(Location):
    @property
    def latitude(self):
        return self.position[0]

    @property
    def longitude(self):
        return self.position[1]

    def as_utm(self):
        """
        Return the UTM location.

        Returns:
            UTMLocation: The UTM location of this GPS location.
        """
        easting, northing, zn, zl = utm.from_latlon(self.latitude, self.longitude)

        return UTMLocation(zone_number=zn, zone_letter=zl, position=(easting, northing), deviation=self.deviation)

    @classmethod
    def from_list(cls, gpslocations, weights):
        """
        Estimate the standard deviation of the list of `GPSLocation`s in meters.

        Args:
            gpslocations (np.ndarray):   A list of GPS positions.
            weights (list[float]|np.ndarray):       A list of weights for each location

        Returns:
            GPSLocation:    The mean GPS location
        """

        if gpslocations.size != 0:
            # get the utm zone
            _, _, zone_number, zone_letter = utm.from_latlon(latitude=gpslocations[0][0], longitude=gpslocations[0][1])

            if isinstance(weights, list):
                weights = np.asarray(weights)

            # estimate the mean location
            gps_mean = weighted_position(gpslocations, weights)
            #
            # gps_mean = np.mean(gpslocations, axis=0)

            # convert to UTM
            mean_e, mean_n, _, _ = utm.from_latlon(latitude=gps_mean[0], longitude=gps_mean[1])

            # estimate the distance
            locs = []

            for loc in gpslocations:
                e, n, _, _ = utm.from_latlon(latitude=loc[0], longitude=loc[1])
                locs.append(np.array([e, n]))

            locs = np.asarray(locs)

            locs - np.asarray([mean_e, mean_n])

            return GPSLocation(position=gps_mean, deviation = np.std(locs, axis=0))


class InvalidUTMLocation(RuntimeError):
    pass


class UTMLocation(Location):

    def __init__(self, zone_number=None, zone_letter=None, zone=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if zone is not None:

            try:
                self.zone_number = zone[0]
                self.zone_letter = zone[1]
            except IndexError:
                raise InvalidUTMLocation('The zone parameter must be an iterable with zone number and letter')
        elif zone_number is not None and zone_letter is not None:
            self.zone_number = zone_number
            self.zone_letter = zone_letter
        else:
            raise InvalidUTMLocation('Either specify the UTM zone as number and letter or as a tuple')

    @property
    def zone(self):
        return self.zone_number, self.zone_letter

    @property
    def easting(self):
        return self.position[0]

    @property
    def northing(self):
        return self.position[1]

    def as_gps(self):
        """
        Convert the UTM location to a GPS location

        Returns:
            GPSLocation: The GPS location
        """

        latitude, longitude = utm.to_latlon(easting=self.easting, northing=self.northing,
                                            zone_number=self.zone_number, zone_letter=self.zone_letter)

        return GPSLocation(position=(latitude, longitude), deviation=self.deviation)


def weighted_position(particles, weights):
    """
    Estimate the weighted mean position of the particles.

    Args:
        particles (np.ndarray): The particle positions as a N*2 array
        weights (np.ndarray):   The particle weights as a 1D array

    Returns:
        np.ndarray: The weighted mean particle location

    """
    weights = weights / np.sum(weights)

    return particles.T.dot(weights.ravel())


def gps_utm_location(gpslocations):
    """
    Convert a list of GPS location to its UTM representation.

    Args:
        gpslocations (list[GPSLocation]|list[tuple[float, float]]): A list of GPS locations.

    Returns:
        return list[UTMLocation]: UTM locations

    """
    utmlocs = []

    if isinstance(gpslocations[0], GPSLocation):
        for loc in gpslocations:
            utmlocs.append(loc.as_utm())
    else:
        for latitude, longitude in gpslocations:
            x, y, _, _ = utm.from_latlon(latitude=latitude, longitude=longitude)

            utmlocs.append(np.asarray([x, y]))

    return np.asarray(utmlocs)


class CachedOSMQuery(object):

    def __init__(self, osm):

        # The location used for the last search
        self._last_location = None  # type: UTMLocation

        # The last search radius
        self._last_search_radius = None

        # The ways found
        self._last_result = []

        # The OSM handler to use for querying the OpenStreetMap server
        self._osm = osm

        # Variables for statistics: hit and count
        self._queries_count = 0

        self._queries_hit = []

        # Query durations
        self._queries_durations = []

        # The query radius used for searching
        self._queries_radius = []

    def _query(self, request):
        """
        Query the OpenStreetMap server.

        Args:
            request (str): The request to send to the OpenStreetMap server.

        Returns:
            list[Overpy.Nodes]|None: A list of nodes or None if no ways found.
        """
        result = self._osm.query(request)

        if result:
            return result.get_ways()
        else:
            return None

    def statistics(self):

        total_queries = self._queries_count

        total_hits = np.sum(np.asarray(self._queries_hit))

        total_time_saved = np.sum(np.multiply(np.asarray(self._queries_hit), np.asarray(self._queries_durations)))

        return self._queries_durations, self._queries_radius, (total_queries, total_hits, total_time_saved)

    @property
    def last_result(self):
        return self._last_result

    def _search(self, location, radius, *args, **kwargs):
        """
        Should be implemented by the child class.

        Args:
            location (GPSLocation): The GPS location as reference search point
            radius:                 The search radius
            *args:
            **kwargs:

        Returns:
            tuple[float, any]: The search radius and some arbitrary result.
        """
        raise NotImplementedError()

    def search(self, location, radius=100, cache_threshold=0.8, *args, **kwargs):
        """
        Get the OpenStreetMap nodes around the given location within the given radius

        This function will increment the radius if no ways are found within the given radius.

        Args:
            location (GPSLocation): The GPS location
            radius (int)            The search radius. By default, 100 meter
            cache_threshold (float):The cache threshold, i.e. position distance to latest search
            *args:
            **kwargs:

        Returns:
            list[any]: The nodes around the given location
        """

        # increment the query counter
        self._queries_count += 1

        utmlocation = location.as_utm()

        if self._last_location is not None:
            # check if the distance travelled is so small that we can simply return the last found ways.
            # Therefore, use the last search radius. If the distance between the last and the current location is
            # smaller then the half search radius, we just return the last ways found.
            distance_travelled = np.linalg.norm(np.asarray(utmlocation.position, dtype=np.float64) -
                                                np.asarray(self._last_location.position, dtype=np.float64))

            if distance_travelled < (self._last_search_radius * cache_threshold) and self._last_result:
                # increment the hit of the last query
                self._queries_hit[-1] += 1

                return self._last_result

        start_time = time.time()
        self._last_search_radius, result = self._search(location, int(radius), *args, **kwargs)
        end_time = time.time()

        self._queries_durations.append(end_time - start_time)

        # cache the found ways
        self._last_result = result

        # save the location
        self._last_location = utmlocation

        # add search radius
        self._queries_radius.append(self._last_search_radius)

        # indicate that we've
        self._queries_hit.append(0)

        # return the found entries
        return result


class StreetFinder(CachedOSMQuery):
    """
    Finds the nearest OpenStreetMap nodes around a given location
    """

    QUERY = """
    [timeout:60];
    (
        way["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|motorway_link|trunk_link|primary_link|secondary_link|motorway_junction|living_street"](around:{dist}, {lat:.4f}, {lon:.4f});
        >;
    );
    out body;
    """

    QUERY_EXTENT = """
    [timeout:60];
    (
        way["highway"~"motorway|trunk|primary|secondary|tertiary|unclassified|residential|service|motorway_link|trunk_link|primary_link|secondary_link|motorway_junction|living_street"]({lat_min:.4f}, {lat_max:.4f}, {lon_min:.4f}, {lon_max:.4f});
        >;
    );
    out body;
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

    def _get_surrounding_ways(self, latitude, longitude, radius):
        """
        Get the nearest OSM ways around the specified location within distance.

        Args:
            longitude (float): Longitude
            latitude (float): Latitude
            radius (list[float]|float): Search radius either as float or a list of floats.

        Returns:
            list[overpy.Way]: A list of ways
        """

        if not isinstance(radius, list):
            radius = [radius]

        for r in radius:
            result = self._osm.query(self.QUERY.format(lon=Decimal(longitude).quantize(Decimal('0.0001')),
                                                       lat=Decimal(latitude).quantize(Decimal('0.0001')),
                                                       dist=r))

            if result:
                ways = result.get_ways()

                if ways:
                    return r, ways
            break

        return r, []

    def _get_ways_in_extend(self, lat_min, lat_max, lon_min, lon_max):
        """
        Get the ways within the given extend.
        Args:
            lat_min (float): Latitude
            lat_max (float): Latitude
            lon_min (float): Longitude
            lon_max (float): Longitude

        Returns:

        """
        result = self._osm.query(self.QUERY.format(lat_min=lat_min, lat_max=lat_max, lon_min=lon_min, lon_max=lon_max))

        if result:
            ways = result.get_ways()

            if ways:
                return ways
        else:
            return []

    @property
    def ways(self):
        """The last found ways."""
        return self.last_result

    def _search(self, location, radius, *args, **kwargs):

        if self._last_search_radius is not None:
            search_radius = int(max(self._last_search_radius - radius / 2, radius))
        else:
            search_radius = int(radius)

        return self._get_surrounding_ways(latitude=location.latitude,
                                          longitude=location.longitude,
                                          radius=list(range(search_radius, 10 * search_radius, search_radius)))

    @lru_cache(maxsize=None)
    def way(self, way_id):
        """
        Get the overpy.Way with the given id.

        Args:
            way_id (int): The id of the way.

        Returns:
            overpy.Way: The way with the id.

        Raises:
            UnknownWayException: If the way is unknown.

        """

        request = "way(id: {way_id});(._;>;);out body;".format(way_id=int(way_id))

        try:
            return self._query(request)[0]
        except IndexError:
            raise UnknownWayException('Way with id {} is unknown'.format(int(way_id)))


def init_streetfinder(url=None, **kwargs):
    """
    Initialize a `StreetFinder` with default options.

    Returns:
        StreetFinder:   The initialized streetfinder
    """

    if url is None:
        url = 'https://mux.hs-emden-leer.de/overpass/api/interpreter'

    if 'https' in url:
        ssl.SSLContext.__getnewargs__ = lambda self: (self.protocol,)

        kwargs['context'] = ssl._create_unverified_context()

    return StreetFinder(OSM(url=url, **kwargs))
