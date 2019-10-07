"""
Boxfile writing methods
Author: Thorsten Wagner (thorsten.wagner@mpi-dortmund.mpg.de)
"""
#! /usr/bin/env python
#
# COPYRIGHT
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
import csv
import os
import numpy as np

import cryolo.utils as utils
from cryolo.utils import Filament, BoundBox


def write_box_yolo(path, boxes, write_star=False):
    """
    Write box/star files.
    :param path: Filepath or filename of the box file to write
    :param boxes: Boxes to write
    :param outpath: When path is a filename, it one can specifiy the output path with outpath.
    :param write_star: If true, a star file is written.
    :return: None
    """
    if write_star:
        path = path[:-3] + "star"
        write_star_file(path, boxes)

    else:
        write_eman1_boxfile(path, boxes)


def get_star_file_header(file_name):
    """
        Load the header information.
        Arguments:
        file_name - Path to the file that contains the header.
        Returns:
        List of header names, rows that are occupied by the header.
    """
    start_header = False
    header_names = []
    idx = None

    with open(file_name, "r") as read:
        for idx, line in enumerate(read.readlines()):
            if line.startswith("_"):
                if start_header:
                    header_names.append(line.strip().split()[0])
                else:
                    start_header = True
                    header_names.append(line.strip().split()[0])
            elif start_header:
                break

    if not start_header:
        raise IOError(f"No header information found in {file_name}")

    return header_names, idx


def write_star_file(path, boxes):
    with open(path, "w") as boxfile:
        boxwriter = csv.writer(
            boxfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_NONE
        )
        boxwriter.writerow([])
        boxwriter.writerow(["data_"])
        boxwriter.writerow([])
        boxwriter.writerow(["loop_"])
        boxwriter.writerow(["_rlnCoordinateX #1 "])
        boxwriter.writerow(["_rlnCoordinateY #2"])
        boxwriter.writerow(["_rlnClassNumber #3"])
        boxwriter.writerow(["_rlnAnglePsi #4"])
        boxwriter.writerow(["_rlnAutopickFigureOfMerit  #5"])
        for box in boxes:
            boxwriter.writerow(
                [box.x + box.w / 2, box.y + box.h / 2, -999, -999.00000, -999.00000]
            )


def read_star_file(path, box_width):
    _, skip_indices = get_star_file_header(path)
    boxreader = np.atleast_2d(np.genfromtxt(path, skip_header=skip_indices))
    boxes = []
    for box in boxreader:
        bound_box = BoundBox(
            x=box[0] - box_width / 2, y=box[1] - box_width / 2, w=box_width, h=box_width
        )
        boxes.append(bound_box)
    return boxes


def is_star_filament_file(path):
    if not path.endswith(".star"):
        return False
    _, skip_indices = get_star_file_header(path)
    return skip_indices <= 6


def read_star_filament_file(path, box_width, min_distance=0):
    _, skip_indices = get_star_file_header(path)
    boxreader = np.atleast_2d(np.genfromtxt(path, skip_header=skip_indices))
    filaments = []
    for i, box in enumerate(boxreader):
        if i % 2 == 0:
            x_start = int(box[0] - box_width / 2)
            y_start = int(box[1] - box_width / 2)
            box_start = BoundBox(x=x_start, y=y_start, w=box_width, h=box_width)
        else:
            x_end = int(box[0] - box_width / 2)
            y_end = int(box[1] - box_width / 2)
            box_end = BoundBox(x=x_end, y=y_end, w=box_width, h=box_width)
            length = np.sqrt((x_start - x_end) ** 2 + (y_start - y_end) ** 2)
            if min_distance == 0:
                parts = int((length / (0.1 * box_width)))
            else:
                parts = length / min_distance
            boxes = utils.getEquidistantBoxes(box1=box_start, box2=box_end, num_boxes=parts)
            f = Filament(boxes)
            filaments.append(f)

    return filaments


def write_star_filemant_file(path, filaments):
    with open(path, "w") as starfile:
        starwriter = csv.writer(
            starfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_NONE
        )

        starwriter.writerow(["data_"])
        starwriter.writerow([])
        starwriter.writerow(["loop_"])
        starwriter.writerow(["_rlnCoordinateX #1 "])
        starwriter.writerow(["_rlnCoordinateY #2"])
        starwriter.writerow([])
        # starwriter.writerow(["_rlnClassNumber #3"])
        # starwriter.writerow(["_rlnAnglePsi #4"])
        # starwriter.writerow(["_rlnAutopickFigureOfMerit  #5"])

        for fil in filaments:
            filament_boxes = fil.boxes
            bstart = filament_boxes[0]
            bend = filament_boxes[len(filament_boxes) - 1]
            starwriter.writerow(
                [str(bstart.x + bstart.w / 2) + " " + str(bstart.y + bstart.h / 2)]
            )
            starwriter.writerow(
                [str(bend.x + bend.w / 2) + " " + str(bend.y + bend.h / 2)]
            )


def read_eman1_boxfile(path):
    """
    Read a box file in EMAN1 box format.
    :param path: Path to box file
    :return: List of bounding boxes
    """
    boxreader = np.atleast_2d(np.genfromtxt(path))
    boxes = []
    for box in boxreader:
        bound_box = BoundBox(x=box[0], y=box[1], w=box[2], h=box[3])
        boxes.append(bound_box)
    return boxes


def read_cbox_boxfile(path):
    """
    Read a box file in EMAN1 box format.
    :param path: Path to box file
    :return: List of bounding boxes
    """
    boxreader = np.atleast_2d(np.genfromtxt(path))
    boxes = []
    for box in boxreader:
        bound_box = BoundBox(x=box[0], y=box[1], w=box[2], h=box[3], c=box[4])
        boxes.append(bound_box)
    return boxes


def write_eman1_boxfile(path, boxes):
    with open(path, "w") as boxfile:
        boxwriter = csv.writer(
            boxfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_NONE
        )

        for box in boxes:
            # box.x / box.y = Lower left corner
            boxwriter.writerow([box.x, box.y, box.w, box.h])


def write_cbox_file(path, boxes):
    with open(path, "w") as boxfile:
        boxwriter = csv.writer(
            boxfile, delimiter="\t", quotechar="|", quoting=csv.QUOTE_NONE
        )

        for box in boxes:
            # box.x / box.y = Lower left corner
            boxwriter.writerow([box.x, box.y, box.w, box.h, box.c])


def write_boxfile_manager(path, rectangles):
    """

    :param path: Filepath
    :param rectangles: Rectangles to write
    :return: None
    """
    boxes = []
    for rect in rectangles:
        x_lowerleft = int(rect.get_x())
        y_lowerleft = int(rect.get_y())
        boxize = int(rect.get_width())
        box = BoundBox(x=x_lowerleft, y=y_lowerleft, w=boxize, h=boxize)
        boxes.append(box)
    write_eman1_boxfile(path, boxes)


def write_eman1_filament_start_end(filaments, path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path, "w") as boxfile:
        boxwriter = csv.writer(
            boxfile, delimiter="|", quotechar="|", quoting=csv.QUOTE_NONE
        )
        for fil in filaments:
            fil_boxes = fil.boxes

            boxwriter.writerow(
                [
                    ""
                    + str(fil_boxes[0].x)
                    + " "
                    + str(fil_boxes[0].y)
                    + " "
                    + str(fil_boxes[0].w)
                    + " "
                    + str(fil_boxes[0].h)
                    + " "
                    + str(-1)
                ]
            )

            boxwriter.writerow(
                [
                    ""
                    + str(fil_boxes[len(fil_boxes) - 1].x)
                    + " "
                    + str(fil_boxes[len(fil_boxes) - 1].y)
                    + " "
                    + str(fil_boxes[len(fil_boxes) - 1].w)
                    + " "
                    + str(fil_boxes[len(fil_boxes) - 1].h)
                    + " "
                    + str(-2)
                ]
            )


def is_eman1_filament_start_end(path):
    if not path.endswith(".box"):
        return False
    try:
        box_lines = np.atleast_2d(np.genfromtxt(path))
        if len(box_lines) < 2:
            return False
        return (
            len(box_lines[0]) == 5 and box_lines[0][4] == -1 and box_lines[1][4] == -2
        )
    except ValueError:
        return False


def read_eman1_filament_start_end(path, min_distance=0):
    boxreader = np.atleast_2d(np.genfromtxt(path))
    filaments = []
    for box in boxreader:
        if int(box[4]) == -1:
            x_start = int(box[0])
            y_start = int(box[1])
            box_width = int(box[2])
            box_start = BoundBox(x=x_start, y=y_start, w=box_width, h=box_width)
        if int(box[4]) == -2:
            x_end = int(box[0])
            y_end = int(box[1])
            box_width = int(box[2])
            box_end = BoundBox(x=x_end, y=y_end, w=box_width, h=box_width)
            length = np.sqrt((x_start - x_end) ** 2 + (y_start - y_end) ** 2)
            if min_distance == 0:
                parts = int((length / (0.1 * box_width)))
            else:
                parts = length / min_distance
            boxes = utils.getEquidistantBoxes(box1=box_start, box2=box_end, num_boxes=parts)
            f = Filament(boxes)
            filaments.append(f)

    return filaments


def is_eman1_helicon(path):
    if not (path.endswith(".box") or path.endswith(".txt")):
        return False
    with open(path) as f:
        first_line = f.readline()
        f.close()
    return "#micrograph" in first_line


def read_eman1_helicon(path, min_distance=0):

    if os.stat(path).st_size != 0:
        split_indicis = []
        boxsize = 0
        index_first_helix = -1

        with open(path, "r") as csvfile:
            for index, row in enumerate(csvfile.readlines()):
                if row.startswith("#segment"):
                    boxsize = int(float(row.split()[2]))
                elif row.startswith("#helix"):
                    boxsize = int(float(row[(row.rfind(",") + 1) :]))
                    if index_first_helix == -1:
                        index_first_helix = index
                    else:
                        split_indicis.append(
                            index - index_first_helix - (len(split_indicis) + 1)
                        )

        filaments = []
        coordinates = np.atleast_2d(np.genfromtxt(path))
        coordinates_lowleftcorner = coordinates - boxsize / 2
        coord_filaments = np.split(coordinates_lowleftcorner, split_indicis)
        sqdistance = min_distance * min_distance
        for filament in coord_filaments:
            f = Filament()

            for coords in filament:
                candbox = BoundBox(int(coords[0]), int(coords[1]), boxsize, boxsize)
                if len(f.boxes) > 1:
                    dist = utils.box_squared_distance(
                        f.boxes[len(f.boxes) - 1], candbox
                    )
                    if dist > sqdistance:
                        f.add_box(candbox)
                else:
                    f.add_box(candbox)

            filaments.append(f)
        return filaments
    return None


def write_eman1_helicon(filaments, path, image_filename):

    with open(path, "w") as boxfile:
        boxwriter = csv.writer(
            boxfile, delimiter="|", quotechar="|", quoting=csv.QUOTE_NONE
        )
        # micrograph: actin_cAla_1_corrfull.mrc
        # segment length: 384
        # segment width: 384

        if filaments is not None and len(filaments) > 0:

            boxsize = filaments[0].boxes[0].w

            boxwriter.writerow(["#micrograph: " + image_filename])
            boxwriter.writerow(["#segment length: " + str(int(boxsize))])
            boxwriter.writerow(["#segment width: " + str(int(boxsize))])

            for fil in filaments:
                boxwriter.writerow(
                    [
                        "#helix: ("
                        + str(fil.boxes[0].x + boxsize / 2)
                        + ", "
                        + str(fil.boxes[0].y + boxsize / 2)
                        + "),"
                        + "("
                        + str(fil.boxes[len(fil.boxes) - 1].x + boxsize / 2)
                        + ", "
                        + str(fil.boxes[len(fil.boxes) - 1].y + boxsize / 2)
                        + "),"
                        + str(int(boxsize))
                    ]
                )

                # helix: (3597.3, 2470.9),(3110.9, 3091.7000000000003),38
                for box in fil.boxes:
                    boxwriter.writerow(
                        ["" + str(box.x + boxsize / 2) + " " + str(box.y + boxsize / 2)]
                    )
