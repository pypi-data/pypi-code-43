from gooey import Gooey, GooeyParser
import argparse
import os
import cryolo.config_tools as config_tools
import multiprocessing
import cryolo.__init__ as ini


def config_configuration_parser(parser_config):
    config_required_group = parser_config.add_argument_group(
        "General arguments",
        "These arguments most often have to be changed when creating a config file for crYOLO",
    )

    config_required_group.add_argument(
        "config_out_path",
        default="config_cryolo.json",
        help="Name of configuration file to create.",
        widget="FileSaver",
        gooey_options={
            "validator": {
                "test": 'user_input.endswith("json")',
                "message": "File has to end with .json!",
            },
            "default_file": "config_cryolo.json",
        },
    )
    config_required_group.add_argument(
        "boxsize",
        type=int,
        help="You should specify the same box size here as you used in your training data.  If you train on several datasets with varying box sizes, use something like the average of the used box sizes. In case of the general model fill in your target box size.",
    )

    config_required_group.add_argument(
        "--train_image_folder",
        help="Path to the image folder containing the images to train on. The field can only be left empty when you use a general model.",
        default="",
        widget="DirChooser",
    )
    config_required_group.add_argument(
        "--train_annot_folder",
        help="Path to folder containing the your annotation files like box or star files. The field can only be left empty when you use a general model.",
        default="",
        widget="DirChooser",
    )

    config_required_group.add_argument(
        "--saved_weights_name",
        default="cryolo_model.h5",
        help="Path for saving final weights.",
        widget="FileSaver",
        gooey_options={
            "validator": {
                "test": 'user_input.endswith("h5")',
                "message": "File has to end with .h5!",
            },
            "default_file": "cryolo_model.h5",
        },
    )

    config_model_group = parser_config.add_argument_group(
        "Model options",
        "Options to configure your model. The default options are well tested and typically don't have to be changed.",
    )

    config_model_group.add_argument(
        "-a",
        "--architecture",
        default="PhosaurusNet",
        choices=["PhosaurusNet", "YOLO", "crYOLO"],
        help="Backend network architecture.",
    )
    config_model_group.add_argument(
        "--input_size",
        default=1024,
        type=int,
        help="The images are downsized to this size. This is not the size of your micrographs and only rarely needs to be changed.",
        gooey_options={
            "validator": {
                "test": "float(user_input)%32 < 1",
                "message": "Input size has to be multiple of 32!",
            }
        },
    )

    config_model_group.add_argument(
        "--num_patches",
        type=int,
        default=1,
        help='If specified the patch mode will be used. A value of "2" means, that 2×2 patches will be used. A value of "1" means, that no patches will be used (recommended).',
    )
    config_model_group.add_argument(
        "--overlap_patches",
        type=int,
        default=200,
        help="Only needed when using patch mode. Specifies how much the patches overlap. In our lab, we always keep the default value.",
    )

    config_denoising_group = parser_config.add_argument_group(
        "Denoising options",
        "By default crYOLO denoises your data before training/picking. It will use a low-pass filter, but you can also use neural network denoising (JANNI). Default options are good and typically don't have to be changed.",
    )

    config_denoising_group.add_argument(
        "--filtered_output",
        default="filtered_tmp/",
        help="Output folder for filtered images",
        widget="DirChooser",
    )

    config_denoising_group.add_argument(
        "-f",
        "--filter",
        default="LOWPASS",
        help="Noise filter applied before training/picking. You can choose between a normal low-pass filter"
        " and neural network denoising (JANNI).",
        choices=["NONE", "LOWPASS", "JANNI"],
    )

    config_denoising_group.add_argument(
        "--low_pass_cutoff",
        type=float,
        default=0.1,
        help="Low pass filter cutoff frequency",
        gooey_options={
            "validator": {
                "test": "0.0 <= float(user_input) <= 0.5",
                "message": "Must be between 0 and 0.5",
            }
        },
    )
    config_denoising_group.add_argument(
        "--janni_model",
        help="Path to JANNI model",
        widget="FileChooser",
        gooey_options={"wildcard": "*.h5"},
        default=None,
    )

    config_denoising_group.add_argument(
        "--janni_overlap",
        type=int,
        default=24,
        help="Overlap of patches in pixels (only needed when using JANNI)",
    )

    config_denoising_group.add_argument(
        "--janni_batches",
        type=int,
        default=3,
        help="Number of batches (only needed when using JANNI)",
    )

    config_training_group = parser_config.add_argument_group(
        "Training options",
        "These options influences your training. Default values are robust and typically don't have to be changed.",
    )

    config_training_group.add_argument(
        "--pretrained_weights",
        default="",
        help="Path to h5 file that is used for initialization in case you want to fine tune a previous model.",
        widget="FileChooser",
        gooey_options={
            "validator": {
                "test": 'user_input.endswith("h5")',
                "message": "File has to end with .h5!",
            },
            "wildcard": "*.h5",
        },
    )

    config_training_group.add_argument(
        "--train_times",
        default=10,
        type=int,
        help="How often each image is presented to the network during one epoch. The default should be kept until you have many training images.",
    )

    config_training_group.add_argument(
        "--batch_size",
        type=int,
        default=4,
        help="The number of images crYOLO process in parallel during training.",
    )
    config_training_group.add_argument(
        "--learning_rate",
        type=float,
        default=10 ** -4,
        help="Defines the step size during training. Default should be kept.",
    )
    config_training_group.add_argument(
        "--nb_epoch",
        type=int,
        default=200,
        help="Maximum number of epochs the network will train.",
    )
    config_training_group.add_argument(
        "--object_scale",
        type=float,
        default=5.0,
        help="Penalty scaling factor for missing picking particles.",
    )
    config_training_group.add_argument(
        "--no_object_scale",
        type=float,
        default=1.0,
        help="Penalty scaling factor for picking background.",
    )
    config_training_group.add_argument(
        "--coord_scale",
        type=float,
        default=1.0,
        help="Penalty scaling factor for errors in estimating the correct position.",
    )
    config_training_group.add_argument(
        "--class_scale",
        type=float,
        default=1.0,
        help='Irrelevant, as crYOLO only has the class "particle".',
    )
    config_training_group.add_argument(
        "--log_path", default="logs/", help="Path for log saving", widget="DirChooser"
    )

    config_training_group.add_argument(
        "--debug",
        action="store_true",
        default=True,
        help="If true, the network will provide several statistics during training.",
    )

    config_validation_group = parser_config.add_argument_group(
        "Validation configuration",
        "Validation configuration. If not specified, crYOLO will simply select 20% of the training "
        "data for validation. However it is possible to specify to use specific images "
        "for validation. If you do so, it is important to remove them from your training directories!",
    )
    config_validation_group.add_argument(
        "--valid_image_folder",
        default="",
        help="Path to folder containing the image files.",
        widget="DirChooser",
    )
    config_validation_group.add_argument(
        "--valid_annot_folder",
        default="",
        help="Path to folder containing the validation box files",
        widget="DirChooser",
    )


def create_parser():
    parent_parser = GooeyParser(
        description="The crYOLO particle picking procedure!",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parent_parser.add_subparsers(help="sub-command help")

    # Config generator
    parser_config = subparsers.add_parser(
        "config",
        help="train help",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    config_configuration_parser(parser_config)

    # Training parser
    parser_train = subparsers.add_parser(
        "train",
        help="train help",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    from cryolo.train import create_parser as create_train_parser

    create_train_parser(parser_train)

    # Picking parser
    parser_pick = subparsers.add_parser(
        "predict",
        help="predict help",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    #import cryolo.predict as predict
    from cryolo.predict import create_parser as create_predict_parser

    create_predict_parser(parser_pick)

    # Evaluation parser
    parser_eval = subparsers.add_parser(
        "evaluation",
        help="evalutation help",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    from cryolo.eval import create_parser as create_eval_parser
    #import cryolo.eval as evaluation

    create_eval_parser(parser_eval)

    return parent_parser


PARSER = None


def main():
    import sys


    args = PARSER.parse_args()
    print("#####################################################")
    print(
        "Important debugging information.\nIn case of any problems, please provide this information.")
    print("#####################################################")
    for cmd_arg in sys.argv:
        if cmd_arg.startswith("-"):
            print("")
        print(cmd_arg,end=' ')
    print("")
    print("#####################################################")

    if "config" in sys.argv[1]:
        import cryolo.utils as util
        util.check_for_updates()

        filter = None
        if args.filter == "LOWPASS":
            filter = [args.low_pass_cutoff, args.filtered_output]
        elif args.filter == "JANNI":
            if args.janni_model is None:
                print("Please specify the JANNI model file.")
                sys.exit(1)
            filter = [
                args.janni_model,
                args.janni_overlap,
                args.janni_batches,
                args.filtered_output,
            ]

        config_tools.generate_config_file(
            config_out_path=args.config_out_path,
            architecture=args.architecture,
            input_size=args.input_size,
            anchors=[args.boxsize, args.boxsize],
            max_box_per_image=700,
            num_patches=args.num_patches,
            overlap_patches=args.overlap_patches,
            filter=filter,
            train_image_folder=args.train_image_folder,
            train_annot_folder=args.train_annot_folder,
            train_times=args.train_times,
            pretrained_weights=args.pretrained_weights,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            nb_epoch=args.nb_epoch,
            object_scale=args.object_scale,
            no_object_scale=args.no_object_scale,
            coord_scale=args.coord_scale,
            class_scale=args.class_scale,
            log_path=args.log_path,
            saved_weights_name=args.saved_weights_name,
            debug=args.debug,
            valid_image_folder=args.valid_image_folder,
            valid_annot_folder=args.valid_annot_folder,
            valid_times=1,
        )
    elif "train" in sys.argv[1]:
        import cryolo.train as train

        train.main(args)
    elif "predict" in sys.argv[1]:
        import cryolo.predict as predict

        predict.main(args)
    elif "evaluation" in sys.argv[1]:
        import cryolo.eval as evaluation

        evaluation.main(args)


def _main_():
    global PARSER
    import sys

    PARSER = create_parser()
   # try:
   #     multiprocessing.set_start_method("spawn")
   # except RuntimeError:
   #     print("Ignore set start method")

    kwargs = {"terminal_font_family": "monospace", "richtext_controls": True}

    if len(sys.argv) >= 2:
        if not "--ignore-gooey" in sys.argv:
            sys.argv.append("--ignore-gooey")

    Gooey(
        main,
        program_name="crYOLO " + ini.__version__,
        image_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)), "../icons"),
        progress_regex=r"^.* \( Progress:\s+(-?\d+) % \)$",
        disable_progress_bar_animation=True,
        tabbed_groups=True,
        default_size=(1024, 630),
        **kwargs
    )()


if __name__ == "__main__":
    #try:
    #    multiprocessing.set_start_method("spawn")
    #except RuntimeError:
    #    print("Ignore set start method")
    _main_()
