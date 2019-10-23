import argparse
import pyconrad
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dev_path', nargs='*',
                        help="Path to CONRAD or CONRADRSL folder (root for classpath)")
    parser.add_argument(
        'class_with_main', help="Java class with main (e.g. edu.stanford.rsl.apps.gui.ReconstructionPipelineFrame)")
    parser.add_argument('args', nargs='*', help="CLI arguments")
    parser.add_argument('--gui', action='store_true',
                        help="Activate this flag for GUI applications")

    args = parser.parse_args()
    if not  args.dev_path:
        args.dev_path = []
    pyconrad.setup_pyconrad(dev_dirs=args.dev_path)

    for dir in args.dev_path:
        sys.path.append(dir)

    if args.gui:
        pyconrad.start_gui()

    runable_class = pyconrad.JClass(args.class_with_main)
    runable_class.main(args.args)


if __name__ == '__main__':
    main()
