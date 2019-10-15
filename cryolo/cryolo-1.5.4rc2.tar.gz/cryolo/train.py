"""
Skript to train crYOLO

Author: Thorsten Wagner
"""
#! /usr/bin/env python

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

from __future__ import print_function

import argparse
import json
import multiprocessing
import os
import time

import numpy as np

import cryolo.config_tools as config_tools
import cryolo.imagereader as imagereader
import cryolo.lowpass as lowpass
from cryolo.preprocessing import parse_annotation2
from . import utils
from gooey import Gooey, GooeyParser


os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
try:
    os.environ["CUDA_VISIBLE_DEVICES"]
except KeyError:
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"


def create_parser(parser):
    """
    Adds argument groups to parser
    :param parser: The parser that is used to add argument groups
    :return: An updated parser
    """
    required_group = parser.add_argument_group(
        "Required arguments", "These options are mandatory to run crYOLO train"
    )

    required_group.add_argument(
        "-c",
        "--conf",
        required=True,
        help="Path to configuration file",
        widget="FileChooser",
        gooey_options={
            "validator": {
                "test": 'user_input.endswith("json")',
                "message": "File has to end with .json!",
            },
            "wildcard": "*.json",
        },
    )

    required_group.add_argument(
        "-w",
        "--warmup",
        type=int,
        required=True,
        default=5,
        help="Number of warmup epochs. Set it to zero if you fine tune a model.",
    )

    optional_group = parser.add_argument_group(
        "Optional arguments", "These options are optional to run crYOLO train"
    )

    optional_group.add_argument(
        "-g",
        "--gpu",
        default="",
        nargs="+",
        help="Specifiy which gpu(s) should be used. Multiple GPUs are separated by a whitespace. If not defined otherwise by your system, it will use GPU 0 by default.",
    )

    optional_group.add_argument(
        "-nc",
        "--num_cpu",
        type=int,
        default=-1,
        help="Number of CPUs used during training. By default it will use half of the available CPUs.",
    )

    optional_group.add_argument(
        "--gpu_fraction",
        type=float,
        default=1.0,
        help="Specify the fraction of memory per GPU used by crYOLO during training. Only values between 0.0 and 1.0 are allowed.",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 1.0",
                "message": "Must be between 0 and 1.0",
            }
        },
    )

    optional_group.add_argument(
        "-e",
        "--early",
        default=10,
        type=int,
        help="Early stop patience. If the validation loss did not improve longer than the early stop patience, "
        "the training is stopped.",
    )

    optional_group.add_argument(
        "--fine_tune",
        action="store_true",
        default=False,
        help="Set it to true if you only want to use the fine tune mode. "
             "When using the fine tune mode, only the last layers of your network are trained and you"
             "have to specify pretrained_weights (see action \"config\"->\"Training options\") "
             "You typically use a general model as pretrained weights."
    )

    optional_group.add_argument(
        "-lft",
        "--layers_fine_tune",
        default=2,
        type=int,
        help="Layers to be trained when using fine tuning.",
    )

    deexsp_group = parser.add_argument_group(
        "Deprecated/Experimental/Special ",
        "Contains either deprecated / experimental or very special options.",
    )

    deexsp_group.add_argument(
        "--seed",
        type=int,
        default=10,
        help="Seed for random number generator. Mainly influences selection of validation images. Should be the same during different training runs!",
    )

    deexsp_group.add_argument(
        "--warm_restarts",
        action="store_true",
        help="Use warm restarts and cosine annealing during training",
    )

    deexsp_group.add_argument(
        "--skip_augmentation",
        action="store_true",
        default=False,
        help="Use it if you want to deactivate data augmentation during training.",
    )


# Reset Keras Session
def reset_keras(gpu_fraction=1):
    """
    This functions resets keras memories after training. It is necessary for training in a
    loop (like warmup and real training). Otherwise the program get memory problems.
    :param gpu_fraction: Fraction of memory that should be allocaded.
    :return: None
    """
    from keras.backend.tensorflow_backend import set_session
    from keras.backend.tensorflow_backend import clear_session
    from keras.backend.tensorflow_backend import get_session
    import gc
    import tensorflow

    sess = get_session()
    clear_session()
    sess.close()
    sess = get_session()

    print(
        gc.collect()
    )  # if it's done something you should see a number being outputted

    # use the same config as you used to create the session
    config = tensorflow.ConfigProto()
    config.gpu_options.allow_growth = True
    config.gpu_options.per_process_gpu_memory_fraction = gpu_fraction
    # config.gpu_options.visible_device_list = "0"
    set_session(tensorflow.Session(config=config))


def get_parser():
    """
    Creates parser
    :return: New parser
    """
    parser = GooeyParser(
        description="Train crYOLO model on any datasett",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    create_parser(parser)
    return parser


def get_model(
    config,
    depth,
    anchors,
    experimental_loss,
    do_fine_tune,
    num_fine_tune_layers,
    num_gpus,
    pretrained_weights,
):
    """
    Create the model for training/prediction

    :param config: Configuration dictonary
    :param depth: Image depth
    :param anchors: Anchors
    :param experimental_loss: True if the experimental loss should be used
    :param do_fine_tune: True if fine tuning should be done
    :param num_fine_tune_layers: Number of layers to fine tune
    :param num_gpus: List of GPU IDs to use
    :param pretrained_weights: Pretrained weights for initialization
    :return: Configuriered model
    """
    ###############################
    #   Construct the model
    ###############################
    backend_weights = None
    if "backend_weights" in config["model"]:
        backend_weights = config["model"]["backend_weights"]
    from cryolo.frontend import YOLO

    # import tensorflow as tf
    # graph = tf.Graph()
    # with graph.as_default():
    if num_gpus > 1:
        import tensorflow as tf

        with tf.device("/cpu:0"):
            yolo = YOLO(
                architecture=config["model"]["architecture"],
                input_size=config["model"]["input_size"],
                input_depth=depth,
                labels=config["model"]["labels"],
                max_box_per_image=config["model"]["max_box_per_image"],
                anchors=anchors,
                backend_weights=backend_weights,
                experimental_loss=experimental_loss,
                pretrained_weights=pretrained_weights,
                fine_tune=do_fine_tune,
                num_fine_tune_layers=num_fine_tune_layers,
            )
    else:
        yolo = YOLO(
            architecture=config["model"]["architecture"],
            input_size=config["model"]["input_size"],
            input_depth=depth,
            labels=config["model"]["labels"],
            max_box_per_image=config["model"]["max_box_per_image"],
            anchors=anchors,
            backend_weights=backend_weights,
            experimental_loss=experimental_loss,
            pretrained_weights=pretrained_weights,
            fine_tune=do_fine_tune,
            num_fine_tune_layers=num_fine_tune_layers,
        )

    # print a summary of the whole model
    yolo.model.summary()

    return yolo


def _main_():
    """
    Fake main function, initilazies gooey
    :return: None
    """
    try:
        multiprocessing.set_start_method("spawn")
    except RuntimeError:
        print("Ignore set start method")

    import sys

    # if sys.argv[1] == "gui":
    if len(sys.argv) >= 2:
        if not "--ignore-gooey" in sys.argv:
            sys.argv.append("--ignore-gooey")

    # r'^\d+ particles are found in .* \( (\d+) % \)$'
    kwargs = {"terminal_font_family": "monospace", "richtext_controls": True}
    Gooey(
        main,
        program_name="crYOLO train",
        image_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../icons"),
        progress_regex=r"^.* \( Progress:\s+(-?\d+) % \)$",
        disable_progress_bar_animation=True,
        tabbed_groups=True,
        **kwargs
    )()


def main(args=None):
    """
    Main function. Read the arguments, start the program :-)
    :return: None
    """
    try:
        multiprocessing.set_start_method("spawn")
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
            str_gpus = args.gpu[0].strip().split(" ")
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

    early_stop = int(args.early)

    warm_restarts = args.warm_restarts

    do_augmentation = not args.skip_augmentation

    do_fine_tune = args.fine_tune
    num_fine_tune_layers = args.layers_fine_tune

    num_cpus = int(multiprocessing.cpu_count()/2)
    if args.num_cpu != -1:
        num_cpus = args.num_cpu
    seed = args.seed
    if args.warmup is not None:
        warmup_epochs = int(args.warmup)
        print("Read warmup by argument")
    else:
        if config["train"]["warmup_epochs"] is not None:
            warmup_epochs = config["train"]["warmup_epochs"]
            print("Read warmup by config")
        else:
            warmup_epochs = 0
            print("Set warmup to zero")

    if args.warmup is not None and do_fine_tune:
        warmup_epochs = 0
        print("Ignore warmup, as fine tuning is activated.")

    if early_stop < warmup_epochs:
        early_stop = warmup_epochs

    experimental_loss = False

    #
    # Read and adapt configuration
    #

    with open(config_path) as config_buffer:
        try:
            config = json.loads(config_buffer.read())
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
    num_patches = config_tools.get_number_patches(config)
    experimental_loss = False

    if early_stop < warmup_epochs:
        early_stop = warmup_epochs

    grid_w, grid_h = config_tools.get_gridcell_dimensions(config)

    ###############################
    #   Parse the annotations
    ###############################

    # parse annotations of the training set
    train_imgs, train_labels = parse_annotation2(
        ann_dir=os.path.realpath(config["train"]["train_annot_folder"]),
        img_dir=os.path.realpath(config["train"]["train_image_folder"]),
        grid_dims=(grid_w, grid_h, num_patches),
        anchor_size=int(config["model"]["anchors"][0]),
    )
    config["model"]["labels"] = ["particle"]

    if len(train_imgs) == 0:
        print("No image files were found.")
        import sys
        sys.exit(0)
    # parse annotations of the validation set, if any, otherwise split the training set
    if os.path.exists(config["valid"]["valid_annot_folder"]):
        valid_imgs, valid_labels = parse_annotation2(
            os.path.realpath(config["valid"]["valid_annot_folder"]),
            os.path.realpath(config["valid"]["valid_image_folder"]),
            (grid_w, grid_h, num_patches),
        )

        if (
            len(valid_imgs) == 0
            or len(valid_labels) == 0
            or len(valid_labels) != len(valid_imgs)
        ):
            if len(valid_imgs) == 0:
                print(
                    "No validation images were found. Invalid validation configuration. Check your config file."
                )
            if len(valid_labels) == 0:
                print(
                    "No validation labels were found. Invalid validation configuration. Check your config file."
                )
    else:
        np.random.seed(seed)
        train_valid_split = int(0.8 * len(train_imgs))
        np.random.shuffle(train_imgs)
        valid_imgs = train_imgs[train_valid_split:]
        train_imgs = train_imgs[:train_valid_split]
        print("Validation set:")
        print([item["filename"] for item in valid_imgs])

    #####################################
    # Write runfile
    #####################################

    valid_imgs_paths = [item["filename"] for item in valid_imgs]
    valid_annot_paths = [item["boxpath"] for item in valid_imgs]
    train_imgs_paths = [item["filename"] for item in train_imgs]
    train_annot_paths = [item["boxpath"] for item in train_imgs]

    runjson = {}
    runjson["run"] = {}
    runjson["run"]["valid_images"] = valid_imgs_paths
    runjson["run"]["valid_annot"] = valid_annot_paths
    runjson["run"]["train_images"] = train_imgs_paths
    runjson["run"]["train_annot"] = train_annot_paths

    if not os.path.exists("runfiles/"):
        os.mkdir("runfiles/")
    timestr = time.strftime("%Y%m%d-%H%M%S")
    with open("runfiles/run_" + timestr + ".json", "w") as outfile:
        json.dump(runjson, outfile, ensure_ascii=False, indent=4)

    ##############################
    # Filter the data
    ##############################

    resize_to = None
    if num_patches == 1:
        # In case only one patch is used (should be default), the resizing can already
        # be done at the filtering step
        resize_to = (config["model"]["input_size"], config["model"]["input_size"])

    if "filter" in config["model"]:
        filter_options = config["model"]["filter"]
        if len(filter_options) > 2:
            model_path, overlap, nn_batch_size, filter_img_path = filter_options
            print("Filter data using noise2noise model: ", model_path)

            # Correct absolute filenames
            train_imgs_paths = [img["filename"] for img in train_imgs]

            filtered_paths = utils.filter_images_noise2noise_dir(
                img_paths=train_imgs_paths,
                output_dir_filtered_imgs=filter_img_path,
                model_path=model_path,
                padding=overlap,
                batch_size=nn_batch_size,
                resize_to=resize_to,
            )

            # Update paths of newly filtered images
            for index, path in enumerate(filtered_paths):
                train_imgs[index]["filename"] = path

            valid_imgs_paths = [img["filename"] for img in valid_imgs]
            filtered_paths = utils.filter_images_noise2noise_dir(
                img_paths=valid_imgs_paths,
                output_dir_filtered_imgs=filter_img_path,
                model_path=model_path,
                padding=overlap,
                batch_size=nn_batch_size,
                resize_to=resize_to,
            )
            # Update paths of newly filtered images
            for index, path in enumerate(filtered_paths):
                valid_imgs[index]["filename"] = path

        else:
            cutoff, filter_img_path = filter_options
            start = time.time()
            lowpass.filter_images(
                images=train_imgs,
                filter_cutoff=cutoff,
                filter_tmp_path=filter_img_path,
                num_cpu=num_cpus,
                resize_to=resize_to,
            )
            lowpass.filter_images(
                images=valid_imgs,
                filter_cutoff=cutoff,
                filter_tmp_path=filter_img_path,
                num_cpu=num_cpus,
                resize_to=resize_to,
            )
            end = time.time()
            print("Time needed for filtering:", end - start)

    overlap_labels = set(config["model"]["labels"]).intersection(
        set(train_labels.keys())
    )

    # Read first image and check the image depth.
    img_first = imagereader.image_read(train_imgs[0]["filename"])
    isgrey = False
    if len(img_first.shape) == 2:
        isgrey = True
    elif np.all(img_first[:, :, 0] == img_first[:, :, 1]) and np.all(
        img_first[:, :, 0] == img_first[:, :, 2]
    ):
        isgrey = True

    if isgrey:
        depth = 1
    else:
        depth = 3

    # As only on box size is expected, the anchor box size automatically

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
        img_width = float(train_imgs[0]["img_size"][0]) / num_patches
        img_height = float(train_imgs[0]["img_size"][1]) / num_patches

        cell_w = img_width / grid_w
        cell_h = img_height / grid_h
        box_width, box_height = config_tools.get_box_size(config)

        anchor_width = 1.0 * box_width / cell_w
        anchor_height = 1.0 * box_height / cell_h
        anchors = [anchor_width, anchor_height]

    if not config["train"]["log_path"]:
        log_path = "~/logs/"
    else:
        log_path = config["train"]["log_path"]
        if not os.path.exists(log_path):
            os.mkdir(log_path)

    # Get overlap patches
    overlap_patches = 0
    if "overlap_patches" in config["model"]:
        overlap_patches = int(config["model"]["overlap_patches"])
    elif not len(config["model"]["anchors"]) > 2:
        overlap_patches = config["model"]["anchors"][0]

    ###############################
    # Start the training process
    ###############################
    pretrained_weights = None
    if os.path.exists(config["train"]["pretrained_weights"]):
        pretrained_weights = config["train"]["pretrained_weights"]

    from keras import backend as K
    import tensorflow as tf

    start = time.time()
    # graph = tf.Graph()
    yolo = get_model(
        config,
        depth,
        anchors,
        experimental_loss,
        do_fine_tune,
        num_fine_tune_layers,
        num_gpus,
        pretrained_weights,
    )

    # USE MULTIGPU
    parallel_model = None
    if num_gpus > 1:
        from keras.utils import multi_gpu_model

        parallel_model = multi_gpu_model(yolo.model, gpus=num_gpus, cpu_merge=False)
    try:
        yolo.train(
            train_imgs=train_imgs,
            valid_imgs=valid_imgs,
            train_times=config["train"]["train_times"],
            valid_times=config["valid"]["valid_times"],
            nb_epoch=config["train"]["nb_epoch"],
            learning_rate=config["train"]["learning_rate"],
            batch_size=config["train"]["batch_size"],
            warmup_epochs=warmup_epochs,
            object_scale=config["train"]["object_scale"],
            no_object_scale=config["train"]["no_object_scale"],
            coord_scale=config["train"]["coord_scale"],
            class_scale=config["train"]["class_scale"],
            saved_weights_name=config["train"]["saved_weights_name"],
            debug=config["train"]["debug"],
            log_path=log_path,
            early_stop_thresh=early_stop,
            num_patches=num_patches,
            warm_restarts=warm_restarts,
            overlap_patches=overlap_patches,
            parallel_model=parallel_model,
            num_cpus=num_cpus,
            do_augmentation=do_augmentation,
        )
    except tf.errors.ResourceExhaustedError:
        print("############################")
        print("Not enough GPU memory. Try to reduce training batch size. ")
        print("############################")
        import sys
        sys.exit(0)

    end = time.time()

    print("Time elapsed for training:", (end - start))



if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    _main_()
