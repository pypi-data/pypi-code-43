import os
from arghandler import ArgumentHandler
from .classifier_model import main


def check_path_validity(path):
    try:
        return os.path.exists(path)
    except:
        return False


def classifier_model_cli(parser, context, args):
    """Emit the path to the autocomplete script for use with eval $(snap autocomplete)"""

    handler = ArgumentHandler(usage="Method to train the model",
                              description="Trains the model manually from the cli",
                              epilog="Train the model manually")
    handler.set_subcommands({
        'train': train_model,
    })

    handler.run(args, context_fxn={})


def train_model(parser, context, args):
    """Emit the path to the autocomplete script for use with eval $(snap autocomplete)"""

    handler = ArgumentHandler(usage="Method to train the model",
                              description="Trains the model manually from the cli",
                              epilog="Train the model manually")

    handler.add_argument('-o', '--output', dest='model_path', default='out')

    handler.add_argument('-f', '--file', dest='training_file', default=None)

    out, file = handler.parse_known_args(args)

    if not check_path_validity(out.model_path):
        try:
            os.mkdir(out.model_path)
        except TypeError:
            raise Exception("Please provide a valid path to create the model.")

    if not check_path_validity(out.training_file):
        raise Exception("Training file doesn't exists please provide full path.")

    main(output_dir=out.model_path, training_file=out.training_file)

    # print(out.model_path, out.training_file)

