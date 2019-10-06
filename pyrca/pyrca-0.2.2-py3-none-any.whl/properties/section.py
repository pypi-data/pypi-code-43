from ..utils.calculators import *

from .node import Node


class Section:
    main_section = []
    clippings = []
    area = 0
    has_error = False
    error_message = ''

    def __init__(self):
        self.main_section = []
        self.clippings = []

    def set_main_section(self, nodes: list):
        if len(nodes) >= 3:
            self.main_section = nodes
            self.has_error = False
            self.error_message = 'Main section has been set.'
            return True
        else:
            self.has_error = True
            self.error_message = 'Main section nodes must be 3 or more.'
            return False

    def set_clippings(self, clippings: list):
        _clips = []
        for _clipping in clippings:
            if len(_clipping) < 3:
                self.has_error = True
                self.error_message = 'One or more clippings are invalid.'
                return False
            _clips.append(_clipping)

        self.clippings = _clips
        self.has_error = False
        self.error_message = 'Clippings has been set.'
        return True

    def add_clipping(self, clipping: list):
        if len(clipping) < 3:
            self.has_error = True
            self.error_message = 'Clipping must have 3 or more nodes.'
            return False

        self.clippings.append(clipping)
        self.has_error = False
        self.error_message = 'Clipping has been added.'
        return True

    def remove_clipping(self, index: int):
        if len(self.clippings) < (index + 1):
            self.has_error = True
            self.error_message = 'Cannot remove clipping that doesn\'t exist!'
            return False

        self.clippings.pop(index)

    def centroid_above_axis(self, axis_elevation: float):
        ma_clipping_sections = 0
        clipping_section_areas = 0

        main_y = get_centroid_above_axis(axis_elevation, self.main_section)

        main_section_area = get_area_above_axis(axis_elevation, self.main_section)

        ma_main_section = main_y * main_section_area

        for _clipping in self.clippings:
            _area = get_area_above_axis(axis_elevation, _clipping)
            _y = get_centroid_above_axis(axis_elevation, _clipping) + get_highest_node(self.main_section).y - \
                 get_highest_node(_clipping).y
            clipping_section_areas += _area
            ma_clipping_sections += _area * _y

        kd = (ma_main_section - ma_clipping_sections) / (main_section_area - clipping_section_areas)

        return kd

    def get_area_above_axis(self, axis_elevation):
        _main_section_area = get_area_above_axis(axis_elevation, self.main_section)

        _clippings_area = 0

        for _clipping in self.clippings:
            _clippings_area += get_area_above_axis(axis_elevation, _clipping)

        return _main_section_area - _clippings_area

    def get_centroid(self):
        """
        Get the centroid of the section considering hollow portions.
        :return:
        """
        _ma_main = calculate_centroid_y(self.main_section) * calculate_area(self.main_section)

        _highest_point = get_highest_node(self.main_section).y

        _ma_clippings = 0

        for _clipping in self.clippings:
            _highest_clip_point = get_highest_node(_clipping).y
            _ma_clippings += calculate_area(_clipping) * \
                             (calculate_centroid_y(_clipping) + _highest_point - _highest_clip_point)

        _gross_area = self.gross_area_of_concrete()

        kd = (_ma_main - _ma_clippings) / _gross_area

        return kd

    def get_height(self):
        """
        Get the height of the section.
        :return:
        """
        return get_highest_node(self.main_section).y - get_lowest_node(self.main_section).y

    def gross_area_of_concrete(self):
        """
        Calculates the gross area of concrete
        deducting all hollow sections.
        :return:
        """
        _main_area = calculate_area(self.main_section)

        _clippings_area = 0
        for _clipping in self.clippings:
            _clippings_area += calculate_area(_clipping)

        return _main_area - _clippings_area

    def get_effective_width(self, elevation: float):
        """
        Get the effective width of a section at a certain elevation
        deducting all hollow polygons.
        :param elevation:
        :return:
        """
        _width = 0

        _main_section_intersections = []
        _clippings_intersections = []

        # Find intersections in the main section
        for i in range(1, len(self.main_section)):
            if has_intersected(elevation, self.main_section[i-1], self.main_section[i]):
                _intersection = get_intersection(elevation, self.main_section[i-1], self.main_section[i])
                _main_section_intersections.append(_intersection)

        if len(_main_section_intersections) < 2:
            _width = 0
            return _width
        else:
            _width = distance_between_two_nodes(_main_section_intersections[0], _main_section_intersections[1])

        # Find intersections at the clippings
        for _clipping in self.clippings:
            _intersection_per_clip = []
            for i in range(1, len(_clipping)):
                if has_intersected(elevation, _clipping[i-1], _clipping[i]):
                    _intersection = get_intersection(elevation, _clipping[i-1], _clipping[i])
                    _intersection_per_clip.append(_intersection)
            _clippings_intersections.append(_intersection_per_clip)
            _intersection_per_clip.clear()

        # Deduct total width of the holes
        for _clip_intersections in _clippings_intersections:
            _width -= distance_between_two_nodes(_clip_intersections[0], _clip_intersections[1])

        return _width

    def get_neutral_axis_elevation(self):
        """
        Get the elevation of neutral axis.
        :return:
        """
        return get_highest_node(self.main_section).y - self.get_centroid()

    def area_above_axis(self, elevation: float):
        """
        Get the concrete area above an axis
        :param elevation:
        :return:
        """
        _main_section_area = get_area_above_axis(elevation, self.main_section)

        _clippings_areas = 0

        for _clipping in self.clippings:
            _clippings_areas += get_area_above_axis(elevation, _clipping)

        return _main_section_area - _clippings_areas
