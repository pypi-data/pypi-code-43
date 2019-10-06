from pyrca.properties.beam.node import Node
import math


def calculate_area(nodes: list):
    """
    Calculates area of a section.
    :param nodes: Nodes list. The coordinates of each corner of a section.
    :return: Area of the section.
    """
    _nodes = nodes.copy()

    # Add the first node to the list
    _nodes.append(_nodes[0])

    # Number of nodes
    _n = len(_nodes)

    # Initial value of area
    _area = 0.0

    for i in range(_n - 1):
        j = (i + 1) % _n
        _area += _nodes[i].x * _nodes[j].y
        _area -= _nodes[j].x * _nodes[i].y

    _area = abs(_area) / 2
    return _area


def calculate_centroid_y(nodes: list):
    """
    Calculates centroid of a polygon from the top.
    :param nodes: Nodes list. The coordinates of each corner of a section.
    :return: Distance of centroid from the top.
    """
    _nodes = nodes.copy()

    # Add the first node to the list
    _nodes.append(_nodes[0])

    # Number of nodes
    _n = len(_nodes)

    _area = calculate_area(_nodes)

    _kd = 0

    for i in range(_n - 1):
        _kd += (_nodes[i].y + _nodes[i + 1].y) * \
               (_nodes[i].x * _nodes[i + 1].y - _nodes[i + 1].x * _nodes[i].y)

    _kd = abs(_kd / (6 * _area))
    _kd = abs(get_highest_node(_nodes).y - _kd)

    return _kd


def get_highest_node(nodes: list):
    """
    Get the topmost node from the section.
    :param nodes: Nodes list. The coordinates of each corner of a section.
    :return: Highest node.
    """
    if len(nodes) == 0:
        return None

    _highest_node = nodes[0]

    for _node in nodes:
        if _node.y > _highest_node.y:
            _highest_node = _node

    return _highest_node


def get_lowest_node(nodes: list):
    """
    Get the bottommost node from the section.
    :param nodes: Nodes list. The coordinates of each corner of a section.
    :return: Lowest node.
    """
    if len(nodes) == 0:
        return None

    _lowest_node = nodes[0]

    for _node in nodes:
        if _node.y < _lowest_node.y:
            _lowest_node = _node

    return _lowest_node


def get_nodes_above_axis(axis_elevation: float, nodes: list):
    """
    Get all nodes of section above an axis
    :param axis_elevation: Given axis elevation
    :param nodes: nodes: Nodes list. The coordinates of each corner of a section.
    :return:
    """
    _nodes = nodes.copy()
    _new_nodes = []

    _intersected = 0

    for i in range(1, len(_nodes)):
        y1 = _nodes[i - 1].y
        y3 = _nodes[i].y
        x1 = _nodes[i - 1].x
        x3 = _nodes[i].x

        if y1 == y3:
            if _nodes[i].y >= axis_elevation:
                _new_nodes.append(_nodes[i])
            continue

        x2 = (axis_elevation - y3) / (y1 - y3) * (x1 - x3) + x3

        if _intersected < 2:
            if (y1 <= axis_elevation < y3) or (y1 >= axis_elevation > y3):
                # We got intersection
                _new_nodes.append(Node(x2, axis_elevation))
                _intersected += 1

        if _nodes[i].y >= axis_elevation:
            _new_nodes.append(_nodes[i])

    return _new_nodes


def get_centroid_above_axis(axis_elevation: float, nodes: list):
    """
    Calculates the centroid of section above given axis
    :param axis_elevation: Given axis elevation
    :param nodes: nodes: Nodes list. The coordinates of each corner of a section.
    :return:
    """
    _new_nodes = get_nodes_above_axis(axis_elevation, nodes)

    return calculate_centroid_y(_new_nodes)


def get_area_above_axis(axis_elevation: float, nodes: list):
    """
    Calculates area above an axis.
    :param axis_elevation:
    :param nodes:
    :return:
    """
    _new_nodes = get_nodes_above_axis(axis_elevation, nodes)
    return calculate_area(_new_nodes)


def has_intersected(elevation: float, node1: Node, node2: Node):
    # Check if elevation is out of bounds
    _lower_bound = lower(node1.y, node2.y)
    _higher_bound = greater(node1.y, node2.y)

    return _lower_bound < elevation < _higher_bound


def lower(n1: float, n2: float):
    _lower = n1

    if n2 < _lower:
        _lower = n2

    return _lower


def greater(n1: float, n2: float):
    _greater = n1

    if n2 > _greater:
        _greater = n2

    return _greater


def get_intersection(elevation: float, node1: Node, node2: Node):
    """
    Gets the intersection node of an elevation and 2 nodes
    :param elevation:
    :param node1:
    :param node2:
    :return:
    """
    y1 = node1.y
    y2 = elevation
    y3 = node2.y
    x1 = node1.x
    x3 = node2.x
    x2 = (y2 - y1) / (y3 - y1) * (x3 - x1) + x1

    return Node(x2, y2)


def distance_between_two_nodes(node1: Node, node2: Node):
    """
    Calculates distance between two nodes
    :param node1:
    :param node2:
    :return:
    """
    dist = math.sqrt(math.pow(node1.y - node2.y, 2) + math.pow(node1.x - node2.x, 2))
    return dist


def interpolate(x1: float, x3: float, y1: float, y2: float, y3: float):
    """
    Interpolation function.
    :param x1:
    :param x3:
    :param y1:
    :param y2:
    :param y3:
    :return:
    """
    return (y2 - y3) / (y1 - y3) * (x1 - x3) + x3


def sort_nodes_by_abscissa(nodes: list):
    """
    Using bubble sort to rearrange nodes in a list.
    :param nodes:
    :return:
    """

    # Bubble sort
    _nodes = nodes.copy()
    for i in range(len(_nodes) - 1):
        for j in range(len(_nodes) - 1):
            if _nodes[i].x < _nodes[i+1].x:
                _temp = _nodes[i]
                _nodes[i] = _nodes[i+1]
                _nodes[i+1] = _temp

    return _nodes
