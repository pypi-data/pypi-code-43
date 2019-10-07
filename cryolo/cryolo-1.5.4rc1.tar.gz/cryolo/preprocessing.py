#
# COPYRIGHT
# All contributions by Thorsten Wagner:
# Copyright (c) 2017 - 2019, Thorsten Wagner.
# All rights reserved.
#
# ---------------------------------------------------------------------------
#         Do not reproduce or redistribute, in whole or in part.
#      Use of this code is permitted only under licence from Max Planck Society.
#            Contact us at thorsten.wagner@mpi-dortmund.mpg.de
# ---------------------------------------------------------------------------
#

from __future__ import print_function

import difflib
import os

import mrcfile
import numpy as np
from PIL import Image

import cryolo.CoordsIO as CoordsIO


def parse_annotation2(ann_dir, img_dir, grid_dims=None, anchor_size=None):
    if not os.path.exists(ann_dir):
        import sys

        print(
            "Your annotation folder does not exists: ",
            ann_dir,
            " Check your config file!",
        )
        sys.exit()

    if not os.path.exists(img_dir):
        import sys

        print(
            "Your image folder does not exists: ", img_dir, " Check your config file!"
        )
        sys.exit()

    all_imgs = []
    seen_labels = {}
    img_files = []

    # Scan all image filenames
    for root, directories, filenames in os.walk(img_dir, followlinks=True):
        for filename in filenames:
            if filename.endswith(
                ("jpg", "png", "tiff", "tif", "mrc")
            ) and not filename.startswith("."):
                img_files.append(os.path.join(root, filename))

    # Read annotations
    img_names = list(map(os.path.basename, img_files))
    for root, directories, filenames in os.walk(ann_dir, followlinks=True):
        for ann in sorted(filenames):
            if ann.endswith((".box", ".txt", ".star")) and not ann.startswith("."):

                img = {"object": []}
                ann_without_ext = os.path.splitext(os.path.basename(ann))[0]

                cand_list = [i for i in img_names if ann_without_ext in i]
                try:
                    cand_list_no_fileextension = list(map(os.path.basename, cand_list))
                    corresponding_img_path = difflib.get_close_matches(
                        ann_without_ext, cand_list_no_fileextension, n=1, cutoff=0
                    )[0]
                    corresponding_img_path = cand_list[
                        cand_list_no_fileextension.index(corresponding_img_path)
                    ]

                except IndexError:
                    print("Cannot find corresponding image file for ", root, ann)
                    import sys

                    sys.exit()
                index_image = img_names.index(corresponding_img_path)
                img["filename"] = img_files[index_image]
                print(ann, " assigned to ", img["filename"])
                if img["filename"].endswith("mrc"):
                    with mrcfile.mmap(img["filename"], permissive=True) as mrc:
                        img_height = mrc.header.ny
                        img_width = mrc.header.nx

                else:
                    im = Image.open(img["filename"])
                    img_width, img_height = [int(i) for i in im.size]
                boxpath = os.path.join(root, ann)
                img["boxpath"] = boxpath
                img["img_size"] = (img_width, img_height)
                is_helicion_ptcl = is_helicon_with_particle_coords(boxpath)
                is_helicion_eman = is_eman1_helicion(boxpath)
                if is_helicion_ptcl or is_helicion_eman:
                    grid_w = grid_dims[1]
                    num_patches = grid_dims[2]
                    cell_h = img_height / (num_patches * grid_w)

                    if is_helicion_ptcl:
                        filaments = CoordsIO.read_eman1_helicon(boxpath, int(cell_h))
                    else:
                        filaments = CoordsIO.read_eman1_filament_start_end(
                            boxpath, int(cell_h)
                        )

                    for filament in filaments:
                        for box in filament.boxes:
                            obj = {}
                            box_xmin = int(box.x)
                            box_width = int(box.w)
                            box_height = int(box.h)
                            box_ymin = img_height - (int(box.y) + box_height)

                            box_xmax = box_xmin + box_width
                            box_ymax = box_ymin + box_height
                            obj["name"] = "particle"
                            obj["xmin"] = box_xmin
                            obj["ymin"] = box_ymin
                            obj["xmax"] = box_xmax
                            obj["ymax"] = box_ymax
                            img["object"] += [obj]
                            if obj["name"] in seen_labels:
                                seen_labels[obj["name"]] += 1
                            else:
                                seen_labels[obj["name"]] = 1
                elif ann.endswith((".star")):
                    if os.stat(boxpath).st_size != 0:
                        box_lines = np.atleast_2d(
                            np.genfromtxt(boxpath, comments="_", skip_header=4)
                        )
                        for row in box_lines:
                            obj = {}
                            box_xmin = int(row[0] - anchor_size / 2)
                            box_width = int(anchor_size)
                            box_height = int(anchor_size)
                            # box_ymin = img_height - (int(row[1]) + box_height)

                            box_ymin = img_height - int(row[1] + anchor_size / 2)

                            box_xmax = box_xmin + box_width
                            box_ymax = box_ymin + box_height
                            obj["name"] = "particle"
                            obj["xmin"] = box_xmin
                            obj["ymin"] = box_ymin
                            obj["xmax"] = box_xmax
                            obj["ymax"] = box_ymax
                            img["object"] += [obj]
                            if obj["name"] in seen_labels:
                                seen_labels[obj["name"]] += 1
                            else:
                                seen_labels[obj["name"]] = 1
                else:
                    if os.stat(boxpath).st_size != 0:
                        boxes = CoordsIO.read_eman1_boxfile(boxpath)
                        for box in boxes:
                            """
                            Box files are written with coordinate system with an origin in the top left corner. 
                            Each box file is specified by the lower left corner of the box and witdh and the hight of the box.
                            This has to be converted to a coordinate system with origin in the botten left corner.
                            """
                            obj = {}
                            box_xmin = int(box.x)
                            box_width = int(box.w)
                            box_height = int(box.h)
                            box_ymin = img_height - (int(box.y) + box_height)

                            box_xmax = box_xmin + box_width
                            box_ymax = box_ymin + box_height
                            obj["name"] = "particle"
                            obj["xmin"] = box_xmin
                            obj["ymin"] = box_ymin
                            obj["xmax"] = box_xmax
                            obj["ymax"] = box_ymax

                            img["object"] += [obj]
                            if obj["name"] in seen_labels:
                                seen_labels[obj["name"]] += 1
                            else:
                                seen_labels[obj["name"]] = 1

                if len(img["object"]) >= 0:
                    all_imgs += [img]

    return all_imgs, seen_labels


def is_helicon_with_particle_coords(path):
    try:
        with open(path) as f:
            first_line = f.readline()
            f.close()
        return "#micrograph" in first_line
    except ValueError:
        return False


def is_eman1_helicion(path):
    try:
        if os.stat(path).st_size == 0:
            return False
        box_lines = np.atleast_2d(np.genfromtxt(path))
        return (
            len(box_lines) > 1
            and len(box_lines[0]) == 5
            and box_lines[0][4] == -1
            and box_lines[1][4] == -2
        )
    except ValueError:
        return False
