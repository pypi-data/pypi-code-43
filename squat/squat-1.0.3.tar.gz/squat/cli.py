import sys
from arghandler import ArgumentHandler
from argparse import RawDescriptionHelpFormatter

try:
    from Classifier.classifier_cli import classifier_model_cli
except:
    from squat.Classifier.classifier_cli import classifier_model_cli


def main(args=sys.argv[1:]):  # noqa  pragma: no cover
    """Parse the args, run the commands."""

    handler = ArgumentHandler(
        epilog="description",
        formatter_class=RawDescriptionHelpFormatter,
    )

    handler.set_subcommands({
        'classifier': classifier_model_cli,
        'help': subcmd_help
    })

    handler.run(args, context_fxn={})


def subcmd_help(*args):
    """Import and run help subcommand"""
    print("classifier")


if __name__ == "__main__":
    main()
