# -*- coding: utf-8 -*-
"""
A Hive plot consists of:

* radialy distributed linear axes
* nodes along those axes
* conections among those nodes

Pyveplot provides the corresponding objects: a *Hiveplot* class
which contains an arbitrary number of *Axis* objects which in
turn contain an arbitrary number of *Node* objects, and a method
to connect them.
"""
import svgwrite
from math import sin, cos, atan2, degrees, radians, sqrt
from collections import OrderedDict

dwg = svgwrite.Drawing()


def cartesian2polar(x, y):
    rho = sqrt(x**2 + y**2)
    phi = degrees(atan2(y, x))
    return(rho, phi)


def polar2cartesian(rho, phi):
    x = rho * cos(radians(phi))
    y = rho * sin(radians(phi))
    return(x, y)


class Hiveplot:
    """
    Base class for a Hive plot.

    """

    def __init__(self, filename):
        self.axes = []

    def connect_axes(self, axis0, axis1, edges, **kwargs):
        """
        if source and target nodes exist in *axis0* and *axis1*
        connect them with the *connect* method.
        """
        for e in edges:
            if (e[0] in axis0.nodes and e[1] in axis1.nodes):
                self.connect(axis0, e[0], axis0.nodes[e[0]].offset,
                             axis1, e[1], axis1.nodes[e[1]].offset,
                             **kwargs)

            if (e[0] in axis1.nodes and e[1] in axis0.nodes):
                self.connect(axis0, e[1], axis0.nodes[e[1]].offset,
                             axis1, e[0], -axis1.nodes[e[0]].offset,
                             **kwargs)

    def connect(self,
                axis0, n0_key, source_distance,
                axis1, n1_key, target_distance,
                **kwargs):
        """Draw edges as Bézier curves.

        Parameters
        ----------
        axis0 : source Axis object
        n0_key : key of source node in nodes dictionary of axis0
        source_distance : distance at which to set control point of bezier
                          curve, at 90 degrees from the axis. Positive values
                          make curves start to the right of the node, negative
                          values make curves start from the left of the node.
        axis1 : target Axis object
        n1_key : key of target node in nodes dictionary of axis1
        target_distance : distance at which to set control point of bezier
                          curve, at 90 degrees from the axis. Positive values
                          make curves start to the right of the node, negative
                          values make curves start from the left of the node.
        kwargs : extra SVG attributes for path element, optional. Set or change
                 attributes using key=value.

        """
        n0 = axis0.nodes[n0_key]
        n1 = axis1.nodes[n1_key]

        pth = svgwrite.path.Path(d="M %s %s" % (n0.x, n0.y),
                                 fill='none', **kwargs)  # source

        # compute source control point
        if source_distance >= 0:
            direction = 1
        else:
            direction = -1
        phi = axis0.angle + (90 * direction)
        (x, y) = polar2cartesian(source_distance, phi)
        x += n0.x
        y += n0.y
        pth.push("C %s %s" % (x, y))  # first control point in path

        # compute target control point
        if target_distance >= 0:
            direction = -1
        else:
            direction = 1
        phi = axis1.angle + (90 * direction)
        (x, y) = polar2cartesian(target_distance, phi)
        x += n1.x
        y += n1.y
        pth.push("%s %s" % (x, y))   # second control point in path

        pth.push("%s %s" % (n1.x, n1.y))  # target
        dwg.add(pth)

    def draw_axes(self):
        """
        Inserts every axis' svg group into the main drawing
        """
        for axis in self.axes:
            dwg.add(axis.getGroup())

    def save(self, filename):
        """
        Draws axes.
        Calculates width and height for viewbox.
        Saves to *filename*.
        """
        self.draw_axes()

        width = max([a.end for a in self.axes]) * 2
        height = width

        dwg.viewbox(-1 * width / 2.0, -1 * height / 2.0, width, height)

        dwg.saveas(filename)


class Axis:

    def __init__(self, start, end='auto', angle=0, **kwargs):
        """Initialize Axis object with start, end positions and optional SVG attributes

        Parameters
        ----------
        start : point closest to the center of the plot
        end : point farthest from the center of the plot
        angle : angle to set the axis, in degrees. 90 degrees points south.
        kwargs : extra SVG attributes for line element, optional
                 Set or change attributes using key=value

        Example
        -------
        >>> axis0 = Axis(start=10,
                         end=100,
                         angle=45,
                         stroke="black",
                         stroke_width=1.5) # pass SVG attributes of axes

        """
        self.start = start
        self.p1 = polar2cartesian(start, angle)

        self.end = end
        if end != 'auto':
            self.p2 = polar2cartesian(end, angle)

        self.center = (0, 0)
        self.angle = angle
        self.nodes = OrderedDict()
        self.attrs = kwargs
        self.g = svgwrite.container.Group()

    def place_node(self, node, offset):
        """Add a Node object to nodes dictionary

        Parameters
        ----------
        node   : a Node object
        offset : float
                 sets the distance from the start point of axis
                 at which the node will be placed

        """
        node.x, node.y = polar2cartesian(self.start + offset, self.angle)
        node.offset = offset + self.start

    def add_node(self, ID, node):
        """
        adds node to axis' node list, computes placement of every node
        in axis
        """
        self.nodes[ID] = node
        self.auto_place_nodes()

    def auto_place_nodes(self):
        """
        Calculates offsets for nodes, then uses *place_node* method
        to update their coordinates.
        """
        offset = 0
        for v in self.nodes:
            node = self.nodes[v]

            offset += node.radius
            self.place_node(node, offset)
            offset += node.radius

        self.end = offset + self.start

    def length(self):
        """
        returns length of axis calculated from node radii
        """
        return sum([self.nodes[v].radius * 2
                    for v in self.nodes])

    def draw(self):
        """
        add sub-element groups to axis svg group
        """
        self.auto_place_nodes()

        # draw axis
        self.g.add(dwg.line(start=polar2cartesian(self.start, self.angle),
                            end=polar2cartesian(self.end, self.angle),
                            **self.attrs))

        # draw nodes
        for node in self.nodes.values():
            self.g.add(node.g)

    def getGroup(self):
        self.draw()
        return self.g


class Node:
    """Base class for Node objects.

    Holds coordinates for node placement and a SVG Group
    object in the *g* attribute.

    """
    def __init__(self, radius, label):
        """
        Parameters
        ----------
         - radius. Will be used by *add_circle* method
         - label
        """
        self.x = 0
        self.y = 0
        self.radius = radius
        self.label = label
        self.g = svgwrite.container.Group()

    def draw(self):
        if self.radius > 0:
            self.add_circle(self.radius)

        if self.label != "":
            self.add_label(self.label)

    def add_circle(self,
                   fill='grey',
                   fill_opacity=0.3,
                   stroke='grey',
                   stroke_width=0.1,
                   **kwargs):
        """
        Adds circle at node's coordinates
        """
        self.g.add(dwg.circle(
            center=(self.x, self.y),
            r=self.radius,
            fill=fill,
            fill_opacity=fill_opacity,
            stroke=stroke,
            stroke_width=stroke_width,
            **kwargs))

    def add_label(self, label,
                  angle=0,
                  scale=0.3,
                  text_anchor="middle", **kwargs):
        """
        adds label at node's coordinates
        """
        self.g.add(
            dwg.text(
                label,
                text_anchor=text_anchor,
                transform="translate(%s, %s) scale(%s) rotate(%s)" % (self.x,
                                                                      self.y,
                                                                      scale,
                                                                      angle)))
