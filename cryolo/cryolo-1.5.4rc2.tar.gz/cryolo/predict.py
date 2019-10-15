"""
Prediction script crYOLO
"""

# ! /usr/bin/env python
#
# COPYRIGHT
#
# All contributions by Ngoc Anh Huyn:
# Copyright (c) 2017, Ngoc Anh Huyn.
# All rights reserved.
#
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
import multiprocessing

import time
import argparse
import os
import sys
import json
import traceback
import numpy as np
from lineenhancer import line_enhancer, maskstackcreator
from . import CoordsIO
from . import imagereader
from . import utils
from . import filament_tracer
from . import config_tools
from . import lowpass
from gooey import Gooey, GooeyParser
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
try:
    os.environ["CUDA_VISIBLE_DEVICES"]
except KeyError:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"


ARGPARSER = None
filament_tracers = []

def create_parser(parser, use_gooey=True):
    """

    :param parser: Parser where the subgroups are added
    :param use_gooey: ture if gooey is used
    :return:
    """

    required_group = parser.add_argument_group(
        "Required arguments", "These options are mandatory to run crYOLO prediction"
    )
    args = ["-c", "--conf"]
    kwargs = {
        "help": "Path to the crYOLO configuration file.",
        "required": True,
        "gooey_options": {
            "validator": {
                "test": 'user_input.endswith("json")',
                "message": "File has to end with .json!",
            },
            "wildcard": "*.json",
        },
    }

    if use_gooey:
        kwargs["widget"] = "FileChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-w", "--weights"]
    kwargs = {
        "help": "Path to the trained model. It can either be a model that you trained from scratch, a refined model or a general model.",
        "required": True,
        "gooey_options": {
            "validator": {
                "test": 'user_input.endswith("h5")',
                "message": "File has to end with .h5!",
            },
            "wildcard": "*.h5",
        },
    }

    if use_gooey:
        kwargs["widget"] = "FileChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-i", "--input"]
    kwargs = {
        "nargs": "+",
        "help": "Path to one or multiple image folders / images (only directories in GUI).",
        "required": True,
    }
    if use_gooey:
        kwargs["widget"] = "DirChooser"
    required_group.add_argument(*args, **kwargs)

    args = ["-o", "--output"]
    kwargs = {
        "help": "Path to the output folder. All particle coordinates will be written there.",
        "required": True,
    }
    if use_gooey:
        kwargs["widget"] = "DirChooser"

    required_group.add_argument(*args, **kwargs)

    optional_group = parser.add_argument_group(
        "Optional arguments", "Optional arguments for crYOLO"
    )

    optional_group.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=0.3,
        help="Confidence threshold. Have to be between 0 and 1. The higher, the more conservative.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "-g",
        "--gpu",
        default="",
        # type=int,
        nargs="+",
        help="Specify which gpu(s) should be used. Multiple GPUs are separated by a whitespace. If not defined otherwise by your system, it will use GPU 0 by default.",
    )

    optional_group.add_argument(
        "-d",
        "--distance",
        default=0,
        type=int,
        help="Particles with a distance less than this value (in pixel) will be removed. This option should not be used in filament mode.",
    )

    optional_group.add_argument(
        "-pbs",
        "--prediction_batch_size",
        default=3,
        type=int,
        help="How many images should be predicted in one batch. Smaller values might resolve memory issues.",
    )

    optional_group.add_argument(
        "--gpu_fraction",
        type=float,
        default=1.0,
        help="Specify the fraction of memory per GPU used by crYOLO during prediction. Only values between 0.0 and 1.0 are allowed.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "-nc",
        "--num_cpu",
        type=int,
        default=-1,
        help="Number of CPUs used during filtering / filament tracing. By default it will use all of the available CPUs.",
    )

    optional_group.add_argument(
        "--norm_margin",
        type=float,
        default=0.0,
        help="Relative margin size for normalization.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0.0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "--monitor",
        action="store_true",
        help='When this option is activated, crYOLO will monitor your input folder. This especially useful for automation purposes. You can stop the monitor mode by writing an empty file with the name "stop.cryolo" in the input directory.',
    )

    optional_group.add_argument(
        "--otf",
        action="store_true",
        default=False,
        help="On the fly filtering. Filtered micrographs will not be written to disk. Might be slower",
    )

    filament_group = parser.add_argument_group(
        "Filament options",
        "These options are only relevant if you want to use  the filament mode",
    )

    filament_group.add_argument(
        "--filament", action="store_true", help="Activate filament mode"
    )

    filament_group.add_argument(
        "--nosplit",
        action="store_true",
        help="The filament mode does not split to curved filaments",
    )

    filament_group.add_argument(
        "--nomerging",
        action="store_true",
        help="The filament mode does not merge filaments",
    )

    filament_group.add_argument(
        "-fw",
        "--filament_width",
        default=None,
        type=int,
        help="Filament width (in pixel)",
    )

    filament_group.add_argument(
        "-mw",
        "--mask_width",
        default=100,
        type=int,
        help="Mask width (in pixel). A Gaussian filter mask is used to estimate the direction of the filaments. This parameter defines how elongated the mask is. The default value typically don't has to be changed.",
    )

    filament_group.add_argument(
        "-bd",
        "--box_distance",
        default=None,
        type=int,
        help="Distance in pixel between two boxes.",
    )

    filament_group.add_argument(
        "-mn",
        "--minimum_number_boxes",
        default=None,
        type=int,
        help="Minimum number of boxes per filament.",
    )

    filament_group.add_argument(
        "-sr",
        "--search_range_factor",
        type=float,
        default=1.41,
        help="The search range for connecting boxes is the box size times this factor.",
    )

    depexp_group = parser.add_argument_group(
        "Deprecated/Experimental/Special ",
        "Contains either deprecated / experimental or very special options.",
    )
    depexp_group.add_argument(
        "-p",
        "--patch",
        type=int,
        help="(DEPRECATED) Number of patches. Use the config file in case you want to use patches.",
    )

    depexp_group.add_argument(
        "--write_empty",
        action="store_true",
        help="Write empty box files when not particle could be found.",
    )


def get_parser():
    parser = GooeyParser(
        description="Pick particles with crYOLO on any dataset",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    create_parser(parser)
    return parser


def _main_():
    import sys

    # if sys.argv[1] == "gui":
    if len(sys.argv) >= 2:
        if not "--ignore-gooey" in sys.argv:
            sys.argv.append("--ignore-gooey")

    # r'^\d+ particles are found in .* \( (\d+) % \)$'
    kwargs = {"terminal_font_family": "monospace", "richtext_controls": True}
    Gooey(
        main,
        program_name="crYOLO Predict",
        image_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../icons"),
        progress_regex=r"^.* \( Progress:\s+(-?\d+) % \)$",
        disable_progress_bar_animation=True,
        tabbed_groups=True,
        **kwargs
    )()


def main(args=None):
    try:
        multiprocessing.set_start_method("fork")
    except RuntimeError:
        pass
    import cryolo.utils as util
    util.check_for_updates()
    print("START METHOD:", multiprocessing.get_start_method())

    if args is None:
        parser = get_parser()
        args = parser.parse_args()

    if isinstance(args.gpu, list):
        if len(args.gpu) == 1:
            num_gpus = 1
            if args.gpu[0] != "-1":
                str_gpus = args.gpu[0].strip().split(" ")
                num_gpus = len(str_gpus)
                os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)
        else:
            str_gpus = [str(entry) for entry in args.gpu]
            num_gpus = len(str_gpus)
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)
    else:
        num_gpus = 1
        if args.gpu != -1 and len(args.gpu) > 0:
            str_gpus = str(args.gpu)
            os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(str_gpus)

    if args.gpu_fraction < 1.0 and args.gpu_fraction > 0.0:
        import tensorflow as tf
        from keras.backend.tensorflow_backend import set_session

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = args.gpu_fraction
        set_session(tf.Session(config=config))
    else:
        import tensorflow as tf
        from keras.backend.tensorflow_backend import set_session

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True

        set_session(tf.Session(config=config))

    config_path = args.conf
    weights_path = args.weights
    input_path = args.input
    for path_index, path in enumerate(input_path):
        input_path[path_index] = os.path.realpath(path)
    obj_threshold = args.threshold
    min_distance = args.distance
    mask_width = args.mask_width
    prediction_batch_size = args.prediction_batch_size
    no_merging = args.nomerging
    otf = args.otf
    do_merging = True
    monitor = args.monitor
    norm_margin = args.norm_margin
    search_range_factor = args.search_range_factor
    if no_merging:
        do_merging = False

    nosplit = False
    if args.nosplit is not None:
        nosplit = args.nosplit

    outdir = None
    if args.output is not None:
        outdir = str(args.output)
    write_empty = args.write_empty

    num_cpus = int(multiprocessing.cpu_count()/2)
    if args.num_cpu != -1:
        num_cpus = args.num_cpu

    with open(config_path) as config_buffer:
        try:
            config = json.load(config_buffer)
        except json.JSONDecodeError:
            print(
                "Your configuration file seems to be corruped. Please check if it is valid."
            )
        if config["model"]["input_size"] % 32 > 0:
            new_input_size = int(32 * round(float(config["model"]["input_size"]) / 32))
            print(
                "You input size is not a multiple of 32. Round it to the next multiple of 32:",
                new_input_size,
            )
            config["model"]["input_size"] = new_input_size

    filament_mode = args.filament
    if filament_mode:
        if args.filament_width is None:
            sys.exit("Please specify your filament width ( -fw / --filament_width)")
        else:
            filament_width = args.filament_width
        if args.box_distance is None:
            sys.exit("Please specify your box distance ( -bd / --box_distance)")
        else:
            box_distance = args.box_distance
        minimum_number_boxes = 1
        if args.minimum_number_boxes is not None:
            minimum_number_boxes = args.minimum_number_boxes

    if args.patch is not None and args.patch > 0:
        num_patches = int(args.patch)
    else:
        num_patches = config_tools.get_number_patches(config)

    # Get overlap patches
    overlap_patches = 0
    if "overlap_patches" in config["model"]:
        overlap_patches = int(config["model"]["overlap_patches"])
    elif not len(config["model"]["anchors"]) > 2:
        overlap_patches = config["model"]["anchors"][0]

    write_direct = True
    if filament_mode:
        write_direct = False
    try:
        picking_results = do_prediction(
            config_path=config_path,
            weights_path=weights_path,
            input_path=input_path,
            obj_threshold=obj_threshold,
            num_patches=num_patches,
            filament_mode=filament_mode,
            write_empty=write_empty,
            overlap=overlap_patches,
            num_images_batch_prediction=prediction_batch_size,
            num_gpus=num_gpus,
            num_cpus=num_cpus,
            otf=otf,
            normalization_margin=norm_margin,
            write_direct=write_direct,
            min_distance=min_distance,
            outdir=outdir,
            monitor=monitor,
        )
    except tf.errors.ResourceExhaustedError:
        print("############################")
        print("Not enough GPU memory. Try to reduce prediction batch size (-pbs). ")
        print("############################")
        sys.exit(0)

    export_size = config_tools.get_box_size(config)[0]
    if write_direct == False:
        del_not_fully_immersed, del_min_distance = picking_postprocessing(
            picking_results, export_size, min_distance
        )

        if min_distance > 0:
            print(
                del_min_distance,
                "particles were filtered because of the distance threshold",
                min_distance,
            )

        print(
            "Deleted",
            del_not_fully_immersed,
            "particles as they were not fully immersed in the micrograph",
        )

    ###############################
    #   Filament Post Processing
    ###############################

    # 1. Build sets of images (size = number of processors)
    # 2. Enhance
    # 3. Filamental post processing

    if filament_mode:
        picking_result_with_boxes = []
        picking_result_no_boxes = []
        picking_result_with_boxes_subsets = []
        picked_filaments = 0
        for picking_result_micrograph in picking_results:
            if picking_result_micrograph["boxes"]:
                picking_result_with_boxes.append(picking_result_micrograph)
            else:
                picking_result_micrograph["filaments"] = []
                picking_result_no_boxes.append(picking_result_micrograph)

        if picking_result_with_boxes:
            image_width, image_height = imagereader.read_width_height(
                picking_result_with_boxes[0]["img_path"]
            )
            rescale_factor = 1024.0 / max(image_width, image_height)
            rescale_factor_x = 1024.0 / image_width
            rescale_factor_y = 1024.0 / image_height

            mask_creator = maskstackcreator.MaskStackCreator(
                filament_width=filament_width * rescale_factor,
                mask_size=1024,
                mask_width=mask_width,
                angle_step=2,
                bright_background=True,
            )
            print("Start filament tracing")
            print("Initialisation mask stack")
            mask_creator.init()
            # Devide picking result into chunks

            number_processors = num_cpus

            picking_result_with_boxes_subsets = [
                picking_result_with_boxes[i : i + number_processors]
                for i in range(0, len(picking_result_with_boxes), number_processors)
            ]
            process_counter = 1

            # Parallel tracing

            filament_width_scaled = filament_width * rescale_factor
            search_radius_scaled = export_size * rescale_factor * search_range_factor
            for picking_result_subset in picking_result_with_boxes_subsets:
                image_subset = [
                    picking_result_subset[i]["img_path"]
                    for i in range(0, len(picking_result_subset))
                ]
                boxes_subset = [
                    picking_result_subset[i]["boxes"]
                    for i in range(0, len(picking_result_subset))
                ]
                print(
                    " Enhance subset ",
                    process_counter,
                    "of",
                    len(picking_result_with_boxes_subsets),
                )
                enhanced_images = line_enhancer.enhance_images(
                    image_subset, mask_creator, num_cpus
                )
                angle_images = [
                    enhanced_images[i]["max_angle"] for i in range(len(enhanced_images))
                ]

                print(
                    " Trace subset ",
                    process_counter,
                    "of",
                    len(picking_result_with_boxes_subsets),
                )
                # global filament_tracers
                global filament_tracers
                filament_tracers = []
                for index, boxset in enumerate(boxes_subset):
                    angle_image_flipped = np.flipud(angle_images[index])
                    filament_tracers.append(
                        filament_tracer.FilamentTracer(
                            boxes=boxset,
                            orientation_image=angle_image_flipped,
                            filament_width=filament_width_scaled,
                            search_radius=search_radius_scaled,
                            angle_delta=10,
                            rescale_factor=rescale_factor,
                            rescale_factor_x=rescale_factor_x,
                            rescale_factor_y=rescale_factor_y,
                            do_merging=do_merging,
                            box_distance=box_distance,
                            nosplit=nosplit,
                        )
                    )
                """
                procs = []
                for tracer in filament_tracers:
                    proc = multiprocessing.Process(target=tracer.trace_filaments)
                    procs.append(proc)
                    proc.start()
                for proc in procs:
                    proc.join()
                """
                #subset_new_filaments = [
                #    tracer.trace_filaments() for tracer in filament_tracers
                #]

                pool = multiprocessing.Pool(processes=num_cpus)

                subset_new_filaments = pool.map(
                   trace_subset_filements, range(len(filament_tracers))
                )
                pool.close()
                pool.join()

                print("Tracing done")
                for index_subset in range(len(picking_result_subset)):
                    new_filaments = subset_new_filaments[index_subset]

                    # Min number of boxes filter:
                    filaments = filament_tracer.filter_filaments_by_num_boxes(
                        new_filaments, minimum_number_boxes
                    )

                    picked_filaments += len(filaments)

                    if len(filaments) >= 1:
                        picking_result_subset[index_subset]["filaments"] = filaments
                    else:
                        picking_result_subset[index_subset]["filaments"] = None

                print("Total number of filaments picked so far: ", picked_filaments)
                process_counter += 1

        if write_empty:
            picking_result_with_boxes_subsets.append(picking_result_no_boxes)

        print("Total number of filaments picked: ", picked_filaments)

        ###############################
        #   Write bounding boxes
        ###############################
        for picking_result_subset in picking_result_with_boxes_subsets:

            for result in picking_result_subset:

                if (result["filaments"] is not None) or write_empty:
                    pth = result["pth"]
                    eman_helix_segmented_path = pth
                    eman_start_end = pth
                    star_start_end = pth[:-3] + "star"

                    if outdir is not None:
                        filename = os.path.basename(pth)
                        eman_helix_segmented_path = os.path.join(
                            outdir, "EMAN_HELIX_SEGMENTED", filename
                        )
                        eman_start_end = os.path.join(
                            outdir, "EMAN_START_END", filename
                        )
                        filename = filename[:-3] + "star"
                        star_start_end = os.path.join(
                            outdir, "STAR_START_END", filename
                        )

                    if not os.path.exists(os.path.dirname(eman_helix_segmented_path)):
                        os.makedirs(os.path.dirname(eman_helix_segmented_path))

                    if not os.path.exists(os.path.dirname(eman_start_end)):
                        os.makedirs(os.path.dirname(eman_start_end))

                    if not os.path.exists(os.path.dirname(star_start_end)):
                        os.makedirs(os.path.dirname(star_start_end))
                    CoordsIO.write_eman1_helicon(
                        filaments=result["filaments"],
                        path=eman_helix_segmented_path,
                        image_filename=os.path.basename(result["img_path"]),
                    )

                    CoordsIO.write_eman1_filament_start_end(
                        filaments=result["filaments"], path=eman_start_end
                    )

                    CoordsIO.write_star_filemant_file(
                        filaments=result["filaments"], path=star_start_end
                    )

    else:
        ###############################
        #   Write bounding boxes
        ###############################
        if write_direct == False:
            prediction_result_to_disk(outdir, picking_results)


def prediction_result_to_disk(outdir, picking_results):
    for box_to_write in picking_results:

        original_path = box_to_write["pth"]
        eman1_path = original_path

        star_path = os.path.splitext(original_path)[0] + ".star"
        cbox_path = os.path.splitext(original_path)[0] + ".cbox"

        if outdir is not None:
            filename = os.path.basename(eman1_path)
            eman1_path = os.path.join(outdir, "EMAN", filename)

        # Create directory if it does not existes
        if not os.path.exists(os.path.dirname(eman1_path)):
            os.makedirs(os.path.dirname(eman1_path))

        CoordsIO.write_eman1_boxfile(path=eman1_path, boxes=box_to_write["boxes"])

        if outdir is not None:
            filename = os.path.basename(star_path)
            star_path = os.path.join(outdir, "STAR", filename)

        # Create directory if it does not existes
        if not os.path.exists(os.path.dirname(star_path)):
            os.makedirs(os.path.dirname(star_path))
        CoordsIO.write_star_file(path=star_path, boxes=box_to_write["boxes"])

        if outdir is not None:
            filename = os.path.basename(cbox_path)
            star_path = os.path.join(outdir, "CBOX", filename)

        # Create directory if it does not existes
        if not os.path.exists(os.path.dirname(star_path)):
            os.makedirs(os.path.dirname(star_path))
        CoordsIO.write_cbox_file(path=star_path, boxes=box_to_write["boxes_unfiltered"])


def min_distance_filter(boxes, min_distance):
    min_distance_sq = min_distance * min_distance

    import itertools

    all_comb = itertools.combinations(boxes, 2)

    distsqs = map(utils.box_squared_distance, all_comb)
    low_distance_pairs = list(itertools.compress(all_comb, distsqs < min_distance_sq))
    for box_a, box_b in low_distance_pairs:
        box_to_delte = box_a
        if box_a.c > box_b.c:
            box_to_delte = box_b
        boxes.remove(box_to_delte)

    return boxes


def rescale(box, image_height, image_width, export_size=None):
    x_ll = int(box.x * image_width - box.w/2 * image_height) # lower left
    y_ll = int(image_height - box.y * image_height - box.h / 2.0 * image_width) # lower right
    boxheight_in_pxl = int(box.h * image_width)
    boxwidth_in_pxl = int(box.w * image_height)
    if export_size is not None:
        delta_boxheight = export_size - boxheight_in_pxl
        delta_boxwidth = export_size - boxwidth_in_pxl
        x_ll = x_ll - delta_boxwidth / 2
        y_ll = y_ll - delta_boxheight / 2
        boxheight_in_pxl = export_size
        boxwidth_in_pxl = export_size
    box.x = x_ll
    box.y = y_ll
    box.w = boxwidth_in_pxl
    box.h = boxheight_in_pxl

    return box


def picking_postprocessing(picking_results, export_size, min_distance):

    # Rescaling
    for picking_result_micrograph in picking_results:
        # if num_patches > 1:
        #    image_width = int(picking_result_micrograph["img_width"]/num_patches)+2*overlap_patches
        #    image_height = int(picking_result_micrograph["img_height"]/num_patches)+2*overlap_patches
        # else:
        image_width = picking_result_micrograph["img_width"]
        image_height = picking_result_micrograph["img_height"]
        picking_result_micrograph["boxes"] = [
            rescale(box, image_height, image_width, export_size)
            for box in picking_result_micrograph["boxes"]
        ]

        picking_result_micrograph["boxes_unfiltered"] = [
            rescale(box, image_height, image_width, export_size)
            for box in picking_result_micrograph["boxes_unfiltered"]
        ]

    # Min distance filter
    del_min_distance = 0
    if min_distance > 0:
        sum_particles_before_filtering = np.sum(
            [len(res["boxes"]) for res in picking_results]
        )
        for picking_result_micrograph in picking_results:
            picking_result_micrograph["boxes"] = min_distance_filter(
                picking_result_micrograph["boxes"], min_distance
            )

        num_remain_particles = np.sum([len(res["boxes"]) for res in picking_results])
        del_min_distance = sum_particles_before_filtering - num_remain_particles

    # Filtering of particles which are not fully immersed in the micrograph
    del_not_fully_immersed = 0
    for picking_result_micrograph in picking_results:
        image_width = picking_result_micrograph["img_width"]
        image_height = picking_result_micrograph["img_height"]

        boxes = picking_result_micrograph["boxes"]
        boxes_to_delete = get_not_fully_immersed_box_indices(
            boxes, image_height, image_width
        )
        for index in sorted(boxes_to_delete, reverse=True):
            del boxes[index]
        del_not_fully_immersed += len(boxes_to_delete)

        boxes = picking_result_micrograph["boxes_unfiltered"]
        boxes_to_delete = get_not_fully_immersed_box_indices(
            boxes, image_height, image_width
        )
        for index in sorted(boxes_to_delete, reverse=True):
            del boxes[index]

    return del_not_fully_immersed, del_min_distance


def do_prediction(
    config_path,
    weights_path,
    input_path,
    num_patches,
    obj_threshold=0.3,
    write_empty=False,
    config_pre=None,
    overlap=0,
    filament_mode=False,
    num_images_batch_prediction=3,
    num_gpus=1,
    num_cpus=-1,
    yolo=None,
    otf=False,
    normalization_margin=0,
    monitor=False,
    **kwargs
):
    """

    :param config_path: Path to the config file
    :param weights_path: Path do weights file (h5)
    :param input_path: Path to the folder containing the input images
    :param num_patches: Number of patches to use
    :param obj_threshold: Threshold for objects
    :param write_empty:
    :param config_pre:
    :param overlap:
    :param filament_mode:
    :param num_images_batch_prediction:
    :param num_gpus:
    :param yolo:
    :param otf: on the fly picking
    :param montior: Monitor input folder
    :param write_direct: direct wiring
    :return:
    """
    for path in input_path:
        path_exists = os.path.exists(path)
        if not path_exists:
            sys.exit("Input path does not exist: " + path)

    img_paths = []
    if isinstance(input_path, list):

        for path in input_path:
            isdir = os.path.isdir(path)
            if isdir:
                dir_files = os.listdir(path)

                dir_files = [
                    i
                    for i in dir_files
                    if not i.startswith(".")
                    and os.path.isfile(os.path.join(path, i))
                    and i.endswith(("tiff", "tif", "mrc", "mrcs", "png", "jpg", "jpeg"))
                ]

                img_paths.extend(
                    [os.path.join(path, image_file) for image_file in dir_files]
                )
            elif os.path.isfile(path):
                if not path.startswith(".") and path.endswith(
                    ("tiff", "tif", "mrc", "png", "mrcs", "jpg", "jpeg")
                ):
                    img_paths.append(path)
    else:
        isdir = os.path.isdir(input_path)
        if isdir:
            img_paths = os.listdir(input_path)

            img_paths = [
                i
                for i in img_paths
                if not i.startswith(".")
                and os.path.isfile(os.path.join(input_path, i))
                and i.endswith(("tiff", "tif", "mrc", "mrcs", "png", "jpg", "jpeg"))
            ]
    import time

    if monitor:
        # Setup the monitor mode
        def add_to_list(event):
            if os.path.basename(event.src_path).lower().startswith("stop.cryolo"):
                nonlocal monitor
                monitor = False
                os.remove(event.src_path)
            else:
                img_paths.append(event.src_path)

        patterns = [
            "*.tiff",
            "*.mrc",
            "*.tif",
            "*.mrcs",
            "*.png",
            "*.png",
            "*.jpeg",
            "*.cryolo",
        ]
        ignore_patterns = None  # ".*" #ignore invisible files
        ignore_directories = True
        case_sensitive = False
        image_dir_handler = PatternMatchingEventHandler(
            patterns, ignore_patterns, ignore_directories, case_sensitive
        )

        image_dir_handler.on_created = add_to_list

        go_recursively = False
        my_observer = Observer()
        print("Monitoring:", input_path[0])
        my_observer.schedule(
            image_dir_handler, os.path.realpath(input_path[0]), recursive=go_recursively
        )
        my_observer.start()

    if not img_paths and monitor == False:
        sys.exit("No valid image in your specified input")

    if len(img_paths) == 0 and monitor == True:
        while len(img_paths) == 0:
            time.sleep(1)
        # When monitoring a directory, wait for the first valid image

    img_paths.sort()
    first_image_path = img_paths[0]
    if config_pre is not None:
        config = config_pre
    else:
        with open(config_path) as config_buffer:
            config = json.load(config_buffer)

    # Read (first) image and check the image depth.

    try:
        img_first = imagereader.image_read(first_image_path)
    except ValueError:
        sys.exit("Image " + first_image_path + " is not valid")
    if img_first is None:
        sys.exit("No valid image: " + first_image_path)

    if len(img_first.shape) == 2:
        depth = 1
    elif img_first.shape[2] == 1:
        depth = 1
    elif np.all(img_first[:, :, 0] == img_first[:, :, 1]) and np.all(
        img_first[:, :, 0] == img_first[:, :, 2]
    ):
        depth = 1
    else:
        depth = 3

    grid_w, grid_h = config_tools.get_gridcell_dimensions(config)

    #############################################
    # Read meta data about the model
    #############################################
    anchors = None
    yolo_kwargs = {}
    import h5py

    with h5py.File(weights_path, mode="r") as f:
        try:
            anchors = list(f["anchors"])
        except KeyError:
            None

    with h5py.File(weights_path, mode="r") as f:
        try:
            num_free_layers = int(list(f["num_free_layers"])[0])
            yolo_kwargs["num_fine_tune_layers"] = num_free_layers
        except KeyError:
            pass

    if anchors is None:
        #
        # TODO: Deprecated, anchors are now saved in the model and always defined.
        #

        if len(config["model"]["anchors"]) > 2:
            # general model is used
            img_width = 4096.0 / num_patches
            img_height = 4096.0 / num_patches
            cell_w = img_width / grid_w
            cell_h = img_height / grid_h
            anchors = np.array(config["model"]["anchors"], dtype=float)
            anchors[::2] = anchors[::2] / cell_w
            anchors[1::2] = anchors[1::2] / cell_h

        else:
            # specifc model is used

            img_width = float(img_first.shape[1]) / num_patches
            img_height = float(img_first.shape[0]) / num_patches
            cell_w = img_width / grid_w
            cell_h = img_height / grid_h

            box_width, box_height = config_tools.get_box_size(config)

            anchor_width = 1.0 * box_width / cell_w
            anchor_height = 1.0 * box_height / cell_h

            anchors = [anchor_width, anchor_height]
        print("Calculated Anchors using first image", anchors)
    else:
        print("Read Anchor from model", anchors)

    if yolo is None:
        ###############################
        #   Make the model
        ###############################
        backend_weights = None
        if "backend_weights" in config["model"]:
            backend_weights = config["model"]["backend_weights"]
        from .frontend import YOLO

        yolo = YOLO(
            architecture=config["model"]["architecture"],
            input_size=config["model"]["input_size"],
            input_depth=depth,
            labels=["particle"],
            max_box_per_image=config["model"]["max_box_per_image"],
            anchors=anchors,
            backend_weights=backend_weights,
            pretrained_weights=weights_path,
            **yolo_kwargs
        )

        ###############################
        #   Load trained weights
        ###############################

        # USE MULTIGPU
        if num_gpus > 1:
            from keras.utils import multi_gpu_model

            parallel_model = multi_gpu_model(yolo.model, gpus=num_gpus)
            yolo.model = parallel_model
    else:
        yolo.anchors = anchors

    ##############################
    # Filter the data
    ##############################

    resize_to = None
    if num_patches == 1:
        # In case only one patch is used (should be default), the resizing can already
        # be done at the filtering step
        resize_to = (config["model"]["input_size"], config["model"]["input_size"])

    if monitor:
        # Monitor mode only works OTF
        otf = True

    if otf and not "filter" in config["model"]:
        print(
            "You specified the --otf option. However, filtering is not configured in your"
            "config line, therefore crYOLO will ignore --otf."
        )
    do_nn_filter = False

    if "filter" in config["model"]:

        filter_options = config["model"]["filter"]
        if len(filter_options) > 2:
            do_nn_filter = True
            model_path, overlap, nn_batch_size, filter_img_path = filter_options
            if not otf:
                print("Filter data using noise2noise model: ", model_path)
                img_paths_filtered = utils.filter_images_noise2noise_dir(
                    img_paths=img_paths,
                    output_dir_filtered_imgs=filter_img_path,
                    model_path=model_path,
                    padding=overlap,
                    batch_size=nn_batch_size,
                    resize_to=resize_to,
                )
            else:
                img_paths_filtered = img_paths
        else:
            # Normal lowpass filter
            cutoff, filter_img_path = filter_options
            if not otf:
                img_paths_filtered = filter_images_lowpass(
                    img_paths=img_paths,
                    output_dir_filtered_imgs=filter_img_path,
                    cutoff=cutoff,
                    num_cpus=num_cpus,
                    resize_to=resize_to,
                )
            else:
                img_paths_filtered = img_paths
    else:
        img_paths_filtered = img_paths

    ###############################
    #   Predict bounding boxes
    ###############################
    print("Reset progress bar: ( Progress: -1 % )")
    total_picked = 0
    boxes_to_write = []
    measured_times = []
    picked_img = 1
    batchsize = num_patches * num_patches * num_images_batch_prediction
    tiles = []
    img_tiles = None
    num_written_tiles = 0
    image_indices = []
    skipped_images = []
    sum_del_not_fully_immersed = 0
    sum_del_min_distance = 0

    do_picking = True
    while do_picking:
        img_pths_copy = img_paths_filtered[:]  # copy
        for current_index_image, img_pth in enumerate(img_pths_copy):

            if os.path.basename(img_pth)[0] != ".":

                start = time.time()

                # Read image file!
                try:

                    if (otf or monitor) and "filter" in config["model"]:
                        if do_nn_filter:
                            print("Filter", img_pth)
                            image = utils.filter_image_noise2noise(
                                img_path=img_pth,
                                model_path=model_path,
                                padding=overlap,
                                batch_size=nn_batch_size,
                            )

                            if resize_to is not None:
                                from PIL import Image

                                image = np.array(
                                    Image.fromarray(image).resize(
                                        resize_to, resample=Image.BILINEAR
                                    )
                                )

                        else:
                            image = filter_images_lowpass(
                                img_paths=[img_pth],
                                output_dir_filtered_imgs=None,
                                cutoff=cutoff,
                                num_cpus=num_cpus,
                                otf=True,
                                resize_to=resize_to,
                            )[0]
                    else:
                        image = imagereader.image_read(img_pth)
                except ValueError:
                    print("Image not valid: ", img_pth, "SKIPPED")
                    skipped_images.append(img_pth)
                    continue

                if image is not None or image.shape[0] == 0 or image.shape[1] == 0:
                    image_indices.append(current_index_image)

                    for patch_x in np.arange(0, num_patches):
                        for patch_y in np.arange(0, num_patches):
                            tile_coordinates = imagereader.get_tile_coordinates(
                                image.shape[1],
                                image.shape[0],
                                num_patches,
                                (patch_x, patch_y),
                                overlap=overlap,
                            )
                            tiles.append(tile_coordinates)
                            img_tmp = image[tile_coordinates[1], tile_coordinates[0]]

                            if img_tiles is None:
                                number_tiles_left = (
                                    (len(img_paths) - current_index_image)
                                    * num_patches
                                    * num_patches
                                )
                                num_tiles = min(batchsize, number_tiles_left)
                                img_tiles = np.empty(
                                    shape=(
                                        num_tiles,
                                        img_tmp.shape[0],
                                        img_tmp.shape[1],
                                    ),
                                    dtype=np.float32,
                                )

                            img_tiles[num_written_tiles, :, :] = img_tmp
                            num_written_tiles = num_written_tiles + 1

                    if num_written_tiles == batchsize or current_index_image == (
                        len(img_paths) - 1
                    ):
                        if filament_mode:
                            nms_thresh = 0.5
                        else:
                            nms_thresh = 0.3
                        boxes_per_image_nms, boxes_per_image_unfiltered = yolo.predict(
                            img_tiles,
                            tiles,
                            image.shape,
                            obj_threshold=obj_threshold,
                            nms_threshold=nms_thresh,
                            num_patches=num_patches,
                            normalize_margin=normalization_margin,
                        )
                        end = time.time()
                        measured_times.append(end - start)
                        for box_img_index, boxes in enumerate(boxes_per_image_nms):
                            boxes_image_path = img_paths[
                                image_indices[box_img_index]
                            ]  # Use original image data instead of filtered
                            imgw, imgh = imagereader.read_width_height(
                                boxes_image_path
                            )  # Use original image size instead of filtered image

                            prnt_progress = [
                                len(boxes),
                                "particles are found in",
                                boxes_image_path,
                            ]
                            if monitor == False:
                                prnt_progress.append(" ( Progress: ")
                                prnt_progress.append(
                                    int(float(picked_img) * 100 / len(img_paths))
                                )
                                prnt_progress.append("% )")

                            print(*prnt_progress)

                            picked_img += 1
                            total_picked = total_picked + len(boxes)

                            if boxes or write_empty:
                                box_pth = os.path.join(
                                    os.path.dirname(boxes_image_path), "box"
                                )
                                file_name_without_extension = os.path.splitext(
                                    os.path.basename(boxes_image_path)
                                )[0]
                                box_pth = os.path.join(
                                    box_pth,
                                    os.path.basename(file_name_without_extension)
                                    + ".box",
                                )

                                box_to_write = {
                                    "pth": box_pth,
                                    "img_width": imgw,
                                    "img_height": imgh,
                                    "img_path": boxes_image_path,
                                    "boxes": boxes,
                                    "boxes_unfiltered": boxes_per_image_unfiltered[
                                        box_img_index
                                    ],
                                }

                                if (
                                    "write_direct" in kwargs
                                    and "min_distance" in kwargs
                                    and "outdir" in kwargs
                                ):
                                    if kwargs["write_direct"] == True:
                                        export_size = config_tools.get_box_size(config)[
                                            0
                                        ]
                                        del_not_fully_immersed, del_min_distance = picking_postprocessing(
                                            picking_results=[box_to_write],
                                            export_size=export_size,
                                            min_distance=kwargs["min_distance"],
                                        )
                                        sum_del_min_distance += del_min_distance
                                        sum_del_not_fully_immersed += (
                                            del_not_fully_immersed
                                        )
                                        prediction_result_to_disk(
                                            kwargs["outdir"], [box_to_write]
                                        )

                                boxes_to_write.append(box_to_write)
                            else:
                                print("no boxes: ", boxes_image_path)

                        # Reset variables
                        tiles = []
                        img_tiles = None
                        num_written_tiles = 0
                        image_indices = []
            else:
                print("Not a valid image:", img_pth)

        for imgp in img_pths_copy:
            img_paths_filtered.remove(imgp)

        if monitor == False:
            do_picking = False
            if "my_observer" in locals():
                print("Stop monitoring")
                my_observer.stop()
                my_observer.join()
        else:
            time.sleep(1)

    if len(skipped_images) > 0:
        print(
            "The following images were skipped because of errors during reading them:"
        )
        for img in skipped_images:
            print(img)
    print(
        total_picked,
        "particles in total are found",
        "(",
        int(np.sum(measured_times)),
        "seconds)",
    )

    if "write_direct" in kwargs and kwargs["write_direct"] == True:
        if sum_del_min_distance > 0:
            print(
                sum_del_min_distance,
                "particles were filtered because of the distance threshold",
                kwargs["min_distance"],
            )

        print(
            "Deleted",
            sum_del_not_fully_immersed,
            "particles as they were not fully immersed in the micrograph",
        )

    return boxes_to_write


def get_not_fully_immersed_box_indices(boxes, image_height, image_width):
    boxes_to_delete = []
    for box_index, box in enumerate(boxes):
        if (
            (box.x + box.w) >= image_width
            or box.x < 0
            or box.y < 0
            or (box.y + box.h) >= image_height
        ):
            boxes_to_delete.append(box_index)
    return boxes_to_delete


def filter_images_lowpass(
    img_paths, output_dir_filtered_imgs, cutoff, num_cpus=-1, otf=False, resize_to=None
):
    """
    Filteres a list of images and return a new list with the paths to the filtered images.

    :param img_paths: Path to images to filter
    :param output_dir_filtered_imgs: Output directory to save the filtered images
    :param cutoff: Absolute cutoff frequency (0-0.5)
    :return: List of paths to the filtered images
    """
    if not otf and not os.path.isdir(output_dir_filtered_imgs):
        os.makedirs(output_dir_filtered_imgs)

    arg_tubles = []
    for img_id, img_pth in enumerate(img_paths):
        if os.path.basename(img_pth)[0] != ".":
            if otf:
                arg_tubles.append((img_pth, cutoff, resize_to))
            else:
                arg_tubles.append(
                    (
                        img_pth,
                        cutoff,
                        output_dir_filtered_imgs,
                        img_id + 1,
                        len(img_paths),
                        resize_to,
                    )
                )

    num_processes = None
    if num_cpus != -1:
        num_processes = num_cpus
    lock = multiprocessing.Lock()
    pool = multiprocessing.Pool(
        initializer=lowpass.init,
        initargs=(lock,),
        maxtasksperchild=1,
        processes=num_processes,
    )

    if otf:
        filtered_images = pool.starmap(
            lowpass.filter_single_image, arg_tubles, chunksize=1
        )
    else:
        filtered_images = pool.starmap(
            lowpass.filter_single_image_and_write_to_disk, arg_tubles, chunksize=1
        )
    pool.close()
    pool.join()

    return filtered_images


def trace_subset_filements(i):
    return filament_tracers[i].trace_filaments()


if __name__ == "__main__":
    _main_()
